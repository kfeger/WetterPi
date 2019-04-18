#!/usr/bin/python
#  -*- coding: utf-8 -*-
#
# Screen für schöne große Wetteranzeige
#
#
import sys
import os
import paho.mqtt.client as mqtt # # pip install paho-mqtt
import time
from time import localtime, strftime
import datetime
from bme280 import * #wget -O bme280.py http://bit.ly/bme280py


# von Sensor
TempKueche = 0
FeuchteKueche = 0
DruckKueche = 0


# MQTT starten
client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

#client.tls_insecure_set(true)
client.username_pw_set("kuechensensor", "debpasswd")
client.will_set("19a/kueche/lastwill", "1", qos=0, retain=True)
try:
    client.connect("192.168.2.13", 1883, 90)
except:
    print "Nicht mit mqtt verbunden"
    quit()

#print "Mit mqtt verbunden"
#while 1:
(TempKueche, DruckKueche, FeuchteKueche) = readBME280All(0x76)
# publish(topic, payload=None, qos=0, retain=False)
client.publish("19a/kueche/temperatur", str(round(TempKueche, 1)), 0, True) 
client.publish("19a/kueche/druck", str(round(DruckKueche, 1)), 0, True) 
client.publish("19a/kueche/feuchte", str(round(FeuchteKueche, 1)), 0, True) 
client.publish("19a/kueche/lastwill", "0", 0, False)
'''
print "19a/kueche/temperatur", round(TempKueche,1)   
print "19a/kueche/druck", round(DruckKueche,1)   
print "19a/kueche/feuchte", round(FeuchteKueche,1)   
print "19a/kueche/lastwill", "0"
''' 
time.sleep (1)
client.disconnect()
time.sleep (1)
quit()

    
