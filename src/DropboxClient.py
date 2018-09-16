import os
import dropbox

class DropboxClient:

    def __init__(self, dropboxToken):
        self.dbx = dropbox.Dropbox(dropboxToken)

    def uploadToDropbox(self, file, path):
        
        with open(file,'rb') as f:
            string=f.read()

        a=self.dbx.files_upload(string,'/'+path+'/'+file)
        #move the file to uploaded logs
        file = "'" + file + "'"
        cmd = "sudo mv {0} ./uploaded_logs/".format(file)
        os.system(cmd)
        return a
