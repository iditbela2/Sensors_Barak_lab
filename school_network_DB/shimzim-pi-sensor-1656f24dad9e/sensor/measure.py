import subprocess
import logging
import serial
import time
import pqueue
import counter

class Measure:
    def __init__(self, queue, device, sleep_interval):
        self.queue = queue
        self.device = device
        self.sleep_interval = sleep_interval

    def get_sensor_data(self, device):
        t = serial.Serial(device, 9600)
        #t.setTimeout(1.5)
        t.flushInput()
        retstr = t.read(10)
        if len(retstr)==10:
            if(retstr[0]==b"\xaa" and retstr[1]==b'\xc0'):
                checksum=0
                for i in range(6):
                    checksum=checksum+ord(retstr[2+i])
                if checksum%256 == ord(retstr[8]):
                    pm25=ord(retstr[2])+ord(retstr[3])*256
                    pm10=ord(retstr[4])+ord(retstr[5])*256
                    return dict(pm2_5 = pm25/10.0, pm10 = pm10/10.0)
                else:
                    logging.error("Checksum error (%s): %s != %s", retstr, checksum%256, ord(retstr[8]))
            else:
                logging.error("Header error (%s)", retstr)
        return None
    
    def get_router_details(self):
        try:
            mac = subprocess.check_output("""arp -i $(ip route show match 0/0 | awk '{print $5,$3}') | tail -1 | awk '{print $3}'""", shell=True).strip()
            ssid = subprocess.check_output('iwgetid -r', shell=True).strip()
            return mac, ssid
        except:
            return None, None
    
    def measurement_loop(self):
        while True:
            sensor_data = self.get_sensor_data(self.device)
            if sensor_data:
                router_mac, ssid = self.get_router_details()
                measurement = {
                        "timestamp": time.time(),
                        "wifiRouterMAC": router_mac,
                        "wifiSSID": ssid,
                        }
                measurement.update(sensor_data)
            logging.debug("Sending to queue: %s", measurement)
            try:
                self.queue.put(measurement)
                counter.increment('/var/log/pi-sensor/measurement-counter')
            except:
                logging.exception("Error pushing to queue")
            time.sleep(self.sleep_interval)
