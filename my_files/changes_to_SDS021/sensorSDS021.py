#---------------------------------#
# filename: sensorSDS021.py       #
# author: Zhiye (Zoey) Song       #
#---------------------------------#

import os
import sys
import time
import serial
import numpy as np
import datetime

class SDS021Reader:

    def __init__(self, inport):
        
        #open port
        self.serial = serial.Serial(port=inport,baudrate=9600)

    def readValue(self): 
        """function:
            Read and return a frame with length of 8 from the serial port
        """
        
        step = 0
        
        while True:
            
            while self.serial.inWaiting() != 0:
                
                #read serial input of ASCII characters as an integer
                v = ord(self.serial.read()) 
        
                #total of 10 bit but only focus on 3rd to 6th DATA bits
                if step == 0:
                    #first bit is always 170
                    if v == 170:
                        values = [0,0,0,0,0,0,0]#2...8; pm2.5 low byte...checksum
                        step = 1
                
                elif step == 1:
                    #second bit is always 192
                    if v == 192:
                        step = 2
                    else:
                        step = 0

                elif step > 8:
                    if v==171 and values[6]==(values[0]+values[1]+values[2]+values[3]+values[4]+values[5])%256:
                        step = 0
                        #low and high*265 byte / 10... according to documentation
                        pm25 = (values[0] + values[1]*256)/float(10)
                        pm10 = (values[2] + values[3]*256)/float(10)
                        return [pm25,pm10]
                
                #start DATA bit acquisition
                elif step >= 2:
                    if v == 170: #on 4th measurement 170, 192 repeats #NOT CLEAR
                        step = 1
                        continue
                    values[step-2] = v 
                    step += 1
                
    def read(self, duration, file_name, debug):
        """function:
            Read the frames for a given duration and return PM 2.5 and PM 10 concentrations'
            average, standard deviation, min, and max
        """
        while(int(datetime.datetime.now().minute)%duration!=0):
            time.sleep(1)
        print "read"#
        #initialization
        

        result = [[] for i in range(duration)]
        file_name = "debug_" + file_name
        for j in range(duration):
            species = [[] for i in range(2)]
            while (int(datetime.datetime.now().minute)%duration<(j+1)) and ((j!=duration-1) or (int(datetime.datetime.now().minute)%duration!=0)):
                try:
                    values = self.readValue()
                    
                    #pm2.5
                    species[0].append(values[0])
                    #pm10
                    species[1].append(values[1])
                    
                    
                    time.sleep(1) #WHY???
    
                except KeyboardInterrupt:
                    print "keyboard interrupt"
                    sys.exit()
                except:
                    e = sys.exc_info()[0]
                    print ("ERROR: " + str(e))
    
            #create debug file
            if debug:
                
                f = open(file_name,"a+")
                for pm in range(2):
                    for value in species[pm]:
                        f.write(str(value) + "\n")
                    f.write("-------------\n")
                f.close()
            
            for i in range(len(species)):
                result[j-1].append(np.average(species[i]))
                '''
                result.append(np.std(species[i]))
                result.append(min(species[i]))
                result.append(max(species[i]))
                '''
            print "finish"+str(j)#
        return result
