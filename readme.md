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

[Jobs](#jobs=apijobs)

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

## Jobs: /api/jobs
The login end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

GET will return jobs based on requests from users

Managers and admin can request all jobs, employees can only request jobs assigned to them.

All requests require a session token in the headers

For all active and completed jobs, send no params

For all archived jobs, send {jobStatus: "archived"} (this only available to managers and admin)

For a specific job, send the job id number. ex: {jobId: "2"}

Remember, employees can only request jobs already assigned to them

Required data in headers: {"sessionToken"}
Optional Data: {jobStatus} OR {jobId}
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

Required data: {"sessionToken", "title", "jobStatus"}
Optional Data: {"location", "content", "scheduledDate", "completedDate", "cost", "charged", "invoiced", "clientId", "notes"}
```json
Example Data:

JSON Data Sent:
    {
        "sessionToken": "5R3pkYsHZDgI4nhXM3Is9X", 
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

All requests require a valid session token and a valid job id included in the json data 

Any amount of values can be updated in a single request so long as authorization is adheared to.

Required data: {"sessionToken", "jobId"} + n amount of optional data.
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
