#---------------------------------#
# filename: sensor1main.py        #
# author: Zhiye (Zoey) Song       #
# changes by: Idit Belachsen      #
#---------------------------------#
# written in python2
import subprocess
import datetime
import os
import time
import logging
from connectionStatusUtils import checkInternetConnection
import DropboxClient
from directoryUtils import setWorkingDirectory,setFolder

# create an instance of the dropbox class 
dbxClt = DropboxClient.DropboxClient('k51crRTDG-AAAAAAAAAAE0l64QIodXiNIYV1ghgNDnYm-6dP_g6sOH2kxCmuqqkD')

# set duration = after how many minutes data is written to a log file and uploaded to dropbox
DURATION = 2 #in minutes - NOTE IT SHOULD BE AT LEAST 2 MINUTES OTHERWISE WILL RUN FOREVER

#hardware id
SELECTED_HARDWARE = 1 #1 for SDS021, 2 for PMS5003, 3 for SDS011

# create folders
setFolder(str(SELECTED_HARDWARE))

import sensorSDS021  #importing is done here because class is creating a file in logs_debug folder which is only created in setFolder

# create log debug file
logging.basicConfig(
     filename='/home/pi/logs_debug/sensor_debug_{}.log'.format(datetime.datetime.now()),
     level=logging.DEBUG, 
     format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

#set working directory
log_dir = setWorkingDirectory(str(SELECTED_HARDWARE))

def doMeasurement(duration):

    """function:
        This function calls one of the three sensor
        reader classes according to which station 
        was selected. It receives all values 
        of everything (averaged per minute) after
        a measurement of a set duration of time.
        
        Then it creates a new log file and stores the data.
        File name is the name of the end of the collection period.
    """

    #open a log file for current time
    #file_name = str(datetime.datetime.now()).split(".")[0]
    # NOTE(Idit) - seems like the debug files will have a different name than the log files
    # I removed the file_name initialization and the name of the debug file will be determined
    # in the read function in sensorSDS021.SDS021Reader

    # get PM measurements
    if SELECTED_HARDWARE == 1:
        USBPORT  = "/dev/ttyUSB0"
        results = sensorSDS021.SDS021Reader(USBPORT).readPM(duration,no_outputs=2)
    elif SELECTED_HARDWARE == 2:
        USBPORT  = "/dev/ttyS0"
        results = sensorPMS5003.PMS5003Reader(USBPORT).readPM(duration,no_outputs=12)
    elif SELECTED_HARDWARE == 3:
        USBPORT  = "/dev/ttyUSB0"
        results = sensorSDS011.SDS011Reader(USBPORT).readPM(duration,no_outputs=2)

    # (in case results returned zero values, means something was not measured/was not appended to results)
    # write results to log file
    file_name = "/home/pi/logs_data/" + str(SELECTED_HARDWARE) + "/" + "log_" + str(datetime.datetime.now()).split(".")[0]
    with open(file_name,"w") as f:
        for i in range(len(results[0])):#index for pm#
            for j in range(len(results)):#index for min#
                f.write(str(results[j][i]) + "\n")
            f.write("--END OF "+str(i+1)+"--\n")

#--------------------------#
# Execute Data Acquisition #
#--------------------------#
if DURATION==1:
      logging.exception("Duration must be greater than 1 minute")

while True and DURATION>1:
    logging.info("Starting data acquisition")
    try:            
        while True:
            #upload any not uploaded log
            if checkInternetConnection():
                logging.info("Found internet wireless connection, uploading existing logs to dropbox")
                loaded_file_count = 0
                files = os.listdir(log_dir)
                for file in files:
                    if "log_" in file:
                        logging.debug("Trying to upload file {} to dropbox".format(file))
                        try:
                            dbxClt.uploadToDropbox(file, str(SELECTED_HARDWARE))
                            loaded_file_count+=1
                        except Exception:
                            logging.exception("Error uploading file {} to dropbox".format(file))
                        
                logging.info("Done upploading files to dropbox, {} files loaded.".format(loaded_file_count))
                
            else:
                try:
                    subprocess.check_output("sudo ifconfig wlan0 up".split())
                except:
                    logging.warning("wlan0 failed")
                try:
                    subprocess.check_output("sudo ifconfig wlan1 up".split())
                except:
                    logging.warning("wlan1 failed")

            #measurement
            try:
                logging.info("Starting to measure")
                doMeasurement(DURATION)
                logging.info("Done measuring")
            except Exception:
                logging.exception("Error while taking measurement")

    except Exception:
        logging.exception("Error in main loop")

  
    