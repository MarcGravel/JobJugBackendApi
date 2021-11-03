from app_package import app
from flask import request, Response
import json
from app_package.functions.dataFunctions import get_auth, pop_client_all, pop_dict_req, check_length, check_email
from app_package.functions.queryFunctions import db_commit, db_fetchall, db_fetchone, db_fetchone_index, db_fetchone_index_noArgs

@app.route('/api/clients', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_clients():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid token and get auth level 
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

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
                return Response("No userId sent", mimetype="text/plain", status=400)
            
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

    elif request.method == 'POST':
        pass
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong at clients request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)
