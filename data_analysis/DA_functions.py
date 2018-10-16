
# written in python3

import datetime
import os
import numpy as np
import operator
from functools import reduce
import csv
# from pathlib import Path
# import time
# import dropbox
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as md

'''
getTimes finds the log files that match the chosen dates and returns an array of 
log times chosen (times_chosen = datetime, times_log=strings of that time). It acts
differently for data logs and wifi logs
'''


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
        times_str = np.array([ind[5:] for ind in file_names if 'wifi' in ind])
        # convert to datetime
        times_datetime = np.array([datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))])
        # choose the times between start and end
        times_chosen = times_datetime[(times_datetime >= start) & (times_datetime <= end)]
        # choose the relevant logs
        times_log = np.array(['wifi_' + x.strftime(fmt) for x in times_chosen])
    else:
        raise ValueError("log must be 'data' or 'wifi'" )
    return times_chosen, times_log


'''
getSignalData returns an array of times of measurement (every minute)
and array of the data averaged (during the measurement) per this minute. 
The time of the log-file is the END of measurement that took X minutes duration. 
'''


def getSignalData(path, sensor, start, end, duration, output_no):
    times_chosen, times_log = getTimes(path,sensor,start,end,log = 'data')
    # create an array of measurement times
    times = []
    for t in times_chosen:
        for i in range(duration, 0, -1):
            times.append(t - datetime.timedelta(hours=0, minutes=i))
    # extract all data from chosen logs
    all_data = []
    for i in range(len(times_log)):
        data = np.zeros((duration, output_no), dtype=float)
        filename = path + str(sensor) + '/' + times_log[i]
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            [lines.remove("--END OF " + str(n + 1) + "--") for n in range(output_no)]
            data[:] = np.transpose(np.array_split(lines, output_no))
        f.close()
        all_data.append(data)
    # return an array of times and an array of data measurements
    return np.array(times), np.concatenate(all_data, axis=0)


'''
getMacAddresses returns a matrix of times and mac addresses per certain sensor.
A unique mac address is saved every X duration. Once received, it is saved with a timestamp.
In case it is received again during the same measurement duration, it is not saved again.

'''


def getMacAddresses(path, sensor, start, end):
    _, times_log = getTimes(path,sensor,start,end,log='wifi')
    fmt = "%Y-%m-%d %H:%M:%S"
    # extract all data from chosen logs
    all_mac_data = []
    for i in range(len(times_log)):
        filename = path + 'wifi' + str(sensor) + '/' + times_log[i]
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            lines.remove("--END OF MAC ADDRESSES--")
            lines.remove("--END OF TIMESTEMPS--")
            data = np.transpose(np.array_split(lines, 2))
        f.close()
        all_mac_data.append(data)
    # change the times from strings to datetime
    times_str = np.concatenate(all_mac_data, axis=0)[:,1]
    times = [datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))]
    # return all_mac data
    return np.array(times), np.concatenate(all_mac_data, axis=0)[:,0]

'''
getSignalPerMacAddress finds all times a specific mac address was measured in
a certain sensor between a certain time interval. 

CHANGE THIS FUNCTION TO RETURN THE MEASURED PM DATA
ROUND TO MINUTES, AND TAKE VALUE PER THAT MINUTE. 
INTERPOLATION IS POSSIBLE LATER
'''


def getSignalPerMacAddress(path, sensor, start, end, macAdd, output_no, duration):
    fmt = "%Y-%m-%d %H:%M:%S"
    # call getMacAddresses
    times, macs = getMacAddresses(path, sensor, start, end)
    # take only data per specific mac address
    find = np.where(macs == macAdd.lower())
    mac_data_time_round = np.array([times[find][i].replace(microsecond=0, second=0) for i in range(len(times[find]))])
    # get the data of these times
    pm_data_time, pm_data = getSignalData(path, sensor, start, end, duration, output_no)
    # find the indexes in pm_data_time that match mac_time_data_round (assuming both arrays are sorted)
    ind = np.searchsorted(pm_data_time,mac_data_time_round)
    # return n
    result = np.column_stack((mac_data_time_round, macs[find], np.ones(np.shape(times[find])) * int(sensor), pm_data[ind,:]))
    return result

'''
exportToCSV writes extracted data to csv file according to the sensor type
'''
def exportToCSV(start, end, fmt, times, data, sensor_no):
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


def is_folder_exists(folder):
    return os.path.isdir(folder)


def is_folder_empty(folder):
    return os.listdir(folder) == []


