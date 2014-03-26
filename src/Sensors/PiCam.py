# -*- coding: utf-8 -*-

import time
import picamera
import io

from Sensor import SensorClass
class PiCamClass(SensorClass):
    """A class for a Raspberry Pi Cam"""

    """ ********** WARNING : DOES NOT WORK ************ """
    
    camera = picamera.PiCamera()
    piCamStream = io.BytesIO()
    
    def setup(self):
        self.camera.resolution = (1280, 720)
        #self.camera.start_preview()
        #self.camera.led = False
        return True
        
    def getSensorValue(self):
        print "getSensorValue"
        #self.camera.capture(self.piCamStream, 'jpeg')
        self.camera.capture('test.jpg')
        return piCamStream