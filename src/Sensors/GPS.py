# -*- coding: utf-8 -*
from gps import *
import logging
import time
from Sensor import SensorClass

class GPSClass(SensorClass):
    """A class for a GPS"""
    gpsd = None    

    def setup(self):
        try:
            self.gpsd = gps(mode=WATCH_ENABLE)
            # Check if we have the signal for 'timerTotal' seconds else continue
            timerTotal = 30
            timerStep = 0.2
            logging.debug("self.gpsd.fix.mode : "+str(self.gpsd.fix.mode))
            logging.debug("timerTotal : "+str(timerTotal))
            while self.gpsd.fix.mode < 2 and timerTotal >= timerStep:
                time.sleep(timerStep)
                timerTotal -= timerStep
                self.gpsd.next()
                logging.debug("self.gpsd.fix.mode : "+str(self.gpsd.fix.mode))
                logging.debug("timerTotal : "+str(timerTotal))
            return True
        except socket.error:
            logging.error("Cannot access to GPS using gpsd")
        except:
            logging.error("Unable to configure GPS")
        return False
        
    def getSensorValue(self):
        self.gpsd.next()
        strResult = ''
        strResult += str(self.gpsd.fix.latitude)+","
        strResult += str(self.gpsd.fix.longitude)+","
        strResult += str(self.gpsd.utc)+","
        strResult += str(self.gpsd.fix.time)+","
        strResult += str(self.gpsd.fix.altitude)+","
        strResult += str(self.gpsd.fix.eps)+","
        strResult += str(self.gpsd.fix.epx)+","
        strResult += str(self.gpsd.fix.epv)+","
        strResult += str(self.gpsd.fix.ept)+","
        strResult += str(self.gpsd.fix.speed)+","
        strResult += str(self.gpsd.fix.climb)+","
        strResult += str(self.gpsd.fix.track)+","
        strResult += str(self.gpsd.fix.mode)
        #strResult += str(self.gpsd.satellites)
        return strResult