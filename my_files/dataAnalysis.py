
# im missing ismember, accumarray, cellfunc

import datetime
import os
import numpy as np
import time
import dropbox
import pandas as pd

# find the log files that match the chosen dates and create data array of time intervals
# and measurements. each measurement represents one minute so the time of the log-file is the end of
# measurement and I get the number of required minutes back

def getData(path,sensor, start, end):
    file_names = np.array(os.listdir(path+str(sensor)))
    # extract times from file names
    times_str = np.array([ind[4:] for ind in file_names])
    fmt = "%Y-%m-%d %H:%M:%S"
    # convert to datetime
    times_datetime = np.array([datetime.datetime.strptime(times_str[x], fmt) for x in range(len(times_str))])
    # choose the times between start and end
    times_chosen = times_datetime[(times_datetime >= start) & (times_datetime <= end)]
    # choose the relevant logs
    times_log = np.array(['log_'+x.strftime(fmt) for x in times_chosen])
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

            # # run over the file and split where I have "END OF"
            # for i in num_splits
            #     ind = data.index("--END OF "+str(i)+"--")
            #     all_data[:ind,.append(data)

    # return an array of times and an array of data measurements
    return np.array(times), data


#getDataForAMacAdress()


# Make sure data was manually downloaded
sensor_no = 1
start_date = datetime.datetime(2018,8,1,0,0,0)
end_date = datetime.datetime(2018,8,2,0,0,0)
duration = 5 # measurement duration. maybe I don't need
dataPath = '/Users/iditbela/Documents/Sensors_Barak_lab/downloaded_data/'

# extract data
times, data = getData(dataPath,1,start_date,end_date)

# plot signal
import matplotlib.pyplot as plt


plt.plot(times, data)
plt.show()




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

