import re
from app_package.functions.queryFunctions import db_fetchone, db_fetchone_index
from flask import Response

# Regular expression for email string
def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def pop_user_dict(data):
    user = {
        "userId": data[0],
        "auth": data[1],
        "name": data[2],
        "email": data[3],
        "phone": data[4],
    }
    return user

def pop_job_all(data):
    job = {
        "jobId": data[0],
        "title": data[1],
        "location": data[2],
        "content": data[3],
        "scheduledDate": data[4],
        "completedDate": data[5],
        "cost": data[6],
        "charged": data[7],
        "jobStatus": data[8],
        "invoiced": data[9],
        "clientId": data[10],
        "notes": data[11]
    }
    return job

def pop_job_emp(data):
    job = {
        "jobId": data[0],
        "title": data[1],
        "location": data[2],
        "content": data[3],
        "scheduledDate": data[4],
        "completedDate": data[5],
        "jobStatus": data[6],
        "clientId": data[7],
        "notes": data[8]
    }
    return job

def get_auth(token):
    is_token_valid = db_fetchone_index("SELECT EXISTS(SELECT user_id FROM user_session WHERE session_token=?)", [token])
    if is_token_valid == 1:
        auth_level = db_fetchone("SELECT auth_level FROM users u INNER JOIN user_session s \
                                ON u.id = s.user_id WHERE session_token=?", [token])    
        return auth_level[0]
    else:
        return "invalid"

