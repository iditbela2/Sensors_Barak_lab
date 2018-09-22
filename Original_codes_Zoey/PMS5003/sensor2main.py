#---------------------------------#
# filename: sensor2main.py        #
# author: Zhiye (Zoey) Song       #
#---------------------------------#
import subprocess
import datetime
import os
import sys
import time
import sensorPMS5003#
import dropbox
dbx=dropbox.Dropbox('WOPNUZO-UIAAAAAAAAAACYgjS_zDgTy9g0xuHm08BFrC251BAW05ZNspRn3VdTKi')

DURATION = 5 #in minutes
DEBUG = False #True to also create a debug file

#hardware id
SELECTED_HARDWARE = 2 #1 for SDS021, 2 for PMS5003, 3 for SDS011
 
def doMeasurement(duration, debug):

    """function:
        This function calls one of the three sensor
        reader classes according to which station 
        was selected. It receives all values 
        of everything after 
        a measurement of a set duration of time.
        
        Then it creates a new log file and stores the data.
        It return the file name of the newly created log file.
    """
    global df
    

    print "START MEASUREMENT"
    df.write("START MEASUREMENT")
    count = 0

    #open a log file for current time
    file_name = str(datetime.datetime.now()).split(".")[0]

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
    #return file_name

def checkInternetConnection():
    
    """function:
        This function checks if there is an internet connection
        to the wifi and uploading is possible. It returns True if yes.
    """
    
    count = 0
    list=subprocess.check_output("iwconfig")
    list=list.decode("utf-8")
    copy=list
    list=list.split("\n")
    for line in list:
        if line.find("wlan0")>-1 or line.find("wlan1")>-1:
            if line[line.find("ESSID")+6]=="o":
                return False
            return True
    return False

    
def uploadToDropbox(file,id):
    f=open('/home/pi/logs/'+str(id)+'/'+file,'r')
    string=f.read()
    f.close()
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
        df=open('/home/pi/sensordebug.txt','a+')#
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
        cmd = "/home/pi/logs/{0}".format(str(SELECTED_HARDWARE))
        os.chdir(cmd)
            
        while True:

            #upload any not uploaded log
            if checkInternetConnection():
                cmd = "/home/pi/logs/{0}".format(str(SELECTED_HARDWARE))
                files = os.listdir(cmd)
                for file in files:
                    if "log_" in file:
                        print file
                        try: uploadToDropbox(file, SELECTED_HARDWARE)
                        except:
                            print "failed"
                            continue
            else:
                subprocess.check_output(("sudo ifconfig wlan0 up").split())
                subprocess.check_output(("sudo ifconfig wlan1 up").split())

            while True:

                #measurement
                try:
                    doMeasurement(DURATION, DEBUG)
                    print "done measurement"#
                    df.write("done measurement")
                except Exception as e:
                    df.write(str(sys.exc_info()))
                    df.write(str(e))
                    df.write('\n')
                    print e
                    print sys.exc_info()
                    continue
                if checkInternetConnection():
                    break
                else:
                    subprocess.check_output(("sudo ifconfig wlan0 up").split())
                    subprocess.check_output(("sudo ifconfig wlan1 up").split())

    except Exception as e:
        df.flush()
        df.write(str(sys.exc_info()))
        df.write(str(e))
        df.write('\n')
        print e
        print sys.exc_info()
        continue
