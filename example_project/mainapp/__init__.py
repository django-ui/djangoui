import os

#print ("Initializing example_app folder: " + os.getcwd())
if (os.path.exists("mainapp/services.py")):
    from . import services
    
