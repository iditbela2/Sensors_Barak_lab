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
from directoryUtils import setDirectory,setFolder

logging.basicConfig(
     filename='/home/pi/wifi_debug_{}.log'.format(datetime.datetime.now()),
     level=logging.DEBUG,
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

dbxClt = DropboxClient('k51crRTDG-AAAAAAAAAAE0l64QIodXiNIYV1ghgNDnYm-6dP_g6sOH2kxCmuqqkD')

DURATION = 5
DEBUG = True

#hardware id
SELECTED_HARDWARE = 1 #1 for SDS021, 2 for PMS5003, 3 for SDS011

def detectDevices(duration):

    '''
        This function calls wifiMacAddress class which contains
        two functions - one which detects nearby wi-fi enabled devices
        and another which organizes all mac addresses
        found ....???

        It receives all mac addresses and their timestamps
        in the set duration parameter of time.

        Then it creates a new log file and stores the data.
        File name is the name of the end of the collection period.
'''
    # get mac addresses
    fmt = "%Y-%m-%d %H:%M:%S"


    # write results to wifi log file
    file_name = "wifi_" + str(datetime.datetime.now()).split(".")[0]
    with open(file_name,"w") as f:






        # initialization
        splited_line = []
        time_list = []
        start_append = 0
        exp = 0

        # command line configuration
        # only display source, and destination of the packet
        cmd = ("sudo tshark -l -i mon0 -o column.format:" + '"src","%uhs","dst","%uhd"').split()

        # execute the command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # for every output line
        for line in iter(process.stdout.readline, ""):

            # acquire data for set duration of time
            if int(str(datetime.datetime.now()).split(":")[1]) % duration == 0 and int(
                    str(datetime.datetime.now()).split(":")[1]) != start_time:
                process.terminate()
                break

            # start writing to the file when a MAC address is read
            if start_append == 0:
                if "Capturing on" in str(line):
                    start_append = 1
                    continue
                else:
                    df.write(str(line) + "\n")

            splited_line = line.split(" ")

            for mac in splited_line:

                if "\n" not in mac:
                    mac = mac + "\n"

                # check if it is a valid MAC address
                if ("ff:ff:ff:ff:ff:ff" not in mac) and (len(mac) == 18):

                    # write the address to file if it was not detected before
                    mac = mac.replace(":", "")
                    if mac not in time_list:
                        time_list.append(mac)
                        f.write(mac)
                        # print mac
        if int(str(datetime.datetime.now()).split(":")[1]) % duration != 0:
            print
            "pipe closed"
            df.write("pipe closed\n")
            df.write(str(line) + "\n")
            try:
                subprocess.check_output(("sudo airmon-ng start wlan0").split())
            except Exception as e:
                df.write(str(sys.exc_info()))
                df.write(str(e))
                df.write('\n')
            try:
                subprocess.check_output(("sudo airmon-ng start wlan1").split())
            except Exception as e:
                df.write(str(sys.exc_info()))
                df.write(str(e))
                df.write('\n')

        ##        exp=1
        df.write(subprocess.check_output("free -m".split()))
        f.write("---END OF MAC ADDRESSES---")
        f.close()
        process.terminate()
        if exp == 1:
            raise Exception('pipe closed')
        return


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
        log_dir = setDirectory('wifi' + str(SELECTED_HARDWARE)

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
                            dbxClt.uploadToDropbox(file,SELECTED_HARDWARE,'/home/pi/logs/wifi'+str(SELECTED_HARDWARE)+'/')
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

