# -*- coding: utf-8 -*-
from Sensor import SensorClass
import smbus
import math
import time
import logging
import sys
sys.path.append("Libs")
import mpu6050

class MPU6050Class(SensorClass):
    """A class for a Gyroscope/Accemerometre sensor MPU6050"""
    power_mgmt_1 = 0x6b
    accel_scale = 16384.0

    # *****************
    # Please set the real address of your device (using i2cdetect)
    address = 0x69
            
    def setup(self):
        # Sensor initialization
        self.mpu = mpu6050.MPU6050(0x69)
        self.mpu.dmpInitialize()
        self.mpu.setDMPEnabled(True)

        # get expected DMP packet size for later comparison
        self.packetSize = self.mpu.dmpGetFIFOPacketSize() 
        return True
    
    def getSensorValue(self):
        mpuIntStatus = self.mpu.getIntStatus()

        if mpuIntStatus >= 2: # check for DMP data ready interrupt (this should happen frequently) 
            # get current FIFO count
            fifoCount = self.mpu.getFIFOCount()

            # check for overflow (this should never happen unless our code is too inefficient)
            if fifoCount == 1024:
                # reset so we can continue cleanly
                self.mpu.resetFIFO()

            # wait for correct available data length, should be a VERY short wait
            fifoCount = self.mpu.getFIFOCount()
            while fifoCount < self.packetSize:
                fifoCount = self.mpu.getFIFOCount()

            result = self.mpu.getFIFOBytes(self.packetSize)
            q = self.mpu.dmpGetQuaternion(result)
            g = self.mpu.dmpGetGravity(q)
            ypr = self.mpu.dmpGetYawPitchRoll(q, g)

            strYPR = "{0:.2f},{1:.2f},{2:.2f}".format(ypr['yaw'] * 180 / math.pi,ypr['pitch'] * 180 / math.pi,ypr['roll'] * 180 / math.pi)
            return strYPR
        return ""

