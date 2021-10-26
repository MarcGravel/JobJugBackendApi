from app_package import app
from flask import request, Response
import json
from app_package.functions.dataFunctions import get_auth, pop_user_all, pop_user_emp, pop_dict_req, check_length, check_email
from app_package.functions.queryFunctions import db_commit, db_fetchall, db_fetchone, db_fetchone_index, db_fetchone_index_noArgs

@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_users():
    if request.method == 'GET':
        params = request.args
        token = request.headers.get("sessionToken")

        #check valid token and get auth level 
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level == "manager" or auth_level == "admin":
            if len(params.keys()) == 0:
                all_users = db_fetchall("SELECT id, auth_level, name, email, phone, hourly_rate FROM users")
                all_users_list = []

                #create return dict and send
                for a in all_users:
                    user = pop_user_all(a)
                    all_users_list.append(user)
                
                return Response (json.dumps(all_users_list),
                                mimetype="application/json",
                                status=200)
            
            elif len(params.keys()) == 1 and {"userId"} <= params.keys():
                user_id = params.get("userId")

                #check valid integer
                if user_id != None:
                    if user_id.isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)
                else:
                    return Response("No userId sent", mimetype="text/plain", status=400)

                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM users WHERE id=?)", [user_id])

                if check_id_valid == 1:
                    req_user = db_fetchone("SELECT id, auth_level, name, email, phone, hourly_rate FROM users WHERE id=?", [user_id])
                    all_users_list = []

                    #create return dict (always return gets as list)
                    user = pop_user_all(req_user)
                    all_users_list.append(user)

                    return Response(json.dumps(all_users_list, default=str),
                            mimetype="application/json",
                            status=200)
                else:
                    return Response("userId does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect json data sent", mimetype="text/plain", status=400)

        #Only difference between auth levels is employees do not get hourly rate returned.
        #different query along with different pop_user return dict
        elif auth_level == "employee":
            if len(params.keys()) == 0:
                all_users = db_fetchall("SELECT id, auth_level, name, email, phone FROM users")
                all_users_list = []

                #create return dict and send
                for a in all_users:
                    user = pop_user_emp(a)
                    all_users_list.append(user)
                
                return Response (json.dumps(all_users_list),
                                mimetype="application/json",
                                status=200)
            if len(params.keys()) == 1 and {"userId"} <= params.keys():
                user_id = params.get("userId")

                #check valid integer
                if user_id != None:
                    if user_id.isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)
                else:
                    return Response("No userId sent", mimetype="text/plain", status=400)

                #check exists and then returns values if exists
                check_id_valid = db_fetchone_index("SELECT EXISTS(SELECT id FROM users WHERE id=?)", [user_id])

                if check_id_valid == 1:
                    #check if user_id belongs to current user, if so, return dict including hourly rate
                    #if not, do not include hourly rate in return.
                    cur_user_id = db_fetchone_index("SELECT user_id FROM user_session WHERE session_token=?", [token])
                    if int(cur_user_id) == int(user_id):
                        req_user = db_fetchone("SELECT id, auth_level, name, email, phone, hourly_rate FROM users WHERE id=?", [user_id])
                        all_users_list = []

                        #create return dict (always return gets as list)
                        user = pop_user_all(req_user)
                        all_users_list.append(user)

                        return Response(json.dumps(all_users_list, default=str),
                                mimetype="application/json",
                                status=200)
                    else:
                        req_user = db_fetchone("SELECT id, auth_level, name, email, phone FROM users WHERE id=?", [user_id])
                        all_users_list = []

                        #create return dict (always return gets as list)
                        user = pop_user_emp(req_user)
                        all_users_list.append(user)

                        return Response(json.dumps(all_users_list, default=str),
                                mimetype="application/json",
                                status=200)
                else:
                    return Response("userId does not exist", mimetype="text/plain", status=400)
        else:
            return Response("Something went wrong. Invalid Authorization level", mimetype="text/plain", status=500)

    elif request.method == 'POST':
        # only managers/admin can post a new user. Only admins can create new admins
        data = request.json
        token = data.get("sessionToken")

        #check valid session token and gets auth level
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if auth_level != "manager" and auth_level != "admin":
            return Response("Not authorized to create a new user", mimetype="text/plain", status=401)

        if len(data.keys()) >= 5 and len(data.keys()) <= 7:
            new_user = pop_dict_req(data)
        else:
            return Response("Invalid amount of data sent", mimetype="text/plain", status=400)
        
        #validate all REQUIRED feilds then insert now user. Then check non required feilds if values exist

        if "authLevel" in new_user:
            #checks auth level value is valid
            if new_user["authLevel"] != "admin" and new_user["authLevel"] != "manager" and new_user["authLevel"] != "employee":
                return Response("Invalid authLevel. admin, manager, or employee only", mimetype="text/plain", status=400)
            
            #checks current user is admin if trying to create admin
            if new_user["authLevel"] == "admin" and auth_level != "admin":
                return Response("Not authorized to create this user type", mimetype="text/plain", status=401)
        else:
            return Response("authLevel is required to create new user", mimetype="text/plain", status=400)

        if "name" in new_user:
            if not check_length(new_user["name"], 1, 100):
                return Response("name must be between 1 and 60 characters", mimetype="text/plain", status=400)
        else:
            return Response("name is required to create new user", mimetype="text/plain", status=400)
        
        if "email" in new_user:
            if not check_email(new_user["email"]):
                return Response("Invalid email address", mimetype="text/plain", status=400)
            if not check_length(new_user["email"], 1, 60):
                return Response("email length max 60 characters", mimetype="text/plain", status=400)

            #check if email already exists
            email_exists = db_fetchone_index("SELECT EXISTS(SELECT email FROM users WHERE email=?)", [new_user["email"]])
            if email_exists == 1:
                return Response("email already exists. Try another email", mimetype="text/plain", status=400)
        else:
            return Response("email is required to create new user", mimetype="text/plain", status=400)
        
        if "password" in new_user:
            if not check_length(new_user["password"], 6, 50):
                return Response("password must be between 6 and 60 characters", mimetype="text/plain", status=400)
        else:
            return Response("password is required to create new user", mimetype="text/plain", status=400)

        #create user
        db_commit("INSERT INTO users(auth_level, name, email, password) VALUES(?,?,?,?)", \
                    [new_user["authLevel"], new_user["name"], new_user["email"], new_user["password"]])
        
        #get user id of newly insterted job to add data below
        created_user_id = db_fetchone_index_noArgs("SELECT MAX(id) FROM users")
        
        #if data exists for other columns, validate then update row
        if "phone" in new_user:
            if not check_length(new_user["phone"], 7, 20):
                db_commit("DELETE FROM users WHERE id=?", [created_user_id])
                return Response("phone number must be between 7 and 20 characters", mimetype="text/plain", status=400)
            db_commit("UPDATE users SET phone=? WHERE id=?", [new_user["phone"], created_user_id])
        
        if "hourlyRate" in new_user:
            try:
                rate_floated = float(new_user["hourlyRate"])
                db_commit("UPDATE users SET hourly_rate=? WHERE id=?", [new_user["hourlyRate"], created_user_id])
            except ValueError:
                db_commit("DELETE FROM users WHERE id=?", [created_user_id])
                return Response("hourlyRate must be a number", mimetype="text/plain", status=400)
        
        #get new user from db and send back in a valid dict
        req_new_user = db_fetchone("SELECT id, auth_level, name, email, phone, hourly_rate FROM users WHERE id=?", [created_user_id])
        user_to_list = []

        user = pop_user_all(req_new_user)
        user_to_list.append(user)

        return Response(json.dumps(user_to_list, default=str),
                mimetype="application/json",
                status=201)

    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong at users request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)