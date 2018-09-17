#---------------------------------#
# filename: wifi1main.py          #
# author: Zhiye (Zoey) Song       #
# changes by: Idit Belachsen      #
#---------------------------------#
# written in python2
'''
to modify: all values in sensor file
log files separated for sensor and mac
'''
import subprocess
import datetime
import os
import sys
import time
import logging
from connectionStatusUtils import checkInternetConnection
import DropboxClient
from directoryUtils import setWorkingDirectory,setFolder
import wifiMacAddress

logging.basicConfig(
     filename='/home/pi/logs_debug/wifi_main_debug_{}.log'.format(datetime.datetime.now()),
     level=logging.DEBUG,
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

dbxClt = DropboxClient.DropboxClient('k51crRTDG-AAAAAAAAAAE0l64QIodXiNIYV1ghgNDnYm-6dP_g6sOH2kxCmuqqkD')
macAddRdr = wifiMacAddress.MacAddressReader()  # create an instance of MacAddressReader class

DURATION = 1
DEBUG = True

#hardware id
SELECTED_HARDWARE = 1 #1 for SDS021, 2 for PMS5003, 3 for SDS011

def detectDevices(duration):

    '''
        This function calls wifiMacAddress (MacAddressReader class) which
        detects nearby wi-fi enabled devices and read their mac address

        It receives all mac addresses and their timestamps
        in the set duration parameter of time.

        Then it creates a new log file and stores the data.
        File name is the name of the end of the collection period.
'''
    # get mac addresses
    fmt = "%Y-%m-%d %H:%M:%S"
    results = macAddRdr.readMacAddress(DURATION, fmt)

    # write results to wifi log file
    # CHANGE TO FULL PATH
    file_name = "/home/pi/logs_data/wifi_" + str(datetime.datetime.now()).split(".")[0]
    with open(file_name,"w") as f:
        msg = ['MAC ADDRESSES','TIMESTEMPS']
        for i in range(len(results)):
            for j in range(len(results[0])):
                f.write(results[i][j] + "\n")
            f.write("--END OF " + msg[i] + "--\n")

#--------------------------#
# Execute Data Acquisition #
#--------------------------#
while True:
    try:
        #wait for pi to boot up
        if not DEBUG:
            time.sleep(60)
        # create folders and set working directory
        setFolder('wifi' + str(SELECTED_HARDWARE))
        log_dir = setWorkingDirectory('wifi' + str(SELECTED_HARDWARE))

        while True:

            #upload any not uploaded log
            if checkInternetConnection():
                logging.info("Found internet wireless connection, uploading existing logs to dropbox")
                loaded_file_count = 0
                files = os.listdir(log_dir)
                for file in files:
                    if "wifi_" in file:
                        logging.debug("Trying to upload file {} to dropbox".format(file))
                        try:
                            dbxClt.uploadToDropbox(file, 'wifi' + str(SELECTED_HARDWARE))
                            loaded_file_count += 1
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
                logging.info("Starting to measure mac addresses")
                detectDevices(DURATION)
                logging.info("Done measuring mac addresses")
            except Exception:
                logging.exception("Error while taking measurement of mac addresses")

    except Exception:
        logging.exception("Error in main loop")

