# JobJug API

JobJug API is the backend API for JobJug, a website for simple project management in the contracting industry.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
click==8.0.1
colorama==0.4.4
decorator==5.1.0
Flask==2.0.2
Flask-Cors==3.0.10
itsdangerous==2.0.1
Jinja2==3.0.2
mariadb==1.0.7
MarkupSafe==2.0.1
six==1.16.0
validators==0.18.2
Werkzeug==2.0.2
```

# Content

[User Login](#user-login-apilogin)

[Users](#users-apiusers)

[Jobs](#jobs-apijobs)

[Assign Job](#assign-apiassign)

# Usage

## User Login: /api/login
The login end point supports only the POST and DELETE methods.

### POST
HTTP success code: 201

POST will successfully log in a user if email/password combo match

Return data contains confirmation information about the user as well as a session token.

An error will be returned if the login information is invalid.

Required data: {"email", "password"}
```json
Example Data:

JSON Data Sent:
    { 
      "email": "john@gmail.com",
      "password": "anypass123"
    }

JSON Data Returned: 
    { 
        "userId": 2,
        "auth": "employee",
        "name": "John Smith",
        "email": "john@gmail.com",
        "phone": "555-555-2323",
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X"
    } 
```

### DELETE
HTTP success code: 204

DELETE will destroy the session token.

An error will be returned if the sessionToken is invalid.

No data returned on success.    

Required data: {"loginToken"}
```json
Example Data:

JSON Data Sent:
    { 
      "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X"
    }

No Data Returned
```

## Users: /api/users
The users end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

All user auth levels can GET all users

Employees will not receive hourly rate in the returned data

All requests require valid session token in headers

Send no params to receive all users data

Send userId to receive data on specific user

Example is a manager get request for specific user

Required Data in headers: {"sessionToken"}

Optional Params: {"userId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
        "userId": "14" 
    }

JSON Data Returned: 
    [
        {
            "userId": 14,
            "authLevel": "employee",
            "name": "Jerry Dean",
            "email": "jdean@gmail.com",
            "phone": "555-555-5533",
            "hourlyRate": 28.5
        }
    ]
```

### POST
HTTP success code: 201

Only managers and admin can post a new user

Auth level must be: "admin" OR "manager" OR "employee"

Emails must be unique and will return error on duplicate email submit

Required Data: {"sessionToken", "authLevel", "name", "email", "password"}

Optional Data: {"phone", "hourlyRate"}

```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "authLevel": "employee",
        "name": "Jerry Dean",
        "email": "jdean@gmail.com",
        "password": "secretpass123",
        "phone": "555-555-5533",
        "hourlyRate": 28.5
    }

JSON Data Returned: 
    [
        {
            "userId": 14,
            "authLevel": "employee",
            "name": "Jerry Dean",
            "email": "jdean@gmail.com",
            "phone": "555-555-5533",
            "hourlyRate": 28.5
        }
    ]
```

### PATCH 
HTTP success code: 201

PATCH will update users information

Only managers and admins can update user info

Employees can update their own passwords only

Managers can update their own passwords only

Admins can update all passwords

Requires a valid session token as well as a userId to be passed in data

Can update any amount of information in a single request

Send userId of user to update

Required Data: {"sessionToken", "userId"} + n amount of optional data

Optional Data: {"name", "email", "password", "phone", "hourlyRate"}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "password": "secretpass123",
    }

JSON Data Returned: 
    [
        {
            "userId": 14,
            "authLevel": "employee",
            "name": "Jerry Dean",
            "email": "jdean@gmail.com",
            "phone": "555-555-5533",
            "hourlyRate": 28.5
        }
    ]
```

### DELETE
HTTP success code: 204

DELETE will delete a user from the database

Only managers and admin can delete users

Managers cannot delete admins

Send userId of user to delete

Required Data: {"sessionToken", "userId}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "userId": "85",
    }

No JSON Data Returned: 
```

## Jobs: /api/jobs
The jobs end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

GET will return jobs based on requests from users

Managers and admin can request all jobs, employees can only request jobs assigned to them.

All requests require a session token in the headers

For all active and completed jobs, send no params

For all archived jobs, send {jobStatus: "archived"} (this only available to managers and admin)

For a specific job, send the job id number. ex: {jobId: "2"}

Remember, employees can only request jobs already assigned to them

Required Data in headers: {"sessionToken"}

Optional Params: {"jobStatus"} OR {"jobId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
      "jobStatus": "archived" 
    }

