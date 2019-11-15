from nanpy import ArduinoApi 
from nanpy import SerialManager
from time import sleep

led = 13
ledState = False

try:
    connection = SerialManager()
    a = ArduinoApi(connection = connection)
    print("Connection Successful..")
except:
    print("Failed to connect...")
    
#Setup the pinModes
a.pinMode(led, a.OUTPUT)

while True:
#LEDs flashing
    a.digitalWrite(led, a.LOW)
    ledState = False
    print("LED OFF")
    sleep(1)
    a.digitalWrite(led, a.HIGH)
    ledState = True
    print("LED ON")
    sleep(1)

#Set PWM Signal



#Set Potentiometers






