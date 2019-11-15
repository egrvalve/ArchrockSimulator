from nanpy import ArduinoApi
from nanpy import SerialManager
from time import sleep
#import spi as SPI

def ConnectArduino():
	try:		
		connection = SerialManager(device = '/dev/ttyACM0')
		ConnectArduino.a = ArduinoApi(connection = connection)
		print("\n\nConnection Successful...\n\n")
	except:
		print("\n\nFailed to connect...\n\n")

def CrankshaftWaveform():
		global enableSignal
		small_low_delay = 4 #4ms
		small_high_delay = 1 #ms
		big_low_delay = 3  #3 ms
		big_high_delay = 2 #2ms
		#These constants will need to be changed to match 1 cycle of the cam shaft.
		#for testing purposes a periode takes 120 ms.
		#for actual wave form it needs to take 50 ms.

		MyPin=8 # pin for waveform

		#try: #establish Arduino Connection
		#connection = SerialManager()
		#a = ArduinoApi(connection = connection)
		a = ConnectArduino.a
		print("\n\nConnection Successful...\n\n")

		#Setup the pinModes

		a.pinMode(MyPin, a.OUTPUT)
#		if enable:
		while True:
			if not enableSignal:
				a.digitalWrite(MyPin, a.LOW)
				break
		#Set PWM Signal
			for i in range(2):
				a.digitalWrite(MyPin,a.LOW) #2 small
				sleep(0.004)
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
#		else:
#			while True:
#				a.digitalWrite(MyPin,a.LOW)

		#except: #if Arduino Fails to Connect
				#print("\n\nFailed to connect...\n\n")

