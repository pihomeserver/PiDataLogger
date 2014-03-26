# -*- coding: utf-8 -*-
import random
from Sensor import SensorClass
class ExampleIntClass(SensorClass):
    """A class for a dummy sensor returning int value"""
    def setup(self):
        # Nothing to do so let say that all is ok
        return True
    
    def getSensorValue(self):
        return str(random.randint(1, 100))