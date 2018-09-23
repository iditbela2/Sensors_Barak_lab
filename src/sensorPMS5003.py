
# written in python2

import time
import serial
import numpy as np
import datetime
import logging

class PMS5003Reader:

    logging.basicConfig(
        filename='/home/pi/logs_debug/PMS5003Reader_debug_{}.log'.format(datetime.datetime.now()),
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

    def __init__(self, inport):
        
        #open port
        self.serial = serial.Serial(port=inport,baudrate=9600)

    def checkStart(self):
        isStart = False
        head1 = ord(self.serial.read())
        head2 = ord(self.serial.read())
        if head1 == 66 and head2 == 77:
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
        values = [ord(self.serial.read()) for i in range(30)]
        if 66 + 77 + sum(values[0:28]) == values[28]*256 + values[29]:
            pm1 = (values[2]*256 + values[3])
            pm25 = (values[4]*256 + values[5])
            pm10 = (values[6]*256 + values[7])
            pm1atm = (values[8]*256 + values[9])
            pm25atm = (values[10]*256 + values[11])
            pm10atm = (values[12]*256 + values[13])
            no03 = (values[14]*256 + values[15])
            no05 = (values[16]*256 + values[17])
            no1 = (values[18]*256 + values[19])
            no25 = (values[20]*256 + values[21])
            no5 = (values[22]*256 + values[23])
            no10 = (values[24]*256 + values[25])
            aqm = [pm1, pm25, pm10, pm1atm, pm25atm, pm10atm, no03, no05, no1, no25, no5, no10]
        else:
            aqm = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            logging.exception("Error when reading from serial, check-sum failed")
        return aqm

    def readPM(self, duration, no_outputs):
        result = np.zeros((duration, no_outputs)) #initialize the result file. 2 suits SDS, 12(?) is for 5003
        # make sure you start measuring in a round minute
        while datetime.datetime.now().minute%duration != 0:
            time.sleep(0.1) #in seconds.
        logging.info("starting to read PM data")
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