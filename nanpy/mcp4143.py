#import sys
import time
import RPi.GPIO as GPIO
import math

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

def sleep(a):
    time.sleep(a)

# Enables step by step checking by wiring some LEDs to those 3 terminals
def wait_a_key():
    print "waiting..."
    #raw_input()

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

print "Setup"
GPIO.output(SPI_CS1, True)
GPIO.output(SPI_CS2, True)
GPIO.output(SPI_CS3, True)
GPIO.output(SPI_CLK_PIN, False)
wait_a_key()

def set_value(b, CS_NUM):
    b = "0000" "00" "{0:010b}".format(b)

    GPIO.output(CS_NUM, False)
    for x in b:
        GPIO.output(SPI_SDISDO_PIN, int(x))
        GPIO.output(SPI_CLK_PIN, True)
        #For step by step checking: sleep(1)
        GPIO.output(SPI_CLK_PIN, False)
        #For step by step checking: sleep(1)

    #wait_a_key()

    GPIO.output(CS_NUM, True)
    #sleep(0.1)
    
def set_value_by_resistance(givenResistance, cs_NUM):
    
    valueToSet = givenResistance/77.519
    valueToSet = math.floor(valueToSet)
    valueToSet = int(valueToSet)
    print('valueToSet: ' + str(valueToSet))
    set_value(valueToSet, cs_NUM)


try:
#    print('SETTING POT 1')
#    #sweep first pot
#    for i in range(129, 0, -5):
#        print 'set_value:' + str(i)
#        set_value(i, SPI_CS1)
#        sleep(0.1)
#    
#    print('SETTING POT 2')
#    #sweep second pot
#    for i in range(129, 0, -5):
#        print 'set_value:' + str(i)
#        set_value(i, SPI_CS2)
#        sleep(0.1)

    while(True):
        testVal = raw_input('Input a resistance Value: ')
        testVal = int(testVal)
        print('Setting the potentiometer to: ' + str(testVal))
        set_value_by_resistance(testVal, SPI_CS3)




    
finally:
    GPIO.cleanup()










