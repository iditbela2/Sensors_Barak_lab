
# written in python2

import time
import serial
import numpy as np
import datetime
import logging

class SDS021Reader:

    logging.basicConfig(
        filename='/home/pi/logs_debug/SDS021Reader_debug_{}.log'.format(datetime.datetime.now()),
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    def __init__(self, inport):
        
        #open port
        self.serial = serial.Serial(port=inport,baudrate=9600)

    def checkStart(self):
        isStart = False
        head1 = ord(self.serial.read())
        head2 = ord(self.serial.read())
        if head1 == 170 and head2 == 192:
            isStart = True
        return isStart

    def readValue(self):
        # dump old measured values not yet read (buffered)
        self.serial.flushInput()

        while self.serial.inWaiting() == 0:
            time.sleep(0.01)

        # make sure you start after first and second bits
        while not self.checkStart():
            try:
                self.serial.read()
            except Exception:
                logging.exception("Error when reading from serial, values not synced")

        #read serial input of ASCII characters as an integer
        values = [ord(self.serial.read()) for i in range(8)]#total of 10 bit
        # but only focus on 3rd to 6th DATA bits
        # low and high*265 byte / 10... according to documentation
        if sum(values[0:6])%256 == values[6]:
            pm25 = (values[0] + values[1] * 256) / float(10)
            pm10 = (values[2] + values[3] * 256) / float(10)
            aqm = [pm25, pm10]
        else:
            aqm = [0,0]
            logging.exception("Error when reading from serial, check-sum failed")
        return aqm

    def readPM(self, duration, no_outputs):
        """function:
            Read the frames for a given duration and return PM 2.5 and PM 10 concentrations'
            average, [standard deviation, min, and max] PER MINUTE
        """
        result = np.zeros((duration, no_outputs)) #initialize the result file. 2 suits SDS, 12(?) is for 5003
        # make sure you start measuring in a round minute
        while datetime.datetime.now().minute%duration != 0:
            time.sleep(0.1) #in seconds.
        #logging.info("started reading PM data")
        for step in range(duration):
            temp = []
            start_time = datetime.datetime.now().replace(microsecond=0,second=0)
            step_time = datetime.timedelta(hours=0, minutes=1)  # step time. 1 min. of average
            while datetime.datetime.now() < start_time + step_time:
                try:
                    temp.append(self.readValue())  #could values potentialy be empty/zero ?
                except Exception:
                    logging.exception("error in reading PM values using readValue()")
            result[step,:] = np.mean(temp,0) #return mean of 1 minutes readings
        return result