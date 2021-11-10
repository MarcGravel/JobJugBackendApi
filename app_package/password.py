from app_package import app
from flask import request, Response
from app_package.functions.dataFunctions import get_auth, check_length
from app_package.functions.queryFunctions import db_commit, db_fetchone
import bcrypt

#User update password in nav/sidebars

@app.route('/api/password', methods=['PATCH'])
def api_password():
    if request.method == 'PATCH':
        data = request.json
        token = data.get("sessionToken")
        
        #check valid session token
        auth_level = get_auth(token)
        if auth_level == "invalid":
            return Response("Invalid session Token", mimetype="text/plain", status=400)

        if len(data.keys()) == 3 and {"sessionToken", "password", "newPassword"} <= data.keys():
            password = data.get("password")
            new_pass = data.get("newPassword")
            
            #get userid from token
            user_info = db_fetchone("SELECT u.id, u.password FROM users u INNER JOIN user_session s ON u.id = s.user_id WHERE session_token=?", [token]) 
            user_id = user_info[0]
            user_pass = user_info[1]
            
            #validate password
            if bcrypt.checkpw(str(password).encode(), str(user_pass).encode()):
                
                #check if new password is same as old password
                if password == new_pass:
                    print(repr(password), repr(new_pass))
                    return Response("Can't use old password, try a new one.", mimetype="text/plain", status=400)
                
                #check length of new pass
                if not check_length(new_pass, 6, 50):
                    return Response("Password must be between 6 and 60 characters", mimetype="text/plain", status=400)

                #salt and hash password
                pw = new_pass
                salt = bcrypt.gensalt()
                hashed_pass = bcrypt.hashpw(str(pw).encode(), salt)
                
                db_commit("UPDATE users SET password=? WHERE id=?", [hashed_pass, user_id])
                
                return Response(status=201)
            
            else:
                return Response("Existing password Incorrect", mimetype="text/plain", status=401)     
        else:
            return Response("Invalid data sent", mimetype="text/plain", status=400)
    else:
        print("Something went wrong at password request.method")
        return Response("Request method not accepted", mimetype='text/plain', status=500)