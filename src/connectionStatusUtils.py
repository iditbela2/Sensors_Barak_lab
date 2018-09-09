import subprocess

def checkInternetConnection():
    """function:
        This function checks if there is an internet connection
        to the wifi and uploading is possible. It returns True if yes.
        """
    list_output = subprocess.check_output("iwconfig")
    list_output = list_output.decode("utf-8")
    list_output = list_output.split("\n")
    for line in list_output:
        if line.find("wlan0") > -1 or line.find("wlan1") > -1:
            if not line[line.find("ESSID") + 6] == "o":
                return True

    return False
