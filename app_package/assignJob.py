from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import get_auth, pop_user_all
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index, db_fetchall_args, db_fetchone_index_noArgs
import json

@app.route('/api/assignjob', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_assign_job():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level == "manager" or auth_level == "admin":
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
                    get_assigned_emps = db_fetchall_args("SELECT user_id FROM assigned_jobs WHERE job_id=?", [job_id])
                    #get list of user Id
                    user_id_list = [item[0] for item in get_assigned_emps]

                    #loop through list and get users for each user id
                    # then populate employee list and return 
                    user_list = []

                    for u in user_id_list:
                        user = db_fetchone("SELECT id, auth_level, name, email, phone, hourly_rate FROM users WHERE id=?", [u])
                        updated_user = pop_user_all(user)
                        user_list.append(updated_user)
                    
                    return Response (json.dumps(user_list),
                                mimetype="application/json",
                                status=200)

                else:
                    return Response("Not a valid jobId number", mimetype="text/plain", status=400)
            else:
                return Response("Invalid json data sent.", mimetype="text/plain", status=400)
        else:
            return Response("Not authorized to access this data", mimetype="text/plain", status=401)
    
    elif request.method == 'POST':
        pass

    elif request.method == 'PATCH':
        pass

    elif request.method == 'DELETE':
        pass

    else:
        print("Something went wrong at assignJob request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)