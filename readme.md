# JobJug API

JobJug API is the backend API for JobJug, a website for simple project management in the contracting industry.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
bcrypt==3.2.0
blinker==1.4
borb==2.0.13
certifi==2021.10.8
cffi==1.15.0
charset-normalizer==2.0.7
click==8.0.3
colorama==0.4.4
Flask==2.0.2
Flask-Cors==3.0.10
Flask-Mail==0.9.1
fonttools==4.28.0
idna==3.3
itsdangerous==2.0.1
Jinja2==3.0.2
mariadb==1.0.8
MarkupSafe==2.0.1
Pillow==8.4.0
pycparser==2.20
python-barcode==0.13.1
qrcode==7.3.1
requests==2.26.0
six==1.16.0
urllib3==1.26.7
Werkzeug==2.0.2
```

# Content

[User Login](#user-login-apilogin)

[Users](#users-apiusers)

[Jobs](#jobs-apijobs)

[Assign Job](#assign-apiassign)

[Clients](#clients-apiclients)

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

Auth level must be: "admin" OR "manager"

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
        "hourlyRate": "28.5"
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
            "jobId": "634",
            "title": "Westmount Condos",
            "location": "121 Westhills Road",
            "content": "Remove all drywall. Pull old insulation, repair top plate damage. Install new insullation and drywall. Mud/Tape.",
            "scheduledDate": "2020-11-19",
            "completedDate": "2020-11-21",
            "cost": "2853.23",
            "charged": "3625.00",
            "jobStatus": "archived",
            "invoiced": "1",
            "clientId": "53",
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
        "cost": "2242.53",
        "charged": "2950.00",
        "jobStatus": "active",
        "invoiced": "0",
        "clientId": "3",
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
        "jobId": "63",
        "completedDate": "2021-05-24",
        "jobStatus": "complete",
        "invoiced": "1"
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
        "jobId": "63",
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
        "jobId": "63",
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
        "userId": "7", 
        "jobId": "63",
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
        "userId": "7", 
        "jobId": "63",
    }

No JSON Data Returned
```

## Clients: /api/clients
The clients end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

Managers and admins can GET all clients

Employees can only GET clients that are attached to jobs the employee is assigned to

All requests require valid session token in headers

Send no params to receive all available client data as per authorization level

Send clientId to receive data on specific client

Error returned if employee sends clientId not assigned to them

Required Data in headers: {"sessionToken"}

Optional Params: {"clientId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
        "clientId": "14" 
    }

JSON Data Returned: 
    [
        {
            "clientId": 14,
            "name": "John Doe",
            "company": "Some Company Inc.",
            "address": "121 Westhills Road",
            "email": "john.doe@gmail.com",
            "phone": "604-555-2342"
        }
    ]
```

### POST
HTTP success code: 201

Only managers and admin can post a new client

Auth level must be: "admin" OR "manager"

No unique data required as companies can have shared emails and phone numbers

Required Data: {"sessionToken", "name"}

Optional Data: {"company", "address", "email", "phone"}

```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "name": "John Doe",
        "company": "Some Company Inc.",
        "address": "121 Westhills Road",
        "email": "john.doe@gmail.com"
    }

JSON Data Returned: 
    [
        {
            "userId": 14,
            "name": "John Doe",
            "company": "Some Company Inc.",
            "address": "121 Westhills Road",
            "email": "john.doe@gmail.com",
            "phone": null
        }
    ]
```

### PATCH 
HTTP success code: 201

PATCH will update clients information

Only managers and admins can update client info

Requires a valid session token as well as a clientId to be passed in data

Can update any amount of information in a single request and all info can be updated

Send clientId of client to update

Required Data: {"sessionToken", "clientId"} + n amount of optional data

Optional Data: {"name", "company", "address", "email", "phone"}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "clientId": "14",
        "company": "Updated Company Inc.",
        "phone": "555-555-1234"
    }

JSON Data Returned: 
    [
        {
            "userId": 14,
            "name": "John Doe",
            "company": "Updated Company Inc.",
            "address": "121 Westhills Road",
            "email": "john.doe@gmail.com",
            "phone": "555-555-1234"
        }
    ]
```

