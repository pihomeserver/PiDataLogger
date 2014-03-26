# -*- coding: utf-8 -*-
from Sensor import SensorClass
import os
import glob

class DS18B20Class(SensorClass):
    device_folder = ""
    device_file = ""

    """A class for a temperature sensor DS18B20"""
    def setup(self):
        result=os.popen('lsmod | grep "^wire"').read()
        if result=="":
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
        # Set up the location of the sensor in the system. Only the first one will be used
        self.device_folder = glob.glob('/sys/bus/w1/devices/28*')
        
        self.device_file = ""
        if len(self.device_folder) > 0:
            # Define the full path of the file with the temperature value
            if self.device_folder<>"":
                self.device_file = self.device_folder[0] + '/w1_slave'
                return True;
            else:
                return False;
        return False;

    # A function that grabs the raw temperature data from the sensor
    def readTempRaw(self):
        # Open file with data
        f = open(self.device_file, 'r')
        # Read all lines (should not be more than 2)
        lines = f.readlines()
        f.close()
        return lines


    # A function that checks that the connection was good and strips out the temperature
    def getSensorValue(self):
        if self.device_file=="":
            return ''
        else:
            lines = self.readTempRaw()
            # If all is ok you should have a "YES" on the first line
            if lines[0].strip()[-3:] != 'YES':
                return "?"
            # Search for the 't=' on the second line
            equals_pos = lines[1].find('t=')
            # Divide value by 1000 to get real value
            temp = float(lines[1][equals_pos+2:])/1000
            return str(temp)
