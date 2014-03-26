# -*- coding: utf-8 -*-
# Import classes for multiprocessing
from multiprocessing import Process, Queue
import time
import ConfigParser
from Timer import TimerClass as Timer
import logging
import os.path
import sqlite3
from datetime import datetime
import calendar
import sys
sys.path.append("Sensors")
sys.path.append("Libs")

# Main class to manage the data logging
class RecorderClass:
    # Create the communication queue between sensors and the main process
    communication_queue = Queue()
    # Output file
    output_file = ""
    # Store messages from sensors
    dataMessages = []
    # Maximum messages to store before a dump in the output file
    maxMessages = 100
    # Create a list of sensors
    listOfSensors = []
    # Create a list of process linked to each sensor
    listOfWorkerSensors = []
    # Recorder status. Default : no recording
    status = False
    # Connection to the database
    connection = ""
    cursor = ""
    
    # Initialize the recorder
    def initRecorder(self, output_file):
        self.output_file = output_file

    # Get status of the recorder
    def getStatus(self):
        logging.debug('Recorder status : '+str(self.status))
        return self.status

    # Stop all sensors
    def stopAllSensors(self):
        logging.info('Stop all sensors')
        for process in self.listOfWorkerSensors:
            logging.debug('Stop sensor : '+process.name+' - '+str(process.is_alive()))
            process.terminate()
        self.status = False

    # Start all sensors
    def startAllSensors(self):
        logging.info('Start all sensors')
        for process in self.listOfWorkerSensors:
            process.start()
        self.status = True

    # Add a sensor in the data logger
    def addSensor(self, name, ID, type, refresh):
        # Import the wanted module
        sensor = __import__(type, globals(), locals(), [], -1)
        # Extract the class of the sensor
        class_ = getattr(sensor, type+'Class')
        tmpSensor = class_()
        # Init the sensor with parameters
        tmpSensor.init(name, ID, type, refresh, self.communication_queue)
        if tmpSensor.setup()==True:
            logging.info(tmpSensor.getInformation())
            # Save the sensor
            self.listOfSensors.append(tmpSensor)
            # Save the thread used by the sensor
            self.listOfWorkerSensors.append(Process(target=tmpSensor.run, args=()))
        else:
            logging.error('Unable to add sensor '+name)

    # Read waiting messages stored in the queue
    def readQueue(self):
        # Is there a message in the queue ?
        if not self.communication_queue.empty():
            strData = self.communication_queue.get_nowait()
            # Store data in the DB
            data = strData.split(";")
            self.cursor.execute("INSERT INTO Data (tripId, sensorId, strRecordDate, intRecordDate, sensorValue) VALUES (?, ?, ?, ?, ?)", (self.nextTripId, data[2], data[0], data[1], data[4]))
            self.connection.commit()
            # Print the data
            logging.debug('Data received : '+strData)
            
    # Clear all messages in the queue
    def clearQueue(self):
        while not self.communication_queue.empty():
            strData = self.communication_queue.get_nowait()
        
    # Create new trip
    def createTrip(self):
        d = datetime.now()
        self.cursor.execute("INSERT INTO Trip (tripId, intStartDate, strStartDate) VALUES (?, ?, ?)", (self.nextTripId, calendar.timegm(d.timetuple()),str(d)))
        self.connection.commit()
    
    # Close current trip
    def closeCurrentTrip(self):
        d = datetime.now()
        self.cursor.execute("UPDATE Trip set intEndDate = ?, strEndDate = ? WHERE tripId=?", (calendar.timegm(d.timetuple()), str(d), self.nextTripId))
        self.connection.commit()    
        logging.info("Update nextTripId")
        self.nextTripId = self.nextTripId + 1
        logging.info("nextTripId = "+str(self.nextTripId))
        
    # Load a configuration file
    def readConfig(self, filename):
        logging.info('Reading configuration from file '+filename)
        config = ConfigParser.ConfigParser()
        config.read(filename)
        logFilename = config.get("Main", "LogFile")
        if logFilename <> "":
            logging.basicConfig(filename=logFilename, level=logging.DEBUG)
        # Read database configuration
        logging.info("Initialize the database connection")
        databaseFile = config.get("Database", "DatabaseFilename")
        # Open DB (if DB does not exists, will be created)
        self.connection = sqlite3.connect(databaseFile, check_same_thread=False)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # Create tables
        logging.info("Create tables if they do not exist")
        # Trips table
        sql = 'create table if not exists Trip (tripId integer PRIMARY KEY AUTOINCREMENT, strStartDate text, intStartDate integer, strEndDate text, intEndDate integer)'
        self.cursor.execute(sql)
        # Sensors table
        sql = 'create table if not exists Sensors (sensorId text PRIMARY KEY, name text, type text, timer real, description text)'
        self.cursor.execute(sql)
        # Data table
        sql = 'create table if not exists Data (tripId integer, sensorId integer, strRecordDate text, intRecordDate integer, sensorValue blob)'
        self.cursor.execute(sql)
        self.connection.commit()
        # Search for the highest trip id
        logging.info("Search for the next trip id")
        sql = 'SELECT max(tripId) FROM Trip'
        self.cursor.execute(sql)
        self.nextTripId = self.cursor.fetchone()[0]
        if self.nextTripId == None:
            self.nextTripId = 0
        else:
            self.nextTripId = self.nextTripId + 1
        logging.info("nextTripId : "+str(self.nextTripId))
        numberOfSensors = config.get("Main", "NumberOfSensors")
        logging.debug('From file '+filename+', '+numberOfSensors+' sensors')
        if numberOfSensors > 0:
            for idSensor in range (int(numberOfSensors)):
                sensorName = config.get("Sensor"+str(idSensor),"Name")
                sensorType = config.get("Sensor"+str(idSensor),"Type")
                sensorID = config.get("Sensor"+str(idSensor),"ID")
                sensorTimer = float(config.get("Sensor"+str(idSensor),"Timer"))
                logging.debug('Add sensor : '+sensorName+", "+sensorID+", "+sensorType+", "+str(sensorTimer))
                self.addSensor(sensorName, sensorID, sensorType, sensorTimer)
                # Add sensor to the database
                self.cursor.execute("INSERT OR IGNORE INTO Sensors (sensorId, name, type, timer) VALUES (?, ?, ?, ?)", (sensorID, sensorName, sensorType, sensorTimer))
        self.connection.commit()
                

    