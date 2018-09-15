import os
import dropbox

class DropboxClient:

    def __init__(self, dropboxToken):
        self.dbx = dropbox.Dropbox(dropboxToken)

    def uploadToDropbox(self, file, hardware, path):
        with open(path+file,'rb') as f:
            string=f.read()

        a=self.dbx.files_upload(string,'/'+str(hardware)+'/'+file)
        #move the file tto uploaded logs
        file = "'" + file + "'"
        cmd = "sudo mv {0} {1}uploaded_logs/".format(file, path)
        os.system(cmd)
        return a
