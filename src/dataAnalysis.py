
# written in python3
# I miss ismember, accumarray, cellfunc :)

import datetime
import os
import numpy as np
import time
import dropbox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import operator
from functools import reduce
from pathlib import Path
import csv

def is_folder_exists(folder):
    return os.path.isdir(folder)

def is_folder_empty(folder):
    return os.listdir(folder) == []

# find the log files that match the chosen dates and create data array of time intervals
# and measurements. each measurement represents one minute so the time of the log-file is the end of
# measurement and I get the number of required minutes back

# get an array of the log times chosen (times_chosen = datetime, times_log=strings of that time)
def getTimes(path, sensor, start, end, log): # log=data for PM data or log=wifi for macAdress data
    fmt = "%Y-%m-%d %H:%M:%S"
    if log=='data':
        logPath = path+str(sensor)
        file_names = np.array(os.listdir(logPath))
        # extract times from file names
        times_str = np.array([ind[4:] for ind in file_names])
        # convert to datetime
        times_datetime = np.array([datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))])
        # choose the times between start and end
        times_chosen = times_datetime[(times_datetime >= start) & (times_datetime <= end)]
        # choose the relevant logs
        times_log = np.array(['log_' + x.strftime(fmt) for x in times_chosen])
    elif log=='wifi':
        logPath = path+'wifi'+str(sensor)
        file_names = np.array(os.listdir(logPath))
        # extract times from file names
        times_str = np.array([ind[5:] for ind in file_names])
        # convert to datetime
        times_datetime = np.array([datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))])
        # choose the times between start and end
        times_chosen = times_datetime[(times_datetime >= start) & (times_datetime <= end)]
        # choose the relevant logs
        times_log = np.array(['wifi_' + x.strftime(fmt) for x in times_chosen])
    else:
        raise ValueError("log must be 'data' or 'wifi'" )
    return times_chosen, times_log

def getSignalData(path, sensor, start, end):
    times_chosen, times_log = getTimes(path,sensor,start,end,log = 'data')
    # extract all data from chosen logs
    all_data = []
    for ind in range(len(times_log)):
        with open(path+str(sensor)+'/'+times_log[ind]) as f:
            fdata = f.read().splitlines()
            all_data.append(fdata)
    # reorganize the data to numpy array, depending on the shape of the datafile
    num_splits = len([word for word in all_data[0] if word.startswith('--END OF')])
    shape_data = np.shape(all_data)
    times_size = int((shape_data[1] - num_splits) / num_splits)
    # create an array of measurement times
    times = []
    for t in times_chosen:
        for i in range(times_size,0,-1):
            times.append(t - datetime.timedelta(hours=0, minutes=i))
# I SHOULD UNDERSTAND HOW THE DATA IS WRITTEN IN THE FILES....MAYBE THE LOOP IS BACKWARDS
    # create an array of data
    data = np.zeros([times_size*shape_data[0],num_splits])
    temp = np.transpose(all_data)
    for i in range(num_splits):
        ind = np.where(temp == "--END OF " + str(i + 1) + "--")[0][0]
        data[:,i] = np.reshape(temp[ind-times_size:ind, :], (times_size*shape_data[0],))
    # return an array of times and an array of data measurements
    return np.array(times), data

# getMacAddresses returns a matrix of times and mac addresses per certain sensor.
# Since several addresses exist per one time of log, I should have multiple
# identical time values (one for each mac address).
# time of log is taken (representing time between log_time-duration and log_time)
def getMacAddresses(path, sensor, start, end):
    times_chosen, times_log = getTimes(path,sensor,start,end,log='wifi')
    # extract all mac addresses from chosen logs
    all_mac_data = []
    for ind in range(len(times_log)):
        with open(path+'wifi'+str(sensor)+'/'+times_log[ind]) as f:
            fdata = f.read().splitlines()
            all_mac_data.append(fdata[:-1]) # remove the "---END OF..."
    # create an array of times in the size of time_size X all_mac_data[i]
    times_size = np.shape(all_mac_data)[0] #size according to number of logs
    len_mac = [] #array of len of mac addresses in each log
    for d in all_mac_data:
        len_mac.append(len(d))
    # create an array of measurement times minus 5 minutes.
    # that way the time represents the beginning
    # of the measurement and not the end
    times = [] #HOW DO I DO IT NOT IN A LOOP?
    for i in range(times_size):
        for j in range(len_mac[i]):
            times.append(times_chosen[i] - datetime.timedelta(hours=0, minutes=5))
    # create an array of data the same size
    data = np.array(reduce(operator.concat, all_mac_data))
    # return an array of times and an array of data measurements
    return np.array(times), data

