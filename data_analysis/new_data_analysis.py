
# BACKUP OF JUPYTER NOTEBOOK

# import relevant modules
import data_analysis.DA_functions as da
import numpy as np
import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as md


# set path and choose time of measurement
dataPath = '/Users/iditbela/Dropbox/'
start_date = datetime.datetime(2018, 9, 26, 0, 0, 0)
end_date = datetime.datetime(2018, 10, 2, 10, 0, 0)
duration = 10 # measurement duration

# SENSOR-1-SDS021
sensor_no = 1
output_no = 2
times_chosen, times_log = da.getTimes(dataPath,sensor_no,start_date,end_date,log = 'data')
times_1, data_1 = da.getSignalData(dataPath, sensor_no,start_date, end_date, duration, output_no)

# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"

#times_1
#data_1

#%matplotlib notebook
# plot signal SENSOR-1-SDS021
fmt = "%Y-%m-%d %H:%M:%S"
#plt.style.use('ggplot')
fig, ax = plt.subplots()
ax.plot(times_1, data_1[:,0])
ax.plot(times_1,data_1[:,1])
ax.set_ylim(0,80)
ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
ax.legend(('PM 2.5','PM 10'),loc='upper right')
plt.title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_1[0].strftime(fmt)+' and '+ (times_1[len(times_1)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
plt.ylabel(r'$\mu g/m^3$',labelpad=16)
# Tell matplotlib to interpret the x-axis values as dates
ax.xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 20


plt.close('all')
plt.rcParams.update(plt.rcParamsDefault)


# SENSOR-2-PMS5003
sensor_no = 2
output_no = 12
times_chosen, times_log = da.getTimes(dataPath,sensor_no,start_date,end_date,log = 'data')
times_2, data_2 = da.getSignalData(dataPath, sensor_no,start_date, end_date, duration, output_no)


%matplotlib notebook
# plot signal SENSOR-2-PMS5003
fmt = "%Y-%m-%d %H:%M:%S"
#plt.style.use('ggplot')
fig, ax = plt.subplots()
for i in range(6):
    ax.plot(times_2, data_2[:,i])
ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
# plot concentration
ax.legend(('pm1', 'pm2.5', 'pm10', 'pm1atm', 'pm2.5atm', 'pm10atm'),loc='upper right')
plt.title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_2[0].strftime(fmt)+' and '+ (times_2[len(times_2)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
plt.ylabel(r'$\mu g/m^3$',labelpad=16)
# Tell matplotlib to interpret the x-axis values as dates
ax.xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 20














# SENSOR-1-SDS021
sensor_no = 1
start_date = datetime.datetime(2018, 9, 26, 0, 0, 0)
end_date = datetime.datetime(2018, 10, 2, 0, 0, 0)
duration = 10 # measurement duration
output_no = 2
dataPath = '/Users/iditbela/Dropbox/'

times_chosen, times_log = getTimes(dataPath,sensor_no,start_date,end_date,log = 'data')



#------ plot some results ------


# extract data1 to plot a simple signal
sensor_no = 1
times_i, data_i = getSignalData(dataPath, sensor_no, start_date, end_date)

# export data1 to CSV
fmt = "%Y-%m-%d %H:%M:%S"
exportToCSV(start_date, end_date, fmt, times, data, sensor_no)

# extract data2 to csv
sensor_no = 2
times2, data2 = getSignalData(dataPath, sensor_no, start_date, end_date)

# export data2 to csv
exportToCSV(start_date, end_date, fmt, times2, data2, sensor_no)


# plot signal
fmt = "%Y-%m-%d %H:%M:%S"
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

# check data
ind = np.where(data_i[:,0]>50)
ind[0][1:] - ind[0][:-1]

# plot histogram of data
plt.hist(data[:,0],bins = 100)
plt.show()


# extract data to plot per mac address
macAdd = '186590b30ae4' #lets say this is my mac address
# run over all sensors and extract this data
myMacData = np.empty((1,3))
sensors = [1,5]
for s in sensors:
    folder = dataPath+'wifi'+str(s)
    if is_folder_exists(folder) and not is_folder_empty(folder):
        myMacData = np.vstack((myMacData,getSignalPerMacAddress(dataPath,s,start_date,end_date,macAdd)))








