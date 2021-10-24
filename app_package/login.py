from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import check_email, pop_user_dict
from app_package.functions.queryFunctions import db_commit, db_fetchone, db_fetchone_index
import secrets
import json

@app.route('/api/login', methods=['POST', 'DELETE'])
def api_login():
    if request.method == 'POST':
        data = request.json

        if len(data.keys()) == 2 and {"email", "password"} <= data.keys():
            email = data.get("email")
            password = data.get("password")
            
            #function to check if valid email address
            if not check_email(email):
                return Response("Not a valid email", 
                                mimetype="text/plain", 
                                status=400)

            isValidEmail = db_fetchone_index("SELECT EXISTS(SELECT email FROM users WHERE email=?)", [email])
            
            if isValidEmail == 1:
                user_pass = db_fetchone_index("SELECT password FROM users WHERE email=?", [email])

                #validate pass, get user info, and generate token if valid
                if password == user_pass:
                    user = db_fetchone("SELECT id, auth_level, name, email, phone FROM users WHERE email=?", [email])
                    token = secrets.token_urlsafe(16)

                    resp = pop_user_dict(user)
                    resp["sessionToken"] = token

                    #add token+user to session table
                    db_commit("INSERT INTO user_session(user_id, session_token) VALUES(?,?)", [user[0], token])

                    return Response(json.dumps(resp),
                                    mimetype="application/json",
                                    status=201)
                else:
                    return Response("Invalid credentials.", mimetype='text/plain', status=400)
            else:
                return Response("Email does not exist in database", mimetype="text/plain", status=404)
        else:
            return Response("Incorrect data sent", mimetype="text/plain", status=400)
    
    elif request.method == 'DELETE':
        data = request.json

        if len(data.keys()) == 1 and {"sessionToken"} <= data.keys():
            token = data.get("sessionToken")
            is_token_valid = db_fetchone_index("SELECT EXISTS(SELECT * FROM user_session WHERE session_token=?)", [token])

            if is_token_valid == 1:
                db_commit("DELETE FROM user_session WHERE session_token=?", [token])
                return Response(status=204)
            else:
                return Response("Token is not valid", mimetype="text/plain", status=400)       
        else:
            return Response("Incorrect data sent", mimetype="text/plain", status=400)   
    else:
        return Response("Method not allowed", mimetype="text/plain", status=405)