### DELETE
HTTP success code: 204

DELETE will delete a client from the database

Only managers and admin can delete clients

Send clientId of client to delete

Required Data: {"sessionToken", "clientId}
```json
Example Data:

JSON Data Sent:
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "clientId": "14",
    }

No JSON Data Returned: 
```

## Assign Employees: /api/assign
The assign end point supports GET, POST, and DELETE methods.

### GET
HTTP success code: 200

GET will return all employees assigned to the jobId sent

Required Data in headers: {"sessionToken"}

Required Params: {"jobId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
        "jobId": "14" 
    }

JSON Data Returned: 
    [
        {
            "userId": 2,
            "authLevel": "employee",
            "name": "John Smith",
            "email": "john@gmail.com",
            "phone": "555-555-9999"
        }
    ]
```
### POST
HTTP success code: 201

Only managers and admin can post employee assignment to jobs

POST will assign a new employee to a specified job ID

Multiple employees are able to be assigned to a single job.

And error will return if employee already assigned to job

Required Data: {"sessionToken", "userId", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": "14",
        "userId": "2" 
    }

JSON Data Returned: 
    {
        "message": "user is assigned to job"
    }
```

### DELETE
HTTP success code: 204

Only managers and admin can delete employee assignments

DELETE will remove assignment of employee to a specified job ID

And error will return if employee is not assigned to job

Required Data: {"sessionToken", "userId", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": "14",
        "userId": "2" 
    }

No JSON Data Returned
```

## Assign Clients: /api/cliass
The cliass end point supports GET, POST, and DELETE methods.

### GET
HTTP success code: 200

GET will return all clients assigned tto jobs if no data sent

If you want a specific assignemnt returned, send the jobId

Employees will only receive info on clients assigned to jobs they are also assigned to

Required Data in headers: {"sessionToken"}

Optional Params: {"jobId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
        "jobId": "14" 
    }

JSON Data Returned: 
    [
        {
            "clientId": 1,
            "name": "Chris Webber",
            "company": "Private",
            "address": "121 Westhills Road",
            "email": "chris21@gmail.com",
            "phone": "604-555-2342"
        },
        {
            "clientId": 2,
            "name": "Jane Mack",
            "company": "Canada Post",
            "address": "66 NorthVan Road",
            "email": "jane44@post.com",
            "phone": "604-555-1267"
        },
    ]
```
### POST
HTTP success code: 201

Only managers and admin can post client assignment to jobs

POST will assign a new client to a specified job Id

And error will return if client already assigned to job

Required Data: {"sessionToken", "clientId", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": "14",
        "clientId": "2" 
    }

JSON Data Returned: 
    {
        "message": "client is assigned to job"
    }
```

### DELETE
HTTP success code: 204

Only managers and admin can delete client assignments

DELETE will remove assignment of client to a specified job ID

And error will return if client is not assigned to job

Required Data: {"sessionToken", "clientId", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": "14",
        "clientId": "2" 
    }

No JSON Data Returned
```

## Invoice: /api/invoice
The invoice end point supports GET and POST methods.

### GET

GET will return an invoice in .pdf format that will download from suers browser

Only managers and admin can GET invoices

Send jobId to received the PDF file

The PDF will be built each get request according to the data in the jobId and
the clientId associated to that job

Required Data in headers: {"sessionToken"}

Required Params: {"jobId"}
```json
Example Data:

Headers: 
    { 
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X",
        "Content-Type": "application/json"
    }

JSON Params Sent:
    { 
        "jobId": "14" 
    }
```
.pdf file is returned.

### POST

POST will create a .pdf file and automatically send in email to the client
whos clientId is attached to the jobId sent.

This method is automatic and will build and send the file immediately.

Required Data: {"sessionToken", "jobId"}

```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
        "jobId": "14",
    }
```
.pdf file built and sent by email to client.