#---------------------------------#
# filename: sensorSDS021.py       #
# author: Zhiye (Zoey) Song       #
# changes by: Idit Belachsen      #
#---------------------------------#
# written in python2
import os
import sys
import time
import serial
import numpy as np
import datetime
import logging

class SDS021Reader:

    logging.basicConfig(
        filename='/home/pi/SDS021Reader_debug_{}.log'.format(datetime.datetime.now()),
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    def __init__(self, inport):
        
        #open port
        self.serial = serial.Serial(port=inport,baudrate=9600)

    # NOTE (Idit): understand what happens when inWaiting is 4095 (max). will it keep reading and
    # replace the old values by the new ones? or will I get old values when I read ?
    # maybe I need to start by dumping all the "old values"?
    def readValue(self):
        """function:
            Read and return a frame with length of 8 from the serial port
        """
        # dump old measured values not yet read
        while self.serial.inWaiting() != 0:
            [ord(self.serial.read()) for i in range(10)]

        while True:
            while self.serial.inWaiting() == 0:
                time.sleep(0.01)
            #read serial input of ASCII characters as an integer
            values = [ord(self.serial.read()) for i in range(10)]#total of 10 bit
            # but only focus on 3rd to 6th DATA bits
            # low and high*265 byte / 10... according to documentation
            pm25 = (values[2] + values[3] * 256) / float(10)
            pm10 = (values[4] + values[5] * 256) / float(10)
            return [pm25, pm10]
                
    def read(self, duration):
        """function:
            Read the frames for a given duration and return PM 2.5 and PM 10 concentrations'
            average, [standard deviation, min, and max] PER MINUTE
            NOTE (Idit): filename for debug should be initialized here since you only start reading
            when you get to round minute according to duration!
        """
        result = np.empty((duration, 2)) #initialize the result file. 2 suits SDS, 12(?) is for 5003
        # make sure you start measuring in a round minute.
        while(int(datetime.datetime.now().minute)%duration!=0):
            time.sleep(1) #in seconds.
        logging.info("started reading")
        #file_name = "debug_" + str(datetime.datetime.now()).split(".")[0]
        for step in range(duration):
            temp = []
            while(int(datetime.datetime.now().minute)%duration==step):
                try:
                    temp.append(self.readValue())
                except Exception:
                    logging.exception("error in reading values using readValue()")
            result[step,:]=np.mean(temp,0) #return mean of 1 minutes readings
        return result