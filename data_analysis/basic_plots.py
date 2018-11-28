
# First measurements of both sensors
# import relevant modules

import data_analysis.DA_functions as da
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as md

# set path and choose time of measurement

dataPath = '/Users/iditbela/Dropbox/'
start_date = datetime.datetime(2018, 9, 26, 0, 0, 0)
end_date = datetime.datetime(2018, 10, 2, 0, 0, 0)
duration = 10 # measurement duration




# SENSOR-1-SDS021

sensor_no = 1
output_no = 2
times_1, data_1 = da.getSignalData(dataPath, sensor_no,start_date, end_date, duration, output_no)

# plot signal SENSOR-1-SDS021
%config InlineBackend.figure_format = 'retina'
plt.style.use('ggplot')

fmt = "%Y-%m-%d %H:%M:%S"
fig, ax = plt.subplots()
ax.plot(times_1, data_1[:,0])
ax.plot(times_1,data_1[:,1])
ax.set_ylim(0,80)
ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
ax.legend(('PM 2.5','PM 10'),loc='upper right')
plt.title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_1[0].strftime(fmt)+' \nand '+ (times_1[len(times_1)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
plt.ylabel(r'$\mu g/m^3$',labelpad=16)
# Tell matplotlib to interpret the x-axis values as dates
ax.xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 20
plt.show();

plt.close('all')
plt.rcParams.update(plt.rcParamsDefault)






# SENSOR-2-PMS5003

sensor_no = 2
output_no = 12
times_2, data_2 = da.getSignalData(dataPath, sensor_no,start_date, end_date, duration, output_no)

# plot signal SENSOR-2-PMS5003
%config InlineBackend.figure_format = 'retina'
plt.style.use('ggplot')

fmt = "%Y-%m-%d %H:%M:%S"
fig, ax = plt.subplots(nrows=1, ncols=2)
fig.subplots_adjust(hspace=0.1, wspace=0.3)

# plot PM
for i in range(6):
    ax[0].plot(times_2, data_2[:,i])
ax[0].xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
# plot concentration
ax[0].legend(('pm1', 'pm2.5', 'pm10', 'pm1atm', 'pm2.5atm', 'pm10atm'),loc='upper right')
# plt.title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_2[0].strftime(fmt)+' and '+ (times_2[len(times_2)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
ax[0].set_title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_2[0].strftime(fmt)+' \nand '+ (times_2[len(times_2)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
ax[0].set_ylabel(r'$\mu g/m^3$',labelpad=16)
# Tell matplotlib to interpret the x-axis values as dates
ax[0].xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()

# plot No. of particles
for i in range(3):
    ax[1].plot(times_2, data_2[:,6+i])
ax[1].xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
# plot concentration
ax[1].legend(('beyond 0.3', 'beyond 0.5', 'beyond 1.0'),loc='upper right')
# plt.title('PM concentration\n measured by sensor '+str(sensor_no)+'\nbetween '+times_2[0].strftime(fmt)+' and '+ (times_2[len(times_2)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
ax[1].set_title('Number of particles with diameter\n beyond X '+ r'$\mu m$ ' + 'in 0.1 L of air\n' + 'measured by sensor ' +str(sensor_no)+'\nbetween '+times_2[0].strftime(fmt)+' \nand '+ (times_2[len(times_2)-1]+datetime.timedelta(hours=0, minutes=1)).strftime(fmt))
ax[1].set_ylabel('No. of particles',labelpad=16)
# Tell matplotlib to interpret the x-axis values as dates
ax[1].xaxis_date()
# Make space for and rotate the x-axis tick labels
fig.autofmt_xdate()

plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 16
plt.show();

plt.close('all')
plt.rcParams.update(plt.rcParamsDefault)

