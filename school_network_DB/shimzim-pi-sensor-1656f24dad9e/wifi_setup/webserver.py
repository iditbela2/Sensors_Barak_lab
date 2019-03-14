#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import urlparse
import subprocess

WIFI_INTERFACE = 'wlan0'

SERVER_RUNNING = True

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def get_all_ssids(self):
        ret = []
        ssids = subprocess.check_output("iwlist %s scan | grep ESSID | cut -d: -f2" % WIFI_INTERFACE, shell=True).strip()
        for ssid in ssids.split('\n'):
            ret.append(ssid.strip('"'))
        return ret

    def configure_ssid(self, ssid, password=None):
        found = False
        if password:
            password_str = 'psk="%s"' % password
        else:
            password_str = 'key_mgmt=NONE'

        with open('/etc/wpa_supplicant/wpa_supplicant.conf','r') as f:
            content = f.readlines()

        for i, line in enumerate(content):
            if "ssid" in line and ssid in line:
                found = True
                if 'psk' in content[i+1]:
                    start_char = content[i+1].find("psk")
                elif 'key_mgmt' in content[i+1]:
                    start_char = content[i+1].find("key_mgmt")
                content[i+1] = ' '*start_char + '%s\n' % password_str

        if found:
            with open('/etc/wpa_supplicant/wpa_supplicant.conf','w') as f:
                f.write(''.join(content))
        else: 
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
                f.write("""
network={
    ssid="%s"
    %s
}

""" % (ssid, password_str))

    def is_sensor_id_configured(self):
        with open('/etc/pi-sensor/pi-sensor.cfg', 'r') as f:
            content = f.read()
        return "NO_ID" not in content

    def configure_sensor_id(self, sensor_id):
        with open('/etc/pi-sensor/pi-sensor.cfg', 'r') as f:
            content = f.read()
        content = content.replace('NO_ID', sensor_id)
        with open('/etc/pi-sensor/pi-sensor.cfg', 'w') as f:
            f.write(content)

    def do_GET(self):
        if not self.is_sensor_id_configured():
            with open("static/sensor_id.html", "r") as f:
                content = f.read()
        else:
            all_ssids = self.get_all_ssids()
            self._set_headers()
            with open("static/wifi.html", "r") as f:
                content = f.read()
            ssid_list_html = ""
            for ssid in all_ssids:
                ssid_list_html += ('<option value="%s">%s</option>\n' % (ssid, ssid))
            content = content.replace("SSID_LIST_GOES_HERE", ssid_list_html)
        self.wfile.write(content)

    def do_POST(self):
        global SERVER_RUNNING
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data_dict = urlparse.parse_qs(post_data)
        self._set_headers()
        if 'sensor_id' in data_dict:
            self.configure_sensor_id(data_dict['sensor_id'][0])
            self.wfile.write('<h1>SENSOR ID CONFIGURED. SENSOR IS READY</h1>')
        else:
            with open("static/configured.html", "r") as f:
                content = f.read()
            self.wfile.write(content)
            if 'password' in data_dict:
                self.configure_ssid(data_dict['ssid'][0], data_dict['password'][0])
            else:
                self.configure_ssid(data_dict['ssid'][0])
            subprocess.Popen("sleep 2 && /usr/bin/autohotspot", shell=True)
            SERVER_RUNNING = False
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    global SERVER_RUNNING
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    while SERVER_RUNNING:
        httpd.handle_request()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
