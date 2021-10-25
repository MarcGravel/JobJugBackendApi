from app_package import app
from flask import request, Response
import json
from app_package.functions.dataFunctions import pop_job_all, pop_job_emp, get_auth, pop_dict_req, check_length
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index, db_fetchall_args, db_fetchone_index_noArgs

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
                user_id= db_fetchone_index("SELECT user_id FROM user_session WHERE session_token=?", [token])

                #fetch jobs only belonging to this employee
                all_jobs = db_fetchall_args("SELECT id, title, location, content, scheduled_date, completed_date, job_status, client_id, notes \
                                            FROM jobs j INNER JOIN assigned_jobs a ON j.id = a.job_id WHERE a.user_id=?", [user_id])
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
                    user_id = db_fetchone_index("SELECT user_id FROM user_session WHERE session_token=?", [token])
                    #check job belongs to this employee, if not send error, if so send job
                    emp_has_job = db_fetchone_index("SELECT EXISTS(SELECT * FROM assigned_jobs WHERE user_id=? AND job_id=?)", [user_id, job_id])

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

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to create jobs", mimetype="text/plain", status=401)

        if len(data.keys()) >= 3 and len(data.keys()) <= 12:
            new_job = pop_dict_req(data)
        else:
            return Response("Invalid amount of data sent", mimetype="text/plain", status=400)

        #go through both REQUIRED column and check if exists, then validate data
        #once all required data validated then create job. all nullable columns will be checked after and updated into table if exists
        if "title" in new_job:
            if not check_length(new_job["title"], 1, 100):
                return Response("Title must be between 1 and 100 characters", mimetype="text/plain", status=400)
        else:
            return Response("Title is required on a job", mimetype="text/plain", status=400)

        if "jobStatus" in new_job:
            if new_job["jobStatus"] != "active" \
                and new_job["jobStatus"] != "completed" \
                and new_job["jobStatus"] != "archived":
                    
                return Response("Invalid job status. active, completed, or archived only", mimetype="text/plain", status=400)
        else:
            return Response("jobStatus is required on a job, (active, completed, archived)", mimetype="text/plain", status=400) 

        #create job
        db_commit("INSERT INTO jobs(title, job_status) VALUES(?,?)", [new_job["title"], new_job["jobStatus"]])

        #get job id of newly insterted job to add data below
        job_id = db_fetchone_index_noArgs("SELECT MAX(id) FROM jobs")

        #if data exists for other columns, validate then update each. if validations fail, delete job for re post request.
        if "location" in new_job: 
            if not check_length(new_job["location"], 1, 100):
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("location must be between 1 and 100 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE jobs SET location=? WHERE id=?", [new_job["location"], job_id])

        if "content" in new_job:
            if not check_length(new_job["content"], 1, 15000):
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("content must be between 1 and 15,000 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE jobs SET content=? WHERE id=?", [new_job["content"], job_id])

        if "scheduledDate" in new_job:
            if not check_length(new_job["scheduledDate"], 1, 50):
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("scheduledDate must be a date", mimetype="text/plain", status=400)
            db_commit("UPDATE jobs SET scheduled_date=? WHERE id=?", [new_job["scheduledDate"], job_id])

        if "completedDate" in new_job:
            if not check_length(new_job["completedDate"], 1, 50):
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("completedDate must be a date", mimetype="text/plain", status=400)
            db_commit("UPDATE jobs SET completed_date=? WHERE id=?", [new_job["completedDate"], job_id])

        if "cost" in new_job:
            try:
                cost_float = float(new_job["cost"])
                db_commit("UPDATE jobs SET cost=? WHERE id=?", [cost_float, job_id])
            except ValueError:
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("cost must be a number", mimetype="text/plain", status=400)

        if "charged" in new_job:
            try:
                charged_float = float(new_job["charged"])
                db_commit("UPDATE jobs SET charged=? WHERE id=?", [charged_float, job_id])
            except ValueError:
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("charged must be a number", mimetype="text/plain", status=400)
        
        if "invoiced" in new_job:
            if new_job["invoiced"] == "0" or new_job["invoiced"] == "1":
                toInt = int(new_job["invoiced"])
                db_commit("UPDATE jobs SET invoiced=? WHERE id=?", [toInt, job_id])
            else:
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("Invoiced is a boolean expecting 0 or 1", mimetype="text/plain", status=400)

        if "clientId" in new_job:
            client_exists = db_fetchone_index("SELECT EXISTS(SELECT id FROM clients WHERE id=?)", [new_job["clientId"]])

            if client_exists == 1:
                client_id = int(new_job["clientId"])
                db_commit("UPDATE jobs SET client_id=? WHERE id=?", [client_id, job_id])
            else:
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("Client Id does not exist", mimetype="text/plain", status=400)

        if "notes" in new_job:
            if not check_length(new_job["notes"], 1, 3000):
                db_commit("DELETE FROM jobs WHERE id=?", [job_id])
                return Response("notes must be between 1 and 3,000 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE jobs SET notes=? WHERE id=?", [new_job["notes"], job_id])

        #get new job fromdb and send back in a valid dict
        req_new_job = db_fetchone("SELECT * FROM jobs WHERE id=?", [job_id])
        job_to_list = []

        job = pop_job_all(req_new_job)
        job_to_list.append(job)

        return Response(json.dumps(job_to_list, default=str),
                mimetype="application/json",
                status=201)

    elif request.method == 'PATCH':
        pass

    elif request.method == 'DELETE':
        pass

    else:
        return Response("Method not allowed", mimetype="text/plain", status=405)
