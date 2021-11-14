from flask import send_file
from flask.helpers import make_response
from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import get_auth
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index_noArgs, db_fetchone_index
from app_package.functions.borbPdfFunctions import _build_invoice_information, _build_billing_and_shipping_information, _build_content_table, _build_cost_table
import json

#1
from borb.pdf.document import Document 
from borb.pdf.page.page import Page
#2 - imports below for page layout(element coordinates)
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
#3 -add company logo
from borb.pdf.canvas.layout.image.image import Image
#4 -add layout data for alignment and paragraghs, used for company info etc..
from borb.pdf.canvas.layout.text.paragraph import Paragraph
#5 - module to build PDF document
from borb.pdf.pdf import PDF

#temp file
import tempfile

#email package
from flask_mail import Mail
from flask_mail import Message
from dbcreds import mailKey, senderMailAddr, receipMailAddr

@app.route('/api/invoice', methods=['GET', 'POST'])
def api_invoice():

    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)
        
        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to view invoices", mimetype="text/plain", status=401)

        if len(params.keys()) == 1 and {"jobId"} <= params.keys():
            job_id = params.get("jobId")

            #check valid integer
            if job_id != None:
                if str(job_id).isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)
            else:
                return Response("No jobId sent", mimetype="text/plain", status=400)

            #check exists and then returns values if exists
            check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])

            if check_id_valid == 1:
                #check if job has invoice
                invoice_exists = db_fetchone_index("SELECT EXISTS(SELECT id FROM invoices WHERE job_id=?)", [job_id])

                #if not exists, return error
                if invoice_exists == 0:
                    return Response("No invoice for this job", mimetype="text/plain", status=400)

                #get the invoice based on jobId. selects the latest invoice if the job has and error and multiple invoices
                invoice_info = db_fetchone("SELECT MAX(id), job_id, title, content, charged_amount FROM invoices WHERE job_id=?", [job_id])
                
                rounded_float = (str(round(invoice_info[4], 2)))

                invoice = {
                    "id": invoice_info[0],
                    "jobId": invoice_info[1],
                    "title": invoice_info[2],
                    "content": invoice_info[3],
                    "chargedAmount": rounded_float
                }

                #get all client info from job id:
                client_data = db_fetchone("SELECT c.id, c.name, c.company, c.address, c.email, c.phone FROM clients c INNER JOIN jobs j ON j.client_id = c.id WHERE j.id=?", [job_id])

                if client_data == None:
                    return Response("There is no client attached to this job. No available invoice info")

                dictClient = {
                    "id": client_data[0],
                    "name": client_data[1],
                    "company": client_data[2],
                    "address": client_data[3],
                    "email": client_data[4],
                    "phone": client_data[5]
                }

                #removes any none types for simple pdf generation
                client = {}
                for k, v in dictClient.items():
                    if v == '' or v == None:
                        v = " "
                        client[k] = v
                    else:
                        client[k] = v

                #generate pdf with passed data
                pdf = Document()

                #add page
                page = Page()
                pdf.append_page(page)

                #page layout.
                #SingleColumnLayout is used so all content on invoice page is in a single column. like a container
                #vertical margin algo is to make the vertical margin smaller, default is to trim top 10%, this is reduced to 2% to use for header
                page_layout = SingleColumnLayout(page)
                page_layout._vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

                #add company logo
                #Image element added to layout, through the constructor the url and dimensions are set
                page_layout.add(    
                        Image(        
                        "https://s3.stackabuse.com/media/articles/creating-an-invoice-in-python-with-ptext-1.png",        
                        width=Decimal(128),        
                        height=Decimal(128),    
                        ))
                
                #calls build invoice def to populate a table for company info and add to layout
                page_layout.add(_build_invoice_information(invoice["id"]))

                #empty paragraph for spacing after the invoice information function added to page 
                page_layout.add(Paragraph(" "))

                #add billing and shipping info to layout
                page_layout.add(_build_billing_and_shipping_information(client))

                #empty paragraph for spacing 
                page_layout.add(Paragraph(" "))

                #add content table
                page_layout.add(_build_content_table(invoice["title"],invoice["content"]))

                #add cost table
                page_layout.add(_build_cost_table(invoice["chargedAmount"]))
                
                filename = "invoice"+str(invoice["id"])+".pdf"

                #build and send PDF
                tmp = tempfile.TemporaryFile()
                PDF.dumps(tmp, pdf)
                tmp.seek(0)
                resp = make_response(send_file(tmp, as_attachment=True, attachment_filename=filename))
                #must add below to headers to have Content-disposition show on response, which is where filename is stored.
                resp.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return resp

            else:
                return Response("Job id does not exist", mimetype="text/plain", status=400)
        else:
            return Response("Incorrect json data sent", mimetype="text/plain", status=400)
    
    elif request.method == 'POST':

        #configure and initialize the SMTP for email
        app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'apikey'
        app.config['MAIL_PASSWORD'] = mailKey

        mail = Mail(app)
        app.extensions['mail'].debug=0 
        
        #handle POSTrequest:

        #only manager or admin can post an invoice
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to create invoices", mimetype="text/plain", status=401)

        if len(data.keys()) == 5 and {"sessionToken", "jobId", "title", "content", "chargedAmount"} <= data.keys():
            clean_data = {}

            #removes any none types for simple pdf generation
            for k, v in data.items():
                if v == '' or v == None:
                    v = " "
                    clean_data[k] = v
                else:
                    clean_data[k] = v

            #if invoice exists with current job, delete the old invoice before creating new
            invoice_exists = db_fetchone_index("SELECT EXISTS(SELECT id FROM invoices WHERE job_id=?)", [clean_data["jobId"]])

            #if exists, delete before adding new invoice
            if invoice_exists == 1:
                db_commit("DELETE FROM invoices WHERE job_id=?", [clean_data["jobId"]])

            #generate invoice id
            db_commit("INSERT INTO invoices(job_id, title, content, charged_amount) VALUES(?,?,?,?)", \
                        [clean_data["jobId"], clean_data["title"], clean_data["content"], clean_data["chargedAmount"]])

            #get invoice id
            invoice_id = db_fetchone_index_noArgs("SELECT MAX(id) FROM invoices")

            #get all client info from job id:
            client_data = db_fetchone("SELECT c.id, c.name, c.company, c.address, c.email, c.phone FROM clients c INNER JOIN jobs j ON j.client_id = c.id WHERE j.id=?", [clean_data["jobId"]]) 

            if client_data == None:
                return Response("There is no client attached to this job. Cant invoice")

            dictClient = {
                "id": client_data[0],
                "name": client_data[1],
                "company": client_data[2],
                "address": client_data[3],
                "email": client_data[4],
                "phone": client_data[5]
            }

            #removes any none types for simple pdf generation
            client = {}
            for k, v in dictClient.items():
                if v == '' or v == None:
                    v = " "
                    client[k] = v
                else:
                    client[k] = v
            
            #generate pdf with passed data
            pdf = Document()

            #add page
            page = Page()
            pdf.append_page(page)

            #page layout.
            #SingleColumnLayout is used so all content on invoice page is in a single column. like a container
            #vertical margin algo is to make the vertical margin smaller, default is to trim top 10%, this is reduced to 2% to use for header
            page_layout = SingleColumnLayout(page)
            page_layout._vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

            #add company logo
            #Image element added to layout, through the constructor the url and dimensions are set
            page_layout.add(    
                    Image(        
                    "https://s3.stackabuse.com/media/articles/creating-an-invoice-in-python-with-ptext-1.png",        
                    width=Decimal(128),        
                    height=Decimal(128),    
                    ))
            
            #calls build invoice def to populate a table for company info and add to layout
            page_layout.add(_build_invoice_information(invoice_id))

            #empty paragraph for spacing after the invoice information function added to page 
            page_layout.add(Paragraph(" "))

            #add billing and shipping info to layout
            page_layout.add(_build_billing_and_shipping_information(client))

            #empty paragraph for spacing 
            page_layout.add(Paragraph(" "))

            #add content table
            page_layout.add(_build_content_table(clean_data["title"],clean_data["content"]))

            #add cost table
            page_layout.add(_build_cost_table(clean_data["chargedAmount"]))


            ### set up email message
            ### at testing user variable receipMailAddr 
            ### at production -  receip mail address should be client["email"]
            msg= Message("Thank you for choosing TheCompany.",
                sender= senderMailAddr,
                recipients=[client["email"]])

            msg.body = client["name"]+", thank you for working with us. Your invoice is attached."

            #build PDF
            try:
                #temp file create and attach to message
                tmp = tempfile.TemporaryFile()
                PDF.dumps(tmp, pdf)
                tmp.seek(0)
                msg.attach("invoice" + str(invoice_id) + ".pdf", "invoice/pdf", tmp.read())
                tmp.close()
            except:
                print("Cannot build PDF with invoice id "+str(invoice_id))
                return Response("Unable to build PDF", mimetype="text/plain", status=500)

            #send email with pdf attachment
            try:
                with app.app_context():
                    mail.send(msg)
            except:
                print("Error in sending invoice email with invoice id "+str(invoice_id))
                return Response("Unable to send invoice by email", mimetype="text/plain", status=500)

            #get invoice data and return 
            invoice = db_fetchone("SELECT * FROM invoices WHERE id=?", [invoice_id])

            rounded_float = (str(round(invoice[4], 2)))

            resp = {
                "id": invoice[0],
                "jobId": invoice[1],
                "title": invoice[2],
                "content": invoice[3],
                "chargedAmount": rounded_float
            }
            return Response(json.dumps(resp), mimetype="application/json", status=200)          
        else:
            return Response("Invalid json data sent.", mimetype="text/plain", status=400)
    else:
        print("Something went wrong at invoice request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)
