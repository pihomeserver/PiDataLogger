# -*- coding: utf-8 -*-
# Standard class for all sensors
from multiprocessing import TimeoutError
import time
from datetime import datetime
import calendar
import sys

# ***********************************************
# Main class for sensors. Should not be updated
# ***********************************************

class SensorClass:
    """A class for a sensor"""
    # Init class when instantiation is called
    def __init__(self):
        self.name = ""
        self.sensorID = "00000000"
        self.type = ""
        self.timer = 0;
        self.queue = ""
    
    # Initialize the sensor's values
    def init(self, name, ID, type, timer, queue):
        self.name = name
        self.sensorID = ID
        self.type = type
        self.timer = timer
        self.queue = queue
        
    # Setup the sensor if some actions have to be performed before recording
    # Returns True if setup is ok
    # Returns False if setup is nok. Then the sensor will be ignored
    def setup(self):
        pass
    
    # Post a message in the queue
    def postSensorValue(self):
        d = datetime.now()
        return str(d)+";"+str(calendar.timegm(d.timetuple()))+";"+self.getSensorID()+";"+self.type+";"+self.getSensorValue();
    
    # Return sensor ID
    def getSensorID(self):
        return self.sensorID
    
    # Run sensor
    def run(self):
        while True:
            try:
                self.queue.put_nowait(self.postSensorValue())
                time.sleep(self.timer)
            except TimeoutError:
                pass
            except KeyboardInterrupt:
                sys.exit(0)
    
    # Display the sensor's values
    def getInformation(self):
        return 'Information :\n  Name : '+self.name+'\n  Type : '+self.type+'\n  Timer : '+str(self.timer)
        
        