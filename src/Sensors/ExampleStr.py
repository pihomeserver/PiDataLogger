# -*- coding: utf-8 -*-
import random
import string

from Sensor import SensorClass
class ExampleStrClass(SensorClass):
    """A class for a dummy sensor returning string value"""
    def setup(self):
        # Nothing to do so let say that all is ok
        return True
        
    def getSensorValue(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))