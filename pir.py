#!/usr/bin/python
#  -*- coding: utf-8 -*-
#
# Backlight-Steuerung
#
#
import RPi.GPIO as GPIO
import rpi_backlight as screen
from time import sleep
import datetime
import time

GPIO.setmode(GPIO.BCM)

SwitchDisplay = 0
COUNT = 300 #5 Minuten
DisplayOffCount = COUNT
PIRPin = 17
 
def PIRChange(channel):
    global SwitchDisplay, DisplayOffCount

    if GPIO.input(PIRPin) == GPIO.LOW:
        SwitchDisplay = 0
        DisplayOffCount = COUNT
        #print 'Tick 1-0 um ' + datetime.datetime.now().strftime("%H:%M:%S")
        
    else:
        SwitchDisplay = 1
        print 'Tick 0-1 um ' + datetime.datetime.now().strftime("%H:%M:%S")
        if (screen.get_power() != True):
            screen.set_power(True)
            screen.set_brightness(255, smooth=True, duration=3)
        DisplayOffCount = COUNT

GPIO.setup(PIRPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(PIRPin, GPIO.BOTH, callback = PIRChange, bouncetime = 50)
screen.set_power(True)
screen.set_brightness(255)

#print 'Dim nach %d Sekunden, Aus nach %d Sekunden' % (COUNT/3, COUNT)

while 1:
    sleep(1)
    if(DisplayOffCount > 0):
        DisplayOffCount = DisplayOffCount-1
    
    if(SwitchDisplay == 0):
        if(DisplayOffCount == 0):
            screen.set_power(False)
        elif(DisplayOffCount == COUNT/3):
            screen.set_brightness(32, smooth=True, duration=3)
    else:
        if(screen.get_power() == False):
            screen.set_power(True)
        if (screen.get_actual_brightness() < 255):
            screen.set_brightness(255, smooth=True, duration=2)
