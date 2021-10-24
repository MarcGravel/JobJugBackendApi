import re

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
