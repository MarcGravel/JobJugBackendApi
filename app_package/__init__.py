from flask import Flask

app = Flask(__name__)

#imports below the flask (app) initialization to avoid circular imports 
#this is done when importing any files within this package
from app_package import login
from app_package import jobs
from app_package import users
from app_package import assign
from app_package import clients
from app_package import cliass