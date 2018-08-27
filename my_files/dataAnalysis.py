
import matplotlib.pyplot as plt

# Make sure data was manually downloaded



# read data from dropbox folder



# the name of the file should represent the time at the end of the measurement, so use linespace with
# the number of values to add x-time array











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

