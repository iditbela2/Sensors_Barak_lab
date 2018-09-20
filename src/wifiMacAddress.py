import os
import sys
import time
import serial
import numpy as np
import datetime
import logging
import subprocess

class MacAddressReader:

    logging.basicConfig(
        filename='/home/pi/logs_debug/wifiMacAddress_debug_{}.log'.format(datetime.datetime.now()),
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    def __init__(self):
        # command line configuration
        # only display source, and destination of the packet
        # wireshark (tshark) is needed? can't see it on the raspberry pi
        cmd = ("sudo tshark -l -i mon0 -o column.format:" + '"src","%uhs","dst","%uhd"').split()
        # execute the command
        self.pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setpgrp)


    def readMacAddress(self, duration, fmt):
        """function:
            Reads the mac addresses for a given duration of time.
            Read the mac addresses the same way it reads PM values
            (to start in 0 minute).
        """
        # make sure you start measuring in a round minute and a round second.
        while(datetime.datetime.now().minute%duration!=0):
            time.sleep(1)  # in seconds.
        logging.info("started reading mac addresses")
        sys.stdout.flush() # NOT SURE IF NECESSARY
        mac_list = []
        time_list = []
        start_time = datetime.datetime.now()
        mst_time = datetime.timedelta(hours=0, minutes=duration) #measurement time
        while datetime.datetime.now() < start_time + mst_time:
            try:
                lines = self.pr.stdout.readline().split()
                for mac in lines:
                    if ("ff:ff:ff:ff:ff:ff" not in mac) and (len(mac) == 17) and (
                            mac not in mac_list):
                        mac_list.append(mac)
                        time_list.append(datetime.datetime.now().strftime(fmt))
            except Exception:
                logging.exception("error in reading mac values using readValue()")
        # terminate the process ???

        return np.array([mac_list,time_list])




