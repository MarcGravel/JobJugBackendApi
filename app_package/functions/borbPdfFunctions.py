#1
from borb.pdf.document import Document 
from borb.pdf.page.page import Page
#2 - imports below for page layout(element coordinates)
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
#3 -add company logo
from borb.pdf.canvas.layout.image.image import Image
#4 -add layout data for alignment and paragraghs, used for company info etc..
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from datetime import datetime
#5 - module to build PDF document
from borb.pdf.pdf import PDF
#6 - adds color to elements as requested
from borb.pdf.canvas.color.color import HexColor, X11Color
#7 - adds table for content of job
#import FixedColumnWidthTable as Table also required here if not imported above
from borb.pdf.canvas.layout.table.table import TableCell

#4:
#function to build layout of company info
#see layout below. this creates a table with 5 rows and 3 columns. Rows correspond with spacing between 
#text elements are added and aligned to right, they also accept styling, for example font is set.
#padding is added to keep text away from the edges of cells.
def _build_invoice_information(invoice_id):
    table_001 = Table(number_of_rows=5, number_of_columns=3)
	
    table_001.add(Paragraph("123 Main Street"))    
    table_001.add(Paragraph("Date", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))    
    now = datetime.now()    
    table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year)))
	
    table_001.add(Paragraph("Vancouver, B.C, V5N 111"))    
    table_001.add(Paragraph("Invoice #", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph("%i" % (invoice_id)))   
	
    table_001.add(Paragraph("604-555-1214"))    
    table_001.add(Paragraph("Due Date", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
    table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year))) 
	
    table_001.add(Paragraph("thecompany@company.com"))    
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.add(Paragraph("www.thecompany.com"))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))    		
    table_001.no_borders()
    
    return table_001

#6 - add billing and shipping info
def _build_billing_and_shipping_information(client):  
    table_001 = Table(number_of_rows=6, number_of_columns=1)  
    table_001.add(  
        Paragraph(  
            "BILL TO",  
            background_color=HexColor("263238"),  
            font_color=X11Color("White"),  
        )  
    )  
    
    table_001.add(Paragraph(client["name"])) 
    table_001.add(Paragraph(client["company"]))  
    table_001.add(Paragraph(client["address"])) 
    table_001.add(Paragraph(client["email"])) 
    table_001.add(Paragraph(client["phone"])) 
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))  
    table_001.no_borders()  
    return table_001

#7 - add content table.
def _build_content_table(content):  
    table_001 = Table(number_of_rows=2, number_of_columns=1)    
    
    table_001.add(TableCell(Paragraph("Job Scope", font_color=X11Color("White")), background_color=HexColor("1167b1")))  

    color = HexColor("BBBBBB")    
    table_001.add(TableCell(Paragraph(content), background_color=color))  

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))  
    table_001.no_borders()  
    return table_001

def _build_cost_table(charged):
    chargedFloat = float(charged)
    subtotal = str(round(chargedFloat, 2))
    algo_tax = float(subtotal) / 100 * 5
    tax = str(round(algo_tax, 2))
    algo_billed_total = float(subtotal) + float(tax)
    billed_total = str(round(algo_billed_total, 2))  

    table_001 = Table(number_of_rows=3, number_of_columns=4)

    table_001.add(TableCell(Paragraph("Subtotal", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT,), col_span=3,))  
    table_001.add(TableCell(Paragraph(subtotal, horizontal_alignment=Alignment.RIGHT)))  
    table_001.add(TableCell(Paragraph("Taxes", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT), col_span=3,))  
    table_001.add(TableCell(Paragraph(tax, horizontal_alignment=Alignment.RIGHT)))  
    table_001.add(TableCell(Paragraph("Total", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT  ), col_span=3,))  
    table_001.add(TableCell(Paragraph(billed_total, horizontal_alignment=Alignment.RIGHT)))  
    
    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))  
    table_001.no_borders()
    return table_001