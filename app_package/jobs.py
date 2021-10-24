from app_package import app
from flask import request, Response
import json
from app_package.functions.dataFunctions import pop_job_all, pop_job_emp, get_auth
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index, db_fetchall, db_fetchall_args

@app.route('/api/jobs', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_schedule():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)
        
        if auth_level == "manager" or auth_level == "admin":
            #fetching all jobs does not return archived jobs. only active and completed
            if len(params.keys()) == 0:
                all_jobs = db_fetchall_args("SELECT * FROM jobs WHERE job_status=? OR job_status=?", ["active", "completed"])
                all_jobs_list = []

                #create return dict
                for a in all_jobs:
                    job = pop_job_all(a)
                    all_jobs_list.append(job)

                return Response(json.dumps(all_jobs_list, default=str),
                                mimetype="application/json",
                                status=200)

            elif len(params.keys()) == 1 and {"jobStatus"} <= params.keys():
                status = params.get("jobStatus")
                if status == "archived":
                    all_jobs = db_fetchall_args("SELECT * FROM jobs WHERE job_status=?", ["archived"])
                    all_jobs_list = []

                    #create return dict
                    for a in all_jobs:
                        job = pop_job_all(a)
                        all_jobs_list.append(job)

                    return Response(json.dumps(all_jobs_list, default=str),
                            mimetype="application/json",
                            status=200)
                else:
                    return Response("Invalid data. Only 'archived' accepted.", mimetype="text/plain", status=400)

            elif len(params.keys()) == 1 and {"jobId"} <= params.keys():
                job_id = params.get("jobId")
                
                #check valid integer
                if job_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])

                if check_id_valid == 1:
                    req_job = db_fetchone("SELECT * FROM jobs WHERE id=?", [job_id])
                    all_jobs_list = []

                    #create return dict
                    job = pop_job_all(req_job)
                    all_jobs_list.append(job)

                    return Response(json.dumps(all_jobs_list, default=str),
                            mimetype="application/json",
                            status=200)
                else:
                    return Response("Not a valid Id number", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect data sent", mimetype="text/plain", status=400)

        elif auth_level == "employee":
            if len(params.keys()) == 0:
                #get userId
                user_id_tup = db_fetchone("SELECT user_id FROM user_session WHERE session_token=?", [token])

                #fetch jobs only belonging to this employee
                all_jobs = db_fetchall_args("SELECT id, title, location, content, scheduled_date, completed_date, job_status, client_id, notes \
                                            FROM jobs j INNER JOIN assigned_jobs a ON j.id = a.job_id WHERE a.user_id=?", [user_id_tup[0]])
                all_jobs_list = []

                #create return dict
                for a in all_jobs:
                    job = pop_job_emp(a)
                    all_jobs_list.append(job)

                return Response(json.dumps(all_jobs_list, default=str),
                        mimetype="application/json",
                        status=200)
                        
            if len(params.keys()) == 1 and {"jobId"} <= params.keys():
                job_id = params.get("jobId")

                #check valid integer
                if job_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM jobs WHERE id=?)", [job_id])

                if check_id_valid == 1:
                    #get userId
                    user_id_tup = db_fetchone("SELECT user_id FROM user_session WHERE session_token=?", [token])
                    #check job belongs to this employee, if not send error, if so send job
                    emp_has_job = db_fetchone_index("SELECT EXISTS(SELECT * FROM assigned_jobs WHERE user_id=? AND job_id=?)", [user_id_tup[0], job_id])

                    if emp_has_job == 1:
                        req_job = db_fetchone("SELECT id, title, location, content, scheduled_date, completed_date, job_status, client_id, notes \
                                                FROM jobs WHERE id=?", [job_id])
                        all_jobs_list = []

                        #create return dict
                        job = pop_job_emp(req_job)
                        all_jobs_list.append(job)

                        return Response(json.dumps(all_jobs_list, default=str),
                                mimetype="application/json",
                                status=200)
                    else:
                        return Response("Not authorized to view this job", mimetype="text/plain", status=401)
                else: 
                    return Response("Not a valid Id number", mimetype="text/plain", status=400)
            else: 
                    return Response("Unauthorized to view archived jobs", mimetype="text/plain", status=401)
        else: 
            return Response("Invalid Authorization level", mimetype="text/plain", status=401)

    elif request.method == 'POST':
        #only manager or admin can post a job
        data = request.json
        token = data.get("sessionToken")
        
        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)
        print(auth_level)

        return "test"

    elif request.method == 'PATCH':
        pass

    elif request.method == 'DELETE':
        pass

    else:
        return Response("Method not allowed", mimetype="text/plain", status=405)
