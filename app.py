from app_package import app
import sys

#This file is entry point of app
#see endpoints/__init__ for flask and app initialization.

# checks arguments on run for testing or development.
#bjoern server only runs on development 
#CORS is only open during testing
#debug=True only used behind testing mode.
if len(sys.argv) > 1 and len(sys.argv) < 3:
    mode = sys.argv[1]
    if mode == "production":
        import bjoern
        host = "0.0.0.0"
        port = 5010
        print("Running in production mode")
        bjoern.run(app, host, port)
    elif mode == "testing":
        from flask_cors import CORS
        CORS(app)
        print("Running in testing mode")
        app.run(debug=True)
    else:
        print("Invalid mode argument. Please choose testing or production")  

else:
    print("No argument provided or too many arguments")
    exit()