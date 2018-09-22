import os
import logging

# NOTE: IN CASE IT CREATES A FOLDER WITHOUT THE PERMISSIONS NEEDED TO WRITE A FILE, POSSIBLE SOLUTION: sudo chmod -R 777 /home/pi/...

def setFolder(path):

    # check if there is a log folder; if not, create a new one       
    datapath = "/home/pi/logs_data/"
    if not os.path.exists(datapath):
        os.makedirs(datapath)
    # check if there is a debug_log folder; if not, create a new one  
    debugpath = "/home/pi/logs_debug/"
    if not os.path.exists(debugpath):
        os.makedirs(debugpath)
        
    # check if there is a folder for a selected hardware; if not, create a new one
    cmd = "/home/pi/logs_data"
    files = os.listdir(cmd)
    if path not in files:
        cmd = "/home/pi/logs_data/{0}/uploaded_logs".format(path)
        os.makedirs(cmd)
       
def setWorkingDirectory(path):

    # set working directory
    log_dir = "/home/pi/logs_data/{0}".format(path)
    os.chdir(log_dir)
    logging.info("changed dir to {}".format(os.getcwd()))
    return log_dir
