import os

def setFolder(path):

    # check if there is a log folder; if not, create a new one
    cmd = "/home/pi"
    files = os.listdir(cmd)
    if "logs_data" not in files:
        cmd = "sudo mkdir logs_data"
        os.system(cmd)

    # check if there is a folder for a selected hardware; if not, create a new one
    cmd = "/home/pi/logs_data"
    files = os.listdir(cmd)
    if path not in files:
        cmd = "sudo mkdir -p logs_data/{0}/uploaded_logs".format(path)
        os.system(cmd)

def setWorkingDirectory(path):

    # set working directory
    log_dir = "/home/pi/logs_data/{0}".format(path)
    os.chdir(log_dir)
    return log_dir