JSON Data Returned: 
    [
        {
            "jobId": 634,
            "title": "Westmount Condos",
            "location": "121 Westhills Road",
            "content": "Remove all drywall. Pull old insulation, repair top plate damage. Install new insullation and drywall. Mud/Tape.",
            "scheduledDate": "2020-11-19",
            "completedDate": "2020-11-21",
            "cost": 2853.23,
            "charged": 3625.00,
            "jobStatus": "archived",
            "invoiced": 1,
            "clientId": 53,
            "notes": null
        },
        {
            "jobId": 411,
            "title": "Advance Homes",
            "location": "6131 43 E ave",
            "content": "Cabinet door replacement. Remove old doors and hinges. Install customer supplied hinges. New oak doors (lot# 2541234) to be installed on new hinges.",
            "scheduledDate": "2019-11-21",
            "completedDate": "2019-11-29",
            "cost": 1550.42,
            "charged": 1940.00,
            "jobStatus": "archived",
            "invoiced": 1,
            "clientId": 34,
            "notes": "Completed on weekend. 2 hrs overtime"
        },
    ]
```

### POST
HTTP success code: 201

POST will create a new job. Only managers or admin can post new jobs

All requests require a valid manager/admin session token included in the json data

All request also require a title and jobStatus to be sent

Other data is optional and not required for a successful job post.

Required Data: {"sessionToken", "title", "jobStatus"}

Optional Data: {"location", "content", "scheduledDate", "completedDate", "cost", "charged", "invoiced", "clientId", "notes"}
```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "title": "Upgrade bedroom walls",
        "location": "6131 43 E ave",
        "content": "All bedrooms walls to be removed, new insulation placed, and new        dryawall with fresh paint",
        "scheduledDate": "2022-05-23",
        "completedDate": null,
        "cost": 2242.53,
        "charged": 2950.00,
        "jobStatus": "active",
        "invoiced": 0,
        "clientId": 3,
        "notes": null
    }

JSON Data Returned: 
    [
        {
            "jobId": 63,
            "title": "Upgrade bedroom walls",
            "location": "6131 43 E ave",
            "content": "All bedrooms walls to be removed, new insulation placed, and new dryawall with fresh paint",
            "scheduledDate": "2022-05-23",
            "completedDate": null,
            "cost": 2242.53,
            "charged": 2950.00,
            "jobStatus": "active",
            "invoiced": 0,
            "clientId": 3,
            "notes": null
        }
    ]
```

### PATCH
HTTP success code: 200

PATCH update information on an existing job

Managers and admin can update anything, but employees can only update completedDate, jobStatus, and notes

Employees can only update jobStatus to "completed", they cannot reactivate a job or archive it.

All requests require a valid session token and a valid job id included in the json data 

Any amount of values can be updated in a single request so long as authorization is adheared to.

Required Data: {"sessionToken", "jobId"} + n amount of optional data.

Optional Data: {"title", "jobStatus", "location", "content", "scheduledDate", "completedDate", "cost", "charged", "invoiced", "clientId", "notes"}
```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": 63,
        "completedDate": "2021-05-24",
        "jobStatus": "complete",
        "invoiced": 1
    }

JSON Data Returned: 
    [
        {
            "jobId": 63,
            "title": "Upgrade bedroom walls",
            "location": "6131 43 E ave",
            "content": "All bedrooms walls to be removed, new insulation placed, and new dryawall with fresh paint",
            "scheduledDate": "2021-05-23",
            "completedDate": "2021-05-24",
            "cost": 2242.53,
            "charged": 2950.00,
            "jobStatus": "complete",
            "invoiced": 1,
            "clientId": 3,
            "notes": null
        }
    ]
```

### DELETE
HTTP success code: 204

DELETE will delete a job from the database only if passes a few conditions

Only managers and admin can delete jobs, employees cannot

Jobs that are currently invoiced cannot be deleted, will return an error asking user to archive the job instead.

Must send session token for validation as well as a job id to delete

Required Data: {"sessionToken", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": 63,
    }

No JSON Data returned
```

## Assign Job: /api/assign
The login end point supports the GET, POST and DELETE methods.

### GET
HTTP success code: 200

GET will get all users assigned to specified job

Will return a list of user information

Only managers and admin can GET assignments

Required data: {"sessionToken", "jobId"}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": 63,
    }

JSON Data Returned:
    [ 
        { 
            "userId": 2,
            "auth": "employee",
            "name": "John Smith",
            "email": "john@gmail.com",
            "phone": "555-555-2323",
            "hourlyRate": "27"
        },
        { 
            "userId": 7,
            "auth": "employee",
            "name": "Tim Doe",
            "email": "tim@gmail.com",
            "phone": "555-555-7763",
            "hourlyRate": "21.5"
        }
    ] 
```

### POST
HTTP success code: 201

POST will assign a specified user to a specified job

Will return a success message in JSON format

Only managers and admin can POST assignments

Error returned if user is already assigned to the job

Required data: {"sessionToken", "userId", "jobId"}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "userId": 7, 
        "jobId": 63,
    }

JSON Data Returned:
    { 
        "message": "user is assigned to job"
    }

```

### DELETE
HTTP success code: 204

DELETE will remove a specified user to a specified job

Only managers and admin can DELETE assignments

Error returned if user is not assigned to job

No return Response

Required data: {"sessionToken", "userId", "jobId"}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "userId": 7, 
        "jobId": 63,
    }

No JSON Data Returned
```
