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
        # only managers/admin can post a new client.
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" or auth_level != "admin":
            return Response("Not authorized to create a new client", mimetype="text/plain", status=401)

        if len(data.keys()) >= 2 and len(data.keys()) <= 6:
            new_client = pop_dict_req(data)
        else:
            return Response("Invalid amount of data sent", mimetype="text/plain", status=400)

        #validate REQUIRED field then insert new client. Then check non required fields if values exist

        if "name" in new_client:
            if not check_length(new_client["name"], 1, 60):
                return Response("Name must be between 1 and 60 characters", mimetype="text/plain", status=400)
        else:
            return Response("Name is required to create new client", mimetype="text/plain", status=400)

        #create client
        db_commit("INSERT INTO clients(name) VALUES(?)", [new_client["name"]])

        #get client id of newly insterted client to add optional data below
        created_client_id = db_fetchone_index_noArgs("SELECT MAX(id) FROM clients")

        #if data exists for other columns, validate then update row
        if "company" in new_client:
            if not check_length(new_client["company"], 0, 100):
                db_commit("DELETE FROM clients WHERE id=?", [created_client_id])
                return Response("Max 100 characters for company", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET company=? WHERE id=?", [new_client["company"], created_client_id])

        if "address" in new_client:
            if not check_length(new_client["address"], 0, 100):
                db_commit("DELETE FROM clients WHERE id=?", [created_client_id])
                return Response("Max 100 characters for address", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET address=? WHERE id=?", [new_client["address"], created_client_id])

        if "email" in new_client:
            if not check_email(new_client["email"]):
                db_commit("DELETE FROM clients WHERE id=?", [created_client_id])
                return Response("Invalid email address", mimetype="text/plain", status=400)
            if not check_length(new_client["email"], 0, 50):
                db_commit("DELETE FROM clients WHERE id=?", [created_client_id])
                return Response("email length max 50 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET email=? WHERE id=?", [new_client["email"], created_client_id])

        if "phone" in new_client:
            if not check_length(new_client["phone"], 0, 20):
                db_commit("DELETE FROM clients WHERE id=?", [created_client_id])
                return Response("Phone number must be between 7 and 20 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET phone=? WHERE id=?", [new_client["phone"], created_client_id])

        #get new client from db and send back in a valid dict
        req_new_client = db_fetchone("SELECT * FROM clients WHERE id=?", [created_client_id])

        #create return dict and send as list
        client_to_list = []
        client = pop_client_all(req_new_client)
        client_to_list.append(client)
        
        return Response (json.dumps(client_to_list),
                    mimetype="application/json",
                    status=201)

    elif request.method == 'PATCH':
        #only managers/admin can update client info.
        data = request.json
        token = data.get("sessionToken")
        client_id = data.get("clientId")

        #check id exists
        if client_id != None:
            id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])
            if id_valid == 0:
                return Response("clientId does not exist", mimetype="text/plain", status=400)
        else:
            return Response("No clientId sent", mimetype="text/plain", status=400)

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to update client", mimetype="text/plain", status=401)

        if len(data.keys()) >= 3 and len(data.keys()) <= 7:
            upd_client = pop_dict_req(data)
        else:
            return Response("Invalid amount of data sent", mimetype="text/plain", status=400)

        if "name" in upd_client:
            if not check_length(upd_client["name"], 1, 60):
                return Response("Name must be between 1 and 60 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET name=? WHERE id=?", [upd_client["name"], client_id])

        if "company" in upd_client:
            if not check_length(upd_client["company"], 0, 100):
                db_commit("DELETE FROM clients WHERE id=?", [client_id])
                return Response("Max 100 characters for company", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET company=? WHERE id=?", [upd_client["company"], client_id])

        if "address" in upd_client:
            if not check_length(upd_client["address"], 0, 100):
                db_commit("DELETE FROM clients WHERE id=?", [client_id])
                return Response("Max 100 characters for address", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET address=? WHERE id=?", [upd_client["address"], client_id])

        if "email" in upd_client:
            if not check_email(upd_client["email"]):
                db_commit("DELETE FROM clients WHERE id=?", [client_id])
                return Response("Invalid email address", mimetype="text/plain", status=400)
            if not check_length(upd_client["email"], 0, 50):
                db_commit("DELETE FROM clients WHERE id=?", [client_id])
                return Response("email length max 50 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET email=? WHERE id=?", [upd_client["email"], client_id])

        if "phone" in upd_client:
            if not check_length(upd_client["phone"], 0, 20):
                db_commit("DELETE FROM clients WHERE id=?", [client_id])
                return Response("Phone number must be between 7 and 20 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE clients SET phone=? WHERE id=?", [upd_client["phone"], client_id])

        #get updated client from db and send back in a valid dict
        req_upd_client = db_fetchone("SELECT * FROM clients WHERE id=?", [client_id])

        #create return dict and send as list
        client_to_list = []
        client = pop_client_all(req_upd_client)
        client_to_list.append(client)
        
        return Response (json.dumps(client_to_list),
                    mimetype="application/json",
                    status=201)

    elif request.method == 'DELETE':
        #managers and admin can delete clients
        data = request.json
        token = data.get("sessionToken")
        client_id = data.get("clientId")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Unauthorized to delete clients", mimetype="text/plain", status=401)

        #check valid integer
        if client_id != None:
            if str(client_id).isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)
        else:
            return Response("No clientId sent", mimetype="text/plain", status=400)

        #check id exists
        id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])
        if id_valid == 0:
            return Response("clientId does not exist", mimetype="text/plain", status=400)

        db_commit("DELETE FROM clients WHERE id=?", [client_id])
        return Response(status=204)
        
    else:
        print("Something went wrong at clients request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)
