#---------------------------------#
# filename: wifi2main.py          #
# author: Zhiye (Zoey) Song       #
#---------------------------------#
'''
to modify: all values in sensor file
log files separated for sensor and mac
'''
import subprocess
import datetime
import os
import sys
import time
import dropbox
dbx=dropbox.Dropbox('WOPNUZO-UIAAAAAAAAAACYgjS_zDgTy9g0xuHm08BFrC251BAW05ZNspRn3VdTKi')
mac_list=["6470332cfd5a\n","0056cd350b8f\n","3c15c2bb4720\n"]
DURATION = 30
DEBUG = True #True to also create a debug file

#hardware id
SELECTED_HARDWARE = 2 #1 for SDS021, 2 for PMS5003, 3 for SDS011

def detectDevices(duration):
    global df
    global mac_list
    """function:
        This function detects nearby Wi-Fi enabled devices
        and saves their MAC address and time stamps in the log file newly created.
    """


    
    #while(int(str(datetime.datetime.now()).split(":")[1])%duration!=):
        #time.sleep(1)
    start_time=int(str(datetime.datetime.now()).split(":")[1])
    
    print "START DETECTION"
    df.write("START DETECTION\n")
    
    file_name = "test_"+str(datetime.datetime.now()).split(".")[0]
    f = open(file_name,"w")
    #initialization
    splited_line = []
    time_list = []
    start_append = 0
    exp=0

    
    #command line configuration
    #only display source, and destinaiton of the packet


    cmd = ("sudo tshark -l -i mon0 -o column.format:"+'"src","%uhs","dst","%uhd"').split()

    #execute the command
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    #for every output line
    for line in iter(process.stdout.readline, ""):
##        list=list.decode("utf-8")
##        print line
        

        #acquire data for set duration of time    
        if int(str(datetime.datetime.now()).split(":")[1])%duration==0 and int(str(datetime.datetime.now()).split(":")[1])!=start_time:
            process.terminate()
            break

        #start writing to the file when a MAC address is read    
        if start_append == 0:
            if "Capturing on" in str(line):
                start_append = 1
                continue
            else:
                df.write(str(line)+"\n")
            
        splited_line = line.split(" ")
        
        for mac in splited_line:

            if "\n" not in mac:
                mac = mac + "\n"
            
            #check if it is a valid MAC address
            if ("ff:ff:ff:ff:ff:ff" not in mac) and (len(mac) == 18):

                #write the address to file if it was not detected before
                mac=mac.replace(":","")
                
                if mac in mac_list:
                    mac=str(datetime.datetime.now()).split(".")[0]+" "+mac
                    if mac not in time_list:
                        time_list.append(mac)
                        f.write(mac)
                    #print mac
                #f.write(mac)#
    if int(str(datetime.datetime.now()).split(":")[1])%duration!=0:
        print "pipe closed"
        df.write("pipe closed\n")
        df.write(str(line)+"\n")
        subprocess.check_output(("sudo airmon-ng start mon0").split())
        exp=1
    df.write(subprocess.check_output("free -m".split()))
    f.write("---END OF MAC ADDRESSES---")        
    f.close()
    process.terminate()
    if exp==1:
        raise Exception('pipe closed')
    return

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
    f=open('/home/pi/logs/test'+str(id)+'/'+file,'r')
    string=f.read()
    f.close()
    a=dbx.files_upload(string,'/test'+str(id)+'/'+file)
    #move the file to uploaded logs
    file = "'" + file + "'"
    cmd = "sudo mv {0} /home/pi/logs/{1}/uploaded_logs/".format(file, 'test'+str(id))
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
        df=open('/home/pi/testdebug.txt','a+')#
        #check if there is a log folder; if not, create a new one
        cmd = "/home/pi"
        files = os.listdir(cmd)
        if "logs" not in files:
            cmd = "sudo mkdir logs"
            os.system(cmd)

        #check if there is a folder for a selected hardware; if not, create a new one
        cmd = "/home/pi/logs"
        files = os.listdir(cmd)
        if 'test'+str(SELECTED_HARDWARE) not in files:
            cmd = "sudo mkdir -p logs/{0}/uploaded_logs".format('test'+str(SELECTED_HARDWARE))
            os.system(cmd)

        #set working directory
        cmd = "/home/pi/logs/{0}".format('test'+str(SELECTED_HARDWARE))
        os.chdir(cmd)
            
        while True:

            #upload any not uploaded log
            if checkInternetConnection():
                cmd = "/home/pi/logs/{0}".format('test'+str(SELECTED_HARDWARE))
                files = os.listdir(cmd)
                for file in files:
                    if "test_" in file:
                        print file
                        df.write(file+"\n")
                        try: uploadToDropbox(file, SELECTED_HARDWARE)
                        except Exception as e:
                            print "failed"
                            print e
                            df.write(str(e))
                            df.write("failed\n")
                            continue
            else:
                subprocess.check_output(("sudo ifconfig wlan0 up").split())
                subprocess.check_output(("sudo ifconfig wlan1 up").split())

            while True:

                #measurement
                upload_info = detectDevices(DURATION)
                #time.sleep(300)

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
