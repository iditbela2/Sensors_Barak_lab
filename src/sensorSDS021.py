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
        while True:
            [ord(self.serial.read()) for i in range(10)] # will this dump everything?
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
        result = np.empty((duration, 2)) #initialize the result file
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
            result[step,:]=np.mean(temp,0)
        return result

        #     #initialization
        # result = [[] for i in range(duration)]
        # file_name = "debug_" + file_name
        # for j in range(duration):
        #     species = [[] for i in range(2)]
        #     while (int(datetime.datetime.now().minute)%duration<(j+1)) and ((j!=duration-1) or (int(datetime.datetime.now().minute)%duration!=0)):
        #         try:
        #             values = self.readValue()
        #
        #             #pm2.5
        #             species[0].append(values[0])
        #             #pm10
        #             species[1].append(values[1])
        #
        #
        #             time.sleep(1) #WHY???
        #
        #         except KeyboardInterrupt:
        #             print "keyboard interrupt"
        #             sys.exit()
        #         except:
        #             e = sys.exc_info()[0]
        #             print ("ERROR: " + str(e))
        #
        #     #create debug file
        # if debug:
        #
        #     f = open(file_name,"a+")
        #     for pm in range(2):
        #         for value in species[pm]:
        #             f.write(str(value) + "\n")
        #         f.write("-------------\n")
        #     f.close()
        #
        # for i in range(len(species)):
        #     result[j-1].append(np.average(species[i]))
        #     '''
        #     result.append(np.std(species[i]))
        #     result.append(min(species[i]))
        #     result.append(max(species[i]))
        #     '''
        # print "finish"+str(j)#
        # return result
