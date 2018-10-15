
# SENSOR-1-SDS021
sensor_no = 1
start_date = datetime.datetime(2018, 9, 26, 0, 0, 0)
end_date = datetime.datetime(2018, 10, 2, 10, 0, 0)
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








