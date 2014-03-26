#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time as time
import os
import ConfigParser
import signal
import logging
import sys
sys.path.append("Libs")
sys.path.append("Sensors")
from Timer import TimerClass as Timer
from Recorder import RecorderClass

# Define the log level
logging.basicConfig(level=logging.DEBUG)

# Define mode to access GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
# pin id for the shutdown button
GPIO_shutdown=23
# pin id for the record button
GPIO_record=11
# pin id for the LED status
GPIO_led_green=17
GPIO_led_red=21
# Flag for the recording function status
Recording_status=False

# GPIO_shutdown will be an input pin
logging.debug('Setup GPIO #'+str(GPIO_shutdown)+' as an input pin')
GPIO.setup(GPIO_shutdown, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO_shutdown will be an input pin
logging.debug('Setup GPIO #'+str(GPIO_record)+' as an input pin')
GPIO.setup(GPIO_record, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO_led* will be output pins
logging.debug('Setup GPIO #'+str(GPIO_led_green)+' as an output pin')
GPIO.setup(GPIO_led_green, GPIO.OUT)
logging.debug('Setup GPIO #'+str(GPIO_led_red)+' as an output pin')
GPIO.setup(GPIO_led_red, GPIO.OUT)

# Function to turn on/off LED status
def funcLEDstatus(status):
    logging.debug('LED new status : '+status)
    if status == "red":
        GPIO.output(GPIO_led_green, False)
        GPIO.output(GPIO_led_red, True)
    elif status == "green":
        GPIO.output(GPIO_led_green, True)
        GPIO.output(GPIO_led_red, False)
    elif status == "off":
        GPIO.output(GPIO_led_green, False)
        GPIO.output(GPIO_led_red, False)

# Handler to stop the process
def signal_handler(signal, frame):
    logging.debug('dataLogger.signal_handler has been activated')
    # Turn off the status LED
    funcLEDstatus("off")
    GPIO.cleanup()
    exit(0)
    
# Define what to do when the shutdown button is pressed
def funcShutdown(channel):
    logging.debug('dataLogger.funcShutdown has been activated')
    global Recording_status
    global blinkThread
    start_time = time.time()
    intSeconds = 0
    # How long to wait for the button
    maxWaitPushButton = 2
    while intSeconds < maxWaitPushButton and GPIO.input(channel) == GPIO.LOW :
        intSeconds = time.time() - start_time
        time.sleep(0.1)
    if intSeconds >= maxWaitPushButton:
        # Turn off the status LED
        if Recording_status:
            blinkThread.stop()
        funcLEDstatus("off")
        GPIO.cleanup()
        recorder.stopAllSensors()
        os.system('sudo halt')
        #exit()
    else:
        logging.debug('dataLogger.funcShutdown cancelled')

        
# Make the LED blinks
def funcLEDBlink(color, onTime):
    #while 1:
    funcLEDstatus(color)
    time.sleep(onTime)
    funcLEDstatus("off")
        
# Function to start or stop the recording
def funcStartStopRecord(channel):
    global Recording_status
    global blinkThread
    global recorder
    Recording_status = not Recording_status
    if Recording_status:
        # Create the trip record
        recorder.createTrip()
        # Switch the LED color
        funcLEDstatus("red")
        blinkThread.start()
        # Start the recording process
        recorder.clearQueue()
        recordThread.start()
    else:
        # Stop the recording process
        recordThread.stop()
        # Close the trip and calculate next trip ID
        recorder.closeCurrentTrip()
        # Stop LED blinking
        blinkThread.stop()
        # Switch the LED color
        funcLEDstatus("green")

def funcRecordData():
    # Read queue if some messages are waiting
    recorder.readQueue()

# Create a thread to make the LED status blinking
blinkThread = Timer(2.0, funcLEDBlink, ["red", 0.2])
# Add a signal handler for the SIGTERM signal
signal.signal(signal.SIGTERM, signal_handler)
# Wait for the shutdown button to be pressed
GPIO.add_event_detect(GPIO_shutdown, GPIO.FALLING, callback=funcShutdown, bouncetime=300) 
# Wait to start or stop the data recording process
GPIO.add_event_detect(GPIO_record, GPIO.FALLING, callback=funcStartStopRecord, bouncetime=300) 
# Create a thread to record sensors
recordThread = Timer(0.2, funcRecordData, [])

# Define and initialize the recorder
recorder = RecorderClass()
# Load configuration file
recorder.readConfig("Config/config.ini")
# Activate all sensors
recorder.startAllSensors()

# Light up the status LED
funcLEDstatus("green")

try:
    # Loop
    while 1:
        time.sleep(0.2)

    #time.sleep(1)
    #funcStartStopRecord(GPIO_record)
    
except (KeyboardInterrupt):
    funcShutdown(GPIO_shutdown)