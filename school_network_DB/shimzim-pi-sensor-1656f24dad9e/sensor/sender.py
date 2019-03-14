import logging
import time
import requests
import counter
import shutil
import os
import signal
import socket
import fcntl
import struct

SENSOR_ID_BASE = 153769000

class Sender:
    def __init__(self, sensor_id, queue, sleep_interval, sleep_interval_short, max_measurements, url):
        self.sensor_id = sensor_id
        self.queue = queue
        self.sleep_interval = sleep_interval
        self.sleep_interval_short = sleep_interval_short
        self.max_measurements = max_measurements
        self.url = url
        self.empty_queue_encountered = 0

    def get_internal_ip(self, interface):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])

    def send_data_loop(self):
        while True:
            data = []
            try:
                for i in range(self.max_measurements):
                    data.append(self.queue.get_nowait())
                self.empty_queue_encountered = 0
            except:
                if len(data) == 0:
                    logging.exception("Nothing to read from queue - strange")
                    self.empty_queue_encountered += 1
                    if self.empty_queue_encountered > 5:
                        logging.error("Multiple empty-queue errors encountered - erasing the queue and committing suicide")
                        try:
                            shutil.rmtree(os.path.join(os.environ.get("HOME"), "pisensorqueuetemp"))
                            shutil.rmtree(os.path.join(os.environ.get("HOME"), "pisensorqueue"))
                        except:
                            logging.exception("Failed erasing queues")
                        finally:
                            os.kill(os.getpid(), signal.SIGKILL)
            logging.debug("Read %d measurements from queue", len(data))
            if len(data) > 0:
                try:
                    internal_ip = self.get_internal_ip("wlan0")
                except:
                    internal_ip = "unknown"
                to_send = {
                        "sensorID": SENSOR_ID_BASE + self.sensor_id,
                        "internalIP": internal_ip,
                        "measurements": data
                        }
                logging.debug("SENDING PACKAGE: %s", to_send)
                try:
                    resp = requests.post(self.url, json=to_send, headers={'User-Agent':'', 'Content-Type':'application/x-www-form-urlencoded'})
                    counter.increment('/var/log/pi-sensor/report-packets-counter')
                    counter.increment('/var/log/pi-sensor/report-counter', len(data))
                    self.queue.task_done()
                except:
                    logging.exception("Error sending to server - putting %d messages back into queue", len(data))
                    try:
                        logging.info("Server response was: %s", resp.content)
                    except:
                        pass
                    for d in data:
                        self.queue.put(d)
            try:
                messages_in_queue = self.queue.qsize()
            except:
                logging.exception("Failed to read number of messages in the queue")
                messages_in_queue = 0
            if messages_in_queue > 0:
                logging.debug("Short sleep only - there are %s messages still in the queue" % messages_in_queue)
                time.sleep(self.sleep_interval_short)
            else:
                logging.debug("Going to sleep")
                time.sleep(self.sleep_interval)