# find all times a specific mac address was measured in a certain sensor.
# then, get signal for those times
# How do I do it with no ismember? :)
def getSignalPerMacAddress(path, sensor, start, end, macAdd):
    # call getMacAddresses
    times, macs = getMacAddresses(path, sensor, start, end)
    # take only data per specific mac address
    find = np.where(macs == macAdd)
    result = np.transpose(np.array([times[find],macs[find],np.ones(np.shape(times[find]))*int(sensor)]))
    return result


def exportToCSV(start, end, fmt, times, data, sensor_no):
    # write data to csv file
    filename = "s_" + str(sensor_no) + "_from_" + start.strftime(fmt) + "_to_" + end.strftime(fmt) + ".csv"

    with open(filename, 'a') as csvFile:
        writer = csv.writer(csvFile)
        if sensor_no is 1:
            writer.writerow(['time', 'PM 2.5', 'PM 10'])
            for t, d in zip(times, data):
                row = [t.strftime(fmt), str(d[0]), str(d[1])]
                writer.writerow(row)
        if sensor_no is 2:
            writer.writerow(['time', 'pm1', 'pm2.5', 'pm10', 'pm1atm', 'pm2.5atm', 'pm10atm', 'no03', 'no05', 'no1', 'no25', 'no5', 'no10'])
            for t, d in zip(times, data):
                row = [t.strftime(fmt)] + [str(d[i]) for i in range(np.shape(d)[0])]
                writer.writerow(row)
    csvFile.close()

#------ plot some results ------

# Make sure data was manually downloaded/take from dropbox folder
start_date = datetime.datetime(2018,9,25,0,0,0)
end_date = datetime.datetime(2018,10,2,10,0,0)
duration = 10 # measurement duration. maybe I don't need
dataPath = '/Users/iditbela/Dropbox/'

# extract data1 to plot a simple signal
sensor_no = 1
times, data = getSignalData(dataPath, sensor_no, start_date, end_date)

# export data1 to CSV
fmt = "%Y-%m-%d %H:%M:%S"
exportToCSV(start_date, end_date, fmt, times, data, sensor_no)

# extract data2 to csv
sensor_no = 2
times2, data2 = getSignalData(dataPath, sensor_no, start_date, end_date)

# export data2 to csv
exportToCSV(start_date, end_date, fmt, times2, data2, sensor_no)


# plot signal
fig, ax = plt.subplots()
ax.plot(times, data[:,0])
ax.plot(times,data[:,1])
ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
ax.legend(('PM 2.5','PM 10'),loc='upper right')
plt.title('PM concentration measured by\n sensor '+str(sensor_no)+' between\n '+times[0].strftime(fmt)+' and '+times[len(times)-1].strftime(fmt))
plt.ylabel('micro-grams/m^3')
# Tell matplotlib to interpret the x-axis values as dates
#ax.xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()

plt.show()
#plt.savefig('plot.pdf')


# extract data to plot per mac address
macAdd = '186590b30ae4' #lets say this is my mac address
# run over all sensors and extract this data
myMacData = np.empty((1,3))
sensors = [1,5]
for s in sensors:
    folder = dataPath+'wifi'+str(s)
    if is_folder_exists(folder) and not is_folder_empty(folder):
        myMacData = np.vstack((myMacData,getSignalPerMacAddress(dataPath,s,start_date,end_date,macAdd)))













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
# globalData = urllib.request.urlretrieve(filePath, "/Users/iditbela/Documents/Sensors_Barak_lab/src/")
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

