# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 13:48:20 2019

@author: Parker Niemeyer blow me
"""
######################## IMPORT PYTHON LIBRARIES ###############################

from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from nanpy import (ArduinoApi, SerialManager)
from time import sleep
import threading
import os
import RPi.GPIO as GPIO
import math
####################### GLOBAL VARIABLE INSTANTIATION #########################

enableSignal = False   #current crankshaft state
enableSignalPrevious = False  #previous crankshaft state


###############################################################################
############### DEFINE USER FUNCTIONS (not app route functions)################
###############################################################################

########################## ARDUINO FUNCTIONS ##################################

def ConnectArduino(): #establish connection with arduino
	try:		
		connection = SerialManager(device = '/dev/ttyACM0') #change device path for multiple Arduinos
		ConnectArduino.a = ArduinoApi(connection = connection)
		print("\n\nConnection Successful...\n\n")
	except:
		print("\n\nFailed to connect...\n\n")

def CrankshaftWaveform(): #Michael Mechelay's Crankshaft Waveform Function
	global enableSignal
	#for testing purposes a periode takes 120 ms.
	#for actual wave form it needs to take 50 ms.

	MyPin=8 # pin for waveform
	
	#designate Arduino connection
	a = ConnectArduino.a

	#Setup the pinModes
	a.pinMode(MyPin, a.OUTPUT)

	while True:
		if not enableSignal:
			a.digitalWrite(MyPin, a.LOW)
			break
	#Set PWM Signal
		for i in range(2):
			a.digitalWrite(MyPin,a.LOW) #2 small
			sleep(0.004) #in seconds
			#a.delay(small_low_delay)
			a.digitalWrite(MyPin,a.HIGH)
			sleep(0.001)
			#a.delay(small_high_delay)
		for x in range(3):      
			a.digitalWrite(MyPin,a.LOW) #3 large
			sleep(0.003)
			#a.delay(big_low_delay)
			a.digitalWrite(MyPin,a.HIGH)
			sleep(0.002)
			#a.delay(big_high_delay)

		a.digitalWrite(MyPin,a.LOW) #1 small
		sleep(0.004)
		#a.delay(small_low_delay)
		a.digitalWrite(MyPin,a.HIGH)
		sleep(0.001)
		#a.delay(small_high_delay)
		
		for y in range(18):
			a.digitalWrite(MyPin,a.LOW) #18 large
			sleep(0.003)
			#a.delay(big_low_delay)
			a.digitalWrite(MyPin,a.HIGH)
			sleep(0.002)
			#a.delay(big_high_delay)


#===================================================================================
##########                   RASPI GPIO FUNCTIONS             ######################

#pin definitions

'''
RPI PINOUT:
---------------
breadboard connections
pin  6: GND
pin  7: VCC
pin 11: CS
pin 15: SCK
pin 16: SDI/SDO

probes b/w POW & POA
---------------
internal SPI connections
pin 17: CS
pin 22: CLK
pin 23: MOSI
'''
#Common Pins
SPI_SDISDO_PIN = 16 # mosi 16 || 23
SPI_CLK_PIN = 15   #15 || 22

#Chip Select
SPI_CS1 = 11  #11 || 17
SPI_CS2 = 13  #13 || 27
SPI_CS3 = 3   #03 || 02


GPIO.setmode(GPIO.BOARD)
GPIO.setup(SPI_CS1, GPIO.OUT)
GPIO.setup(SPI_CS2, GPIO.OUT)
GPIO.setup(SPI_CS3, GPIO.OUT)
GPIO.setup(SPI_CLK_PIN, GPIO.OUT)
GPIO.setup(SPI_SDISDO_PIN, GPIO.OUT)

GPIO.output(SPI_CLK_PIN, False)
GPIO.output(SPI_SDISDO_PIN, False)
GPIO.output(SPI_CS1, False)
GPIO.output(SPI_CS2, False)
GPIO.output(SPI_CS3, False)

GPIO.output(SPI_CS1, True)
GPIO.output(SPI_CS2, True)
GPIO.output(SPI_CS3, True)
GPIO.output(SPI_CLK_PIN, False)

def set_value(b, CS_NUM):
    b = "0000" "00" "{0:010b}".format(b)

    GPIO.output(CS_NUM, False)
    for x in b:
        GPIO.output(SPI_SDISDO_PIN, int(x))
        GPIO.output(SPI_CLK_PIN, True)
        GPIO.output(SPI_CLK_PIN, False)

    GPIO.output(CS_NUM, True)
    
def set_value_by_resistance(givenResistance, cs_NUM):
    
    valueToSet = givenResistance/77.519  #78.125
    valueToSet = math.floor(valueToSet)
    valueToSet = int(valueToSet)
    #print('valueToSet: ' + str(valueToSet))
    set_value(valueToSet, cs_NUM)
    
    
    
#===================================================================================

def touch(filepath): #CALLED TO CREATE DATABASE FILE
    with open(filepath, 'w'):
        os.utime(filepath, None)

def sendtoArduino(sensorPkg, crankshaftVal):	#CALLED ON SUBMIT
    global enableSignal
    global enableSignalPrevious
    enableSignalPrevious = enableSignal
    enableSignal = crankshaftVal
    
    #set potentiometer values
    set_value_by_resistance(sensorPkg[0], SPI_CS1)
    set_value_by_resistance(sensorPkg[1], SPI_CS2)
    set_value_by_resistance(sensorPkg[2], SPI_CS3)
    
    if (enableSignalPrevious != enableSignal):
        #print("Running Thread")
        CrankshaftThread()
    
    crankshaftVal = bool(crankshaftVal)
    print('\n\nSending Sensor Values to Arduino...\n')
    print('Crankshaft = {}\n'.format(crankshaftVal))
    print('Sensor 1   = {}\n'.format(sensorPkg[0]))
    print('Sensor 2   = {}\n'.format(sensorPkg[1]))
    print('Sensor 3   = {}\n\n'.format(sensorPkg[2]))


def CrankshaftThread(): #called to run Michael's Crankshaft Waveform Function in the background
    global enableSignal

    if enableSignal: #run thread
        bg = threading.Thread(target = CrankshaftWaveform)
        bg.start() 


###############################################################################################
########################INITIALIZE FLASK APPLICATION AND DATABASE STRUCTURE####################
###############################################################################################

app = Flask(__name__, template_folder = '/home/pi/Desktop/nanpy/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SensorValues.db'        
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class sensor(db.Model):
   sensor_id = db.Column('sensor_id',db.Integer,unique = True,primary_key = True)
   sensor_name = db.Column(db.String(100))
   sensor_type = db.Column(db.String(100))
   sensor_value = db.Column(db.Float(100))
   sensor_default = db.Column(db.String(100))

   def __init__(self, sensor_id, sensor_name, sensor_type, sensor_value, sensor_default):
      self.sensor_id = sensor_id
      self.sensor_name = sensor_name
      self.sensor_type = sensor_type
      self.sensor_value = sensor_value
      self.sensor_default = sensor_default

   def __repr__(self):
      return "<Sensor ID: {}, Name: {}, Sensor Type: {} Sensor Value: {}>"\
              .format(self.sensor_id, self.sensor_name, self.sensor_type, self.sensor_value)


def ResetSensorType(sensorType):
    temp = sensor.query.filter_by(sensor_type = sensorType).all()
    for i in range(len(temp)):
        temp[i].sensor_value = temp[i].sensor_default
    db.session.commit()
    print('Resetting Sensor Type: {}\n'.format(sensorType))

# Set Default Sensor Values in SensorValues.db #
def InitializeDatabase():
    touch('/home/pi/Desktop/nanpy/SensorValues.db')
    pot1 = sensor(0,'Sensor 1', 'E1-Oil', 2500, 2500)
    pot2 = sensor(1, 'Sensor 2', 'E1-Oil', 2500, 2500)

    pot3 = sensor(2, 'Sensor 3', 'E1-Coolant', 2500, 2500)
    crankshaft = sensor(3,'Crankshaft Sensor', 'E1-Crankshaft',0, 0)
    db.create_all()
    db.session.add(pot1)
    db.session.add(pot2)
    db.session.add(pot3)
    db.session.add(crankshaft)
    db.session.commit()
    print('\n\nSensor Values Reset to Default...\n\n')


############################# RUN ON START ############################################
#reset sensor database values to default upon program start
touch('/home/pi/Desktop/nanpy/SensorValues.db') #wipe database
ConnectArduino() #establish connection with Arduino 
InitializeDatabase()      #setting default values at startup of application
sendtoArduino([2500,2500,2500], False)
#######################################################################################

@app.route('/')
def home():   
    return render_template('home.html')


#EDIT THIS
@app.route('/G3606', methods = ['GET', 'POST'])
def G3606():
    if request.method == 'POST':
        crankshaftVal = request.form.get('crankshaftVal')           #load crankshaft value from webpage
                                                                    #crankshaftVal won't exist if reset is clicked
        if crankshaftVal is None:   #logic for checking if the submit button was pressed or reset button was pressed
            ResetSensorType('E1-Oil')          #reset button is pressed if flask doesn't receive a value from the submit form
            
            #############
            
            sensorPkg = []          #reset sensor values to default and populate the page with default values
            crankshaftVal = sensor.query.filter_by(sensor_id = 3).first().sensor_value
            crankshaftVal = int(crankshaftVal)
            for i in range(len(sensor.query.all()) - 1):				#fill array with existing sensor values
            	sensorPkg.append(sensor.query.filter_by(sensor_id = i).first().sensor_value)
       
        else:
            sensorPkg = []												#initialize array sensorPkg
            crankshaftVal = request.form.get('crankshaftVal')           #load default crankshaft value
            crankshaftVal = int(crankshaftVal)
            temp = sensor.query.filter_by(sensor_id = 3).first()
            temp.sensor_value = crankshaftVal
            db.session.commit()
            for i in range(len(sensor.query.all()) - 1): 					#for all sensor values in webpage
            	temp = sensor.query.filter_by(sensor_id = i).first()	#temp=obj for each sensor entry in the database
            	temp.sensor_value = request.form.get('pot'+str(i))		#temp.sensor_value = value for each html slider 
            	db.session.commit()										#replace existing values in database
            	sensorPkg.append(sensor.query.filter_by(sensor_id = i).first().sensor_value) #fill array with sensor values to send to Arduino
            
            sendtoArduino(sensorPkg, crankshaftVal)     #send updated values to arduino
            
        if (crankshaftVal == 0):            #logic for populating crankshaft dropdown with db stored value
            enableShutdown = 'selected'
            enableStartup = ''
        elif (crankshaftVal == 1):
            enableShutdown = ''
            enableStartup = 'selected'
    
        
        return render_template('G3606.html', sensorPkg = sensorPkg, crankshaftVal = crankshaftVal,\
                               enableShutdown = enableShutdown, enableStartup = enableStartup)
    else:
        sensorPkg = []
        crankshaftVal = sensor.query.filter_by(sensor_id = 3).first().sensor_value
        crankshaftVal = int(crankshaftVal)
        
        if (crankshaftVal == 0):
            enableShutdown = 'selected'
            enableStartup = ''
        elif (crankshaftVal == 1):
            enableShutdown = ''
            enableStartup = 'selected'
            
        for i in range(len(sensor.query.all()) - 1):				#fill array with existing sensor values
        	sensorPkg.append(sensor.query.filter_by(sensor_id = i).first().sensor_value)
        
        return render_template('G3606.html', sensorPkg = sensorPkg, crankshaftVal = crankshaftVal,\
                               enableShutdown = enableShutdown, enableStartup = enableStartup)


###########################DESIGNATE TARGET IP ADDRESS#####################################    
if __name__ == '__main__':
   db.create_all()
   #app.run(debug=True) #comment out if running over specified IP
   #app.run(host = 'localhost', port = '80')
   app.run(host = '192.168.4.1', port = '80')
   
