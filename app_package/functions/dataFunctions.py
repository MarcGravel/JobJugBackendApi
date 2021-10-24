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
