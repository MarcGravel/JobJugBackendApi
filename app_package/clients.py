from app_package import app
from flask import request, Response
import json
from app_package.functions.dataFunctions import get_auth, pop_client_all, pop_dict_req, check_length, check_email
from app_package.functions.queryFunctions import db_commit, db_fetchall, db_fetchall_args, db_fetchone, db_fetchone_index, db_fetchone_index_noArgs

@app.route('/api/clients', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_clients():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid token and get auth level 
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level == "manager" or auth_level == "admin":
            if len(params.keys()) == 0:
                all_clients = db_fetchall("SELECT * FROM clients")
                all_clients_list = []

                #create return dict and send
                for a in all_clients:
                    client = pop_client_all(a)
                    all_clients_list.append(client)

                return Response (json.dumps(all_clients_list),
                                    mimetype="application/json",
                                    status=200)

            elif len(params.keys()) == 1 and {"clientId"} <=params.keys():
                client_id = params.get("clientId")

                #check valid integer
                if client_id != None:
                    if str(client_id).isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)
                else:
                    return Response("No clientId sent", mimetype="text/plain", status=400)
                
                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])

                if check_id_valid == 1:
                    req_client = db_fetchone("SELECT * FROM clients WHERE id=?", [client_id])
                    all_clients_list = []

                    #create return dict and send
                    client = pop_client_all(req_client)
                    all_clients_list.append(client)

                    return Response(json.dumps(all_clients_list),
                            mimetype="application/json",
                            status=200)
                else:
                    return Response("clientId does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect json data sent", mimetype="text/plain", status=400)

        elif auth_level == "employee":
            #get user id from token
            user_id = db_fetchone_index("SELECT user_id from user_session WHERE session_token=?", [token])

            #get all clients that are associated to jobs that the employee is assigned to.
            if len(params.keys()) == 0:
                all_clients = db_fetchall_args("SELECT c.id, c.name, c.company, c.address, c.email, c.phone FROM clients c INNER JOIN jobs j ON j.client_id = c.id \
                                            INNER JOIN assigned_jobs a ON a.job_id = j.id WHERE a.user_id=?", [user_id])
                all_clients_list = []

                #create obj list
                for a in all_clients:
                    client = pop_client_all(a)
                    all_clients_list.append(client)

                #remove duplicate clients from list
                noDupList = []
                for obj in all_clients_list:
                    if obj not in noDupList:
                        noDupList.append(obj)
                
                return Response (json.dumps(noDupList),
                                mimetype="application/json",
                                status=200)
            
            elif len(params.keys()) == 1 and {"clientId"} <=params.keys():
                client_id = params.get("clientId")

                #check valid integer
                if client_id != None:
                    if str(client_id).isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)
                else:
                    return Response("No clientId sent", mimetype="text/plain", status=400)

                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])

                if check_id_valid == 1:
                    #gets client from clientId if job that is associated with client is assigned to userId
                    req_client = db_fetchone("SELECT c.id, c.name, c.company, c.address, c.email, c.phone FROM clients c INNER JOIN jobs j ON j.client_id = c.id \
                                            INNER JOIN assigned_jobs a ON a.job_id = j.id WHERE a.user_id=? AND c.id=?", [user_id, client_id])
                    
                    #returns error if employee sending client id that does not fit in parameters above

                    if req_client == None:
                        return Response("No access to this client", mimetype="text/plain", status=401)
                    
                    #create return dict and send

                    all_clients_list = []
                    client = pop_client_all(req_client)
                    all_clients_list.append(client)
                    
                    return Response (json.dumps(all_clients_list),
                                mimetype="application/json",
                                status=200)
                else:
                    return Response("clientId does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect json data sent", mimetype="text/plain", status=400)              
        else:
            return Response("Something went wrong. Invalid Authorization level", mimetype="text/plain", status=500)

    elif request.method == 'POST':
        pass
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong at clients request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)
