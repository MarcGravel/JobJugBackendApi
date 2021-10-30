from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import get_auth, pop_user_all
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index, db_fetchall_args, db_fetchone_index_noArgs
import json

@app.route('/api/assignjob', methods=['GET', 'POST', 'DELETE'])
def api_assign_job():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to access this data", mimetype="text/plain", status=401)

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
            
    
    elif request.method == 'POST':
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to assign jobs", mimetype="text/plain", status=401)

        if len(data.keys()) == 3 and {"sessionToken", "userId", "jobId"} <= data.keys():
            #check ids are valid then check if pairs already exist in table. if not, update
            user_id = data.get("userId")
            job_id = data.get("jobId")

            if user_id != None:
                    if str(user_id).isdigit() == False:
                        return Response("Not a valid user id number", mimetype="text/plain", status=400)
            else:
                return Response("No userId sent", mimetype="text/plain", status=400)
            #check exists
            check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM users WHERE id=?)", [user_id])
            if check_id_valid == 0:
                return Response("User id does not exist", mimetype="text/plain", status=400)

            if job_id != None:
                    if str(job_id).isdigit() == False:
                        return Response("Not a valid job id number", mimetype="text/plain", status=400)
            else:
                return Response("No jobId sent", mimetype="text/plain", status=400)
            #check exists
            check_job_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])
            if check_job_id_valid == 0:
                return Response("job id does not exist", mimetype="text/plain", status=400)

            check_matched = db_fetchone_index("SELECT EXISTS(SELECT * FROM assigned_jobs WHERE user_id=? AND job_id=?)", [user_id, job_id])

            if check_matched == 1:
                return Response("This assignment already exists.", mimetype="text/plain", status=400)
            else: 
                db_commit("INSERT INTO assigned_jobs(user_id, job_id) VALUES(?,?)", [user_id, job_id])
                
                resp = {
                    "message": "user is assigned to job"
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

        if len(data.keys()) == 3 and {"sessionToken", "userId", "jobId"} <= data.keys():
            #check ids are valid then check if pairs already exist in table. if not, update
            user_id = data.get("userId")
            job_id = data.get("jobId")

            if user_id != None:
                    if str(user_id).isdigit() == False:
                        return Response("Not a valid user id number", mimetype="text/plain", status=400)
            else:
                return Response("No userId sent", mimetype="text/plain", status=400)
            #check exists
            check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM users WHERE id=?)", [user_id])
            if check_id_valid == 0:
                return Response("User id does not exist", mimetype="text/plain", status=400)

            if job_id != None:
                    if str(job_id).isdigit() == False:
                        return Response("Not a valid job id number", mimetype="text/plain", status=400)
            else:
                return Response("No jobId sent", mimetype="text/plain", status=400)
            #check exists
            check_job_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])
            if check_job_id_valid == 0:
                return Response("job id does not exist", mimetype="text/plain", status=400)

            check_matched = db_fetchone_index("SELECT EXISTS(SELECT * FROM assigned_jobs WHERE user_id=? AND job_id=?)", [user_id, job_id])

            if check_matched == 1:
                db_commit("DELETE FROM assigned_jobs WHERE user_id=? AND job_id=?", [user_id, job_id])
                return Response(status=204)
            else: 
                return Response("This assignment does not exist.", mimetype="text/plain", status=400)

    else:
        print("Something went wrong at assignJob request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)