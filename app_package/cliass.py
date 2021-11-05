from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import get_auth, pop_client_all
from app_package.functions.queryFunctions import db_commit, db_fetchall, db_fetchone, db_fetchone_index, db_fetchall_args
import json

@app.route('/api/cliass', methods=['GET', 'POST', 'DELETE'])
def api_cliass():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)
        
        if len(params.keys()) == 0:
            if auth_level == "manager" or auth_level == "admin":
                #get all clients assigned to a job
                all_clients = db_fetchall("SELECT c.* FROM jobs_clients j INNER JOIN clients c ON \
                                                j.client_id = c.id")
                all_clients_list = []

                #create return dict and send
                for a in all_clients:
                    client = pop_client_all(a)
                    all_clients_list.append(client)

                return Response (json.dumps(all_clients_list),
                                    mimetype="application/json",
                                    status=200)
            if auth_level == "employee":
                #get user id from token
                user_id = db_fetchone_index("SELECT user_id FROM user_session WHERE session_token=?", [token])

                #get all clients assigned to a job
                all_clients = db_fetchall_args("SELECT c.* FROM jobs_clients j INNER JOIN clients c ON \
                                                j.client_id = c.id INNER JOIN assigned_jobs a ON a.job_id = j.job_id \
                                                    WHERE a.user_id=?", [user_id])
                all_clients_list = []

                #create return dict and send
                for a in all_clients:
                    client = pop_client_all(a)
                    all_clients_list.append(client)

                return Response (json.dumps(all_clients_list),
                                    mimetype="application/json",
                                    status=200)

        #get all clients assigned to job 
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
                if auth_level == "manager" or auth_level == "admin":
                    get_assigned_clients = db_fetchall_args("SELECT client_id FROM jobs_clients WHERE job_id=?", [job_id])
                
                    #get list of client Id
                    client_id_list = [item[0] for item in get_assigned_clients]
                    client_list = []

                    for c in client_id_list:
                        client = db_fetchone("SELECT * FROM clients WHERE id=?", [c])
                        updated_client = pop_client_all(client)
                        client_list.append(updated_client)
                    
                    return Response (json.dumps(client_list),
                                    mimetype="application/json",
                                    status=200)
                if auth_level == "employee":
                    #check user is assigned to job that is trying to get client info from
                    #get user id from token
                    user_id = db_fetchone_index("SELECT user_id FROM user_session WHERE session_token=?", [token])

                    #check exists and then returns values if exists
                    check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT * FROM assigned_jobs WHERE user_id=? AND job_id=?)", [user_id, job_id])

                    if check_id_valid == 1:
                        get_assigned_clients = db_fetchall_args("SELECT client_id FROM jobs_clients WHERE job_id=?", [job_id])
                
                        #get list of client Id
                        client_id_list = [item[0] for item in get_assigned_clients]
                        client_list = []

                        print(client_id_list)

                        for c in client_id_list:
                            client = db_fetchone("SELECT * FROM clients WHERE id=?", [c])
                            updated_client = pop_client_all(client)
                            client_list.append(updated_client)
                        
                        return Response (json.dumps(client_list),
                                        mimetype="application/json",
                                        status=200)
                    else:
                        return Response("Unauthorized access to client information", mimetype="text/plain", status=401)
            else:
                return Response("Not a valid jobId number", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data sent.", mimetype="text/plain", status=400)

    elif request.method == 'POST':
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to assign clients", mimetype="text/plain", status=401)

        if len(data.keys()) == 3 and {"sessionToken", "clientId", "jobId"} <= data.keys():
            #check ids are valid then check if pairs already exist in table. if not, update
            client_id = data.get("clientId")
            job_id = data.get("jobId")

            if client_id != None:
                    if str(client_id).isdigit() == False:
                        return Response("Not a valid client id number", mimetype="text/plain", status=400)
            else:
                return Response("No userId sent", mimetype="text/plain", status=400)
            
            #check exists
            check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])
            if check_id_valid == 0:
                return Response("Client id does not exist", mimetype="text/plain", status=400)

            if job_id != None:
                    if str(job_id).isdigit() == False:
                        return Response("Not a valid job id number", mimetype="text/plain", status=400)
            else:
                return Response("No jobId sent", mimetype="text/plain", status=400)
            #check exists
            check_job_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])
            if check_job_id_valid == 0:
                return Response("job id does not exist", mimetype="text/plain", status=400)

            check_matched = db_fetchone_index("SELECT EXISTS(SELECT * FROM jobs_clients WHERE client_id=? AND job_id=?)", [client_id, job_id])

            if check_matched == 1:
                return Response("This assignment already exists.", mimetype="text/plain", status=400)
            else: 
                db_commit("INSERT INTO jobs_clients(client_id, job_id) VALUES(?,?)", [client_id, job_id])
                
                resp = {
                    "message": "client is assigned to job"
                }

                return Response(json.dumps(resp),
                        mimetype="application/json",
                        status=201)
        else:
            return Response("Invalid json data sent.", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to assign jobs", mimetype="text/plain", status=401)

        if len(data.keys()) == 3 and {"sessionToken", "clientId", "jobId"} <= data.keys():
            #check ids are valid then check if pairs already exist in table. if not, update
            client_id = data.get("clientId")
            job_id = data.get("jobId")

            if client_id != None:
                    if str(client_id).isdigit() == False:
                        return Response("Not a valid user id number", mimetype="text/plain", status=400)
            else:
                return Response("No clientId sent", mimetype="text/plain", status=400)
            #check exists
            check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [client_id])
            if check_id_valid == 0:
                return Response("Client id does not exist", mimetype="text/plain", status=400)

            if job_id != None:
                    if str(job_id).isdigit() == False:
                        return Response("Not a valid job id number", mimetype="text/plain", status=400)
            else:
                return Response("No jobId sent", mimetype="text/plain", status=400)
            #check exists
            check_job_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])
            if check_job_id_valid == 0:
                return Response("job id does not exist", mimetype="text/plain", status=400)

            check_matched = db_fetchone_index("SELECT EXISTS(SELECT * FROM jobs_clients WHERE client_id=? AND job_id=?)", [client_id, job_id])

            if check_matched == 1:
                db_commit("DELETE FROM jobs_clients WHERE client_id=? AND job_id=?", [client_id, job_id])
                return Response(status=204)
            else: 
                return Response("This assignment does not exist.", mimetype="text/plain", status=400)

    else:
        print("Something went wrong at assignClients request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)