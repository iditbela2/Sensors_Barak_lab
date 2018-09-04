#---------------------------------#
# filename: sensor1main.py        #
# author: Zhiye (Zoey) Song       #
#---------------------------------#
import subprocess
import datetime
import os
import sys
import time
import sensorSDS021#
import dropbox
import logging

logging.basicConfig(
     filename='/home/pi/sensor_debug_{}.log'.format(datetime.datetime.now()),
     level=logging.DEBUG, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

dbx=dropbox.Dropbox('WOPNUZO-UIAAAAAAAAAACYgjS_zDgTy9g0xuHm08BFrC251BAW05ZNspRn3VdTKi')

DURATION = 5 #in minutes
DEBUG = True #True to also create a debug file

#hardware id
SELECTED_HARDWARE = 1 #1 for SDS021, 2 for PMS5003, 3 for SDS011

def doMeasurement(duration, debug):

    """function:
        This function calls one of the three sensor
        reader classes according to which station 
        was selected. It receives all values 
        of everything after 
        a measurement of a set duration of time.
        
        Then it creates a new log file and stores the data.
        File name is the name of the end of the collection period.
    """

    #open a log file for current time
    file_name = str(datetime.datetime.now()).split(".")[0]
    # NOTE - the debug files will have a different name than the log files

    #measurements
    if SELECTED_HARDWARE == 1:
        USBPORT  = "/dev/ttyUSB0"
        results = sensorSDS021.SDS021Reader(USBPORT).read(duration, file_name, debug)
    elif SELECTED_HARDWARE == 2:
        USBPORT  = "/dev/ttyS0"
        results = sensorPMS5003.PMS5003Reader(USBPORT).read(duration, file_name, debug)
    elif SELECTED_HARDWARE == 3:
        USBPORT  = "/dev/ttyUSB0"
        results = sensorSDS011.SDS011Reader(USBPORT).read(duration, file_name, debug)
        
    file_name = str(datetime.datetime.now()).split(".")[0]
    file_name = "log_" + file_name
    f = open(file_name,"w")

    #if nothing is measured
    if len(results) == 0:
        f.write("-1\n")
    
    #append results at the end of the log file
    else:
        for i in range(len(results[0])):#index for pm#
            for j in range(len(results)):#index for min#
                f.write(str(results[j][i]) + "\n")
            f.write("--END OF "+str(i+1)+"--\n")
    f.close()

def checkInternetConnection():
    
    """function:
        This function checks if there is an internet connection
        to the wifi and uploading is possible. It returns True if yes.
        """
    
    list=subprocess.check_output("iwconfig")
    list=list.decode("utf-8")
    list=list.split("\n")
    for line in list:
        if line.find("wlan0")>-1 or line.find("wlan1")>-1:
            if not line[line.find("ESSID")+6]=="o":
                return True
        
    return False
    
def uploadToDropbox(file,id):
    with open('/home/pi/logs/'+str(id)+'/'+file,'r') as f:
        string=f.read()
 
    a=dbx.files_upload(string,'/'+str(id)+'/'+file)
    #move the file tto uploaded logs
    file = "'" + file + "'"
    cmd = "sudo mv {0} /home/pi/logs/{1}/uploaded_logs/".format(file, str(id))
    os.system(cmd)
    return a

#--------------------------#
# Execute Data Acquisition #
#--------------------------#
while True:
    try:
        #wait for pi to boot up
        if not DEBUG:
            time.sleep(60)
            
        #check if there is a log folder; if not, create a new one
        cmd = "/home/pi"
        files = os.listdir(cmd)
        if "logs" not in files:
            cmd = "sudo mkdir logs"
            os.system(cmd)

        #check if there is a folder for a selected hardware; if not, create a new one
        cmd = "/home/pi/logs"
        files = os.listdir(cmd)
        if str(SELECTED_HARDWARE) not in files:
            cmd = "sudo mkdir -p logs/{0}/uploaded_logs".format(str(SELECTED_HARDWARE))
            os.system(cmd)

        #set working directory
        log_dir = "/home/pi/logs/{0}".format(str(SELECTED_HARDWARE))
        os.chdir(log_dir)
            
        while True:

            #upload any not uploaded log
            if checkInternetConnection():
                logging.info("Found internet wireless connection, uploading existing logs to dropbox")
                #cmd = "/home/pi/logs/{0}".format(str(SELECTED_HARDWARE))
                loaded_file_count = 0
                files = os.listdir(log_dir)
                for file in files:
                    if "log_" in file:
                        logging.debug("Trying to upload file {} to dropbox".format(file))
                        try:
                            uploadToDropbox(file, SELECTED_HARDWARE)
                            loaded_file_count+=1
                        except Exception:
                            logging.exception("Error uploading file {} to dropbox".format(file))
                        
                logging.info("Done upploading files to dropbox, {} files loaded.".format(loaded_file_count))
                
            else:
                try:
                    subprocess.check_output("sudo ifconfig wlan0 up".split())
                except:
                    logging.warn("wlan0 failed")
                try:
                    subprocess.check_output("sudo ifconfig wlan1 up".split())
                except:
                    logging.warn("wlan1 failed")

            #measurement
            try:
                logging.info("Starting to measure")
                doMeasurement(DURATION, DEBUG)
                logging.info("Done measuring")
            except Exception
                logging.exception("Error while taking measurement")

    except Exception:
        logging.exception("Error in main loop")

