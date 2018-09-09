import os
import dropbox

class DropboxClient:

    def __init__(self,dropboxToken):
        self.dbx = dropbox.Dropbox(dropboxToken)

    def uploadToDropbox(self,file,id,path):
        with open(path+file,'rb') as f:
            string=f.read()

        a=self.dbx.files_upload(string,'/'+str(id)+'/'+file)
        #move the file tto uploaded logs
        file = "'" + file + "'"
        cmd = "sudo mv {0}"+path+"uploaded_logs/".format(file, str(id))
        os.system(cmd)
        return a
