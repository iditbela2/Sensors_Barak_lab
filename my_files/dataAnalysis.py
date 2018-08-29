
import matplotlib.pyplot as plt
import datetime
import os
import numpy as np
import time
import dropbox

# Make sure data was manually downloaded

# the name of the file should represent the time at the end of the measurement, so use linespace with
# the number of values to add x-time array

sensor_no = 1
start_date = datetime.datetime(2018,8,1,0,0,0)
end_date = datetime.datetime(2018,8,2,0,0,0)
duration = 5 # measurement duration
dataPath = '/Users/iditbela/Documents/Sensors_Barak_lab/downloaded_data/'


# find the log files that match the chosen dates and create data array of time intervals
# and measurements. each measurement represents one minute so the time of the log-file is the end of
# measurement and I go the number of required minutes back

def getData(sensor, start, end):
    file_names = np.array(os.listdir(dataPath+str(sensor)))
    times_str = np.array([ind[4:] for ind in file_names])
    fmt = "%Y-%m-%d %H:%M:%S"
    times_datetime = np.array([datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))])
    chosen_datetimes = times_datetime[(times_datetime >= start_date) & (times_datetime <= end_date)]
    chosen_logs =









    import time, glob

    outfilename = 'all_' + str((int(time.time()))) + ".txt"

    filenames = glob.glob('*.txt')

    with open(outfilename, 'wb') as outfile:
        for fname in filenames:
            with open(fname, 'r') as readfile:
                infile = readfile.read()
                for line in infile:
                    outfile.write(line)
                outfile.write("\n\n")




    path = r'C:\Users\Data1\\'
    times = []
    yvals = []
    for data_file in sorted(os.listdir(path)):
        with open(data_file, 'r') as f:
            for line in f.readlines()[11:21]:  # read lines from 11 to 21
                column = line.split('\t')
                times.append(column[0])
                yvals.append(column[1])




# convert all name of files to time and then concat to one file / build an array based on start and end











# import dropbox
# import urllib.request
#
# dbx=dropbox.Dropbox('WOPNUZO-UIAAAAAAAAAACYgjS_zDgTy9g0xuHm08BFrC251BAW05ZNspRn3VdTKi')
# filePath = 'https://www.dropbox.com/preview/Apps/Sensor%20Network%20Uploading%20Section/1/log_2018-08-02%2011%3A00%3A00?role=personal/'
# dbx.files_download(filePath, rev=None)
#
# result = dbx.files_get_temporary_link(filePath)
#
# response = dbx.files_list_folder(path='https://www.dropbox.com/sh/vj45xs1o6gmfsgj/AADWSpFEoRaN60QSWX1AAsBya?dl=1')
#
#
# URL = "https://www.dropbox.com/sh/vj45xs1o6gmfsgj/AADWSpFEoRaN60QSWX1AAsBya?dl=0"
# globalData = urllib.request.urlretrieve(filePath, "/Users/iditbela/Documents/Sensors_Barak_lab/my_files/")
#
# def downloadFromDropbox(file,id):
#     f=open('/home/pi/logs/1/')
#     string=f.read()
#     f.close()
#     a=dbx.files_upload(string,'/'+str(id)+'/'+file)
#     #move the file tto uploaded logs
#     file = "'" + file + "'"
#     cmd = "sudo mv {0} /home/pi/logs/{1}/uploaded_logs/".format(file, str(id))
#     os.system(cmd)
#     return a

