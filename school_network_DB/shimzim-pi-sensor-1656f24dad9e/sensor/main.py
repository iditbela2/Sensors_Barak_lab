#!/usr/bin/python
from threading import Thread
import logging
import measure
import sender
from pqueue import Queue
import ConfigParser
import sys
import os

if len(sys.argv) != 2:
    print("Usage: main.py <path_to_config_file>")
    sys.exit(1)
config = ConfigParser.ConfigParser()
config.read(sys.argv[1])
if not os.path.exists('/var/log/pi-sensor'):
    os.makedirs('/var/log/pi-sensor')
logging.basicConfig(filename='/var/log/pi-sensor/pi-sensor.log',level=config.getint('PiSensor', 'LogLevel'), format='%(asctime)s %(levelname)-8s %(threadName)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


logging.info("*** Starting main ***")
logging.info("*** Creating queue ***")
QUEUE_TEMP_DIR = os.path.join(os.environ.get("HOME"), "pisensorqueuetemp")
QUEUE_DIR = os.path.join(os.environ.get("HOME"), "pisensorqueue")
if not os.path.exists(QUEUE_TEMP_DIR):
    os.makedirs(QUEUE_TEMP_DIR)
if not os.path.exists(QUEUE_DIR):
    os.makedirs(QUEUE_DIR)
q = Queue(QUEUE_DIR, tempdir=QUEUE_TEMP_DIR, maxsize=config.get('PiSensor', 'MaxQueueSize'))


logging.info("*** Starting reporter thread ***")
r = sender.Sender(config.getint('PiSensor', 'SensorID'),
            q, config.getint('PiSensor', 'ReporterSleepIntervalSeconds'),
            config.getint('PiSensor', 'ReporterSleepIntervalSecondsShort'),
            config.getint('PiSensor', 'MaxMeasurementsToSend'),
            config.get('PiSensor', 'ServerURL'))
reporter_thread = Thread(target=r.send_data_loop)
reporter_thread.daemon = True
reporter_thread.start()

logging.info("*** Starting measurement loop ***")
m = measure.Measure(q, config.get('PiSensor', 'TtyDevice'), config.getint('PiSensor', 'MeasurementSleepIntervalSeconds'))
measure_thread = Thread(target=m.measurement_loop)
measure_thread.daemon = True
measure_thread.start()

logging.info("*** Running... ***")
reporter_thread.join()
logging.info("reported thread dies")
measure_thread.join()
logging.info("measure thread dies")
