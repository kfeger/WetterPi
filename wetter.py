#!/usr/bin/python
#  -*- coding: utf-8 -*-
#
# Screen für schöne große Wetteranzeige
#
#
from Tkinter import *
import ttk
import locale
import sys
import os
import paho.mqtt.client as mqtt # # pip install paho-mqtt
import urllib2
import time
from time import localtime, strftime
import datetime
from astral import Astral, Location, GoogleGeocoder # pip install astral
from SunTime import *
from bme280 import * #wget -O bme280.py http://bit.ly/bme280py
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
from PIL import Image, ImageTk, ImageOps # # sudo pip install Pillow, sudo apt-get install python-imaging, sudo apt-get install python-imaging-tk
#from resizeimage import resizeimage #sudo pip install python-resize-image
import json
import requests
#import rrdtool
import ConfigParser
import urllib2

logger = logging.getLogger(__name__)

#Sonnenstand
Sunrise = 0
Sunset = 0
SunriseT = 0
SunsetT = 0
SunriseLong = 0
SunsetLong = 0
Hell = 0
SunCount = 0

#Wetter
WeatherCounter = 359
IconPrefix = '/home/pi/Pictures/icons/64/'
WetterImageSize = 100, 100
WetterTagFont = ("Helvetica", 16, "bold")
WetterZahlFont = ("Helvetica", 18, "bold")

#--------------------- Anfang Daten von MQTT ---------------------

TempCarport = 99.9
DruckCarport = 0
DruckCarportvor3h = 0  # der Druck vor 15 Minuten für die Tendenz
DruckCarportvor3hNew = 1 # Beginn der Tendenzberechnung
DruckDelta = 0
DruckDeltaFirst = 1
FeuchteCarport = 0
VoltCarport = 0
WillCarport = 1

TempFront = 0
WillFront = 1
VoltFront = 0

ShowState = 1   # hier wird entschieden, welche der folgenden Daten angezeigt werden
ShowState0 = 0

TempSchlafzimmer = 0
FeuchteSchlafzimmer = 0
VoltSchlafzimmer = 0
WillSchlafzimmer = 0

TempWohnzimmer = 0
FeuchteWohnzimmer = 0
VoltWohnzimmer = 0
WillWohnzimmer = 0

TempKeller = 0
FeuchteKeller = 0
VoltKeller = 0
WillKeller = 0

TempKueche = 0
FeuchteKueche = 0
DruckKueche = 0
WillKueche = 0
#--------------------- Ende Daten von MQTT ---------------------

# von Sensor
TempKuecheS = 0
FeuchteKuecheS = 0
DruckKuecheS = 0

# Fonts
BigTimeFont = ("Helvetica", 72, "bold")
VeryBigFont = ("Helvetica", 52, "bold")
CaptionFont =  ("Helvetica", 48, "bold")
BigFont = ("Helvetica", 22, "bold")
SmallFont = ("Helvetica", 18, "normal")
SmallLittleFont = ("Helvetica", 14, "normal")
LittleFont = ("Helvetica", 5, "normal")

#Display
XMax = 799
XMin = 0
YMax = 599
YMin = 0
HumW = 280
TempW = 250
TempH = 80
HumH = 80

# Allgemeines
SecCount = 0
FlipColor = 0
Background = 'black'
#WiFi
Response = 0


'''
#------------------ Konfiguration --------------------------------

def DoConfig():
    
    global pwHeaterLZ
    global PeriodeLZ
    global Kosten
    global kWh
    global Power
    global debug

    if not os.path.exists('/home/pi/wetter.conf'):
        print 'keine conf'
        configfile = open('/home/pi/wetter.conf', 'w')
        config = ConfigParser.ConfigParser()
        config.add_section('Kosten')
        config.add_section('Zeiten')
        config.set('Kosten', 'Kosten', '0.0')
        config.set('Kosten', 'pro_kWh', '0.25')
        config.set('Kosten', 'Leistung', '0.5')
        config.set('Zeiten', 'HeizungLZ', '0.0')
        config.set('Zeiten', 'PeriodeLZ', '0.0')
        config.set('Debug', 'debug', '1')
        with open('/home/pi/wetter.conf', 'wb') as configfile:
            config.write(configfile)
            configfile.close()
    else:
        config = ConfigParser.ConfigParser()
        config.read('/home/pi/wetter.conf')
        Kosten = config.getfloat('Kosten', 'Kosten')
        kWh = config.getfloat('Kosten', 'pro_kWh')
        Power = config.getfloat('Kosten', 'Leistung')
        pwHeaterLZ = config.getfloat('Zeiten', 'HeizungLZ')
        PeriodeLZ = config.getfloat('Zeiten', 'PeriodeLZ')
        debug = config.getint('Debug', 'debug')
 
#----------------------------------------------------------------------

def SaveConfig():
    global pwHeaterLZ
    global PeriodeLZ
    global Kosten
    global kWh
    global Power
    global debug

    config = ConfigParser.ConfigParser()
    config.read('/home/pi/wetter.conf')
    config.set('Kosten', 'Kosten', str(Kosten))
    config.set('Kosten', 'pro_kWh', str(kWh))
    config.set('Kosten', 'Leistung', str(Power))
    config.set('Zeiten', 'HeizungLZ', str(pwHeaterLZ))
    config.set('Zeiten', 'PeriodeLZ', str(PeriodeLZ))
    config.set('Debug', 'debug', str(debug))
    with open('/home/pi/wetter.conf', 'wb') as configfile:
        config.write(configfile)
        configfile.close()
'''

#----------------- MQTT ---------------------------------------
def on_connect(client, userdata, rc, test):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("19a/carport/#")
    client.subscribe("19a/front/#")
    client.subscribe("19a/schlafzimmer/#")
    client.subscribe("19a/wohnzimmer/#")
    client.subscribe("19a/keller/#")
    client.subscribe("19a/kueche/#")

def on_message(client, userdata, msg):

    global TempCarport
    global DruckCarport, DruckCarportvor3h, DruckCarportvor3hNew
    global FeuchteCarport
    global WillCarport
    global VoltCarport
    
    global TempFront
    global VoltFront
    global WillFront
    
    global TempSchlafzimmer
    global VoltSchlafzimmer
    global FeuchteSchlafzimmer
    global WillSchlafzimmer
    
    global TempWohnzimmer
    global VoltWohnzimmer
    global FeuchteWohnzimmer
    global WillWohnzimmer
    
    global TempKeller
    global VoltKeller
    global FeuchteKeller
    global WillKeller

    global TempKueche
    global FeuchteKueche
    global WillKueche

    
    # Carport
    if (msg.topic == "19a/carport/lastwill"):
        WillCarport = int(str(msg.payload).strip())
    if (msg.topic == "19a/carport/temperatur"):
        TempCarport = float(str(msg.payload).strip())
    if (msg.topic == "19a/carport/feuchte"):
        FeuchteCarport = float(str(msg.payload).strip())
    if (msg.topic == "19a/carport/druck"):
        DruckCarport = float(str(msg.payload).strip())
        if (DruckCarportvor3hNew == 1):
            DruckCarportvor3h = DruckCarport
            DruckCarportvor3hNew = 0
    if (msg.topic == "19a/carport/cpusupply"):
        VoltCarport = round(float(str(msg.payload).strip())/1000, 1)
    
    # Front
    if (msg.topic == "19a/front/lastwill"):
        WillFront = int(str(msg.payload).strip())
    if (msg.topic == "19a/front/temperatur"):
        TempFront = float(str(msg.payload).strip())
    if (msg.topic == "19a/front/cpusupply"):
        VoltFront = round(float(str(msg.payload).strip())/1000, 1)
    
    # Schlafzimmer
    if (msg.topic == "19a/schlafzimmer/lastwill"):
        WillSchlafzimmer = int(str(msg.payload).strip())
    if (msg.topic == "19a/schlafzimmer/temperatur"):
        TempSchlafzimmer = float(str(msg.payload).strip())
    if (msg.topic == "19a/schlafzimmer/feuchte"):
        FeuchteSchlafzimmer = float(str(msg.payload).strip())
    if (msg.topic == "19a/schlafzimmer/cpusupply"):
        VoltSchlafzimmer = round(float(str(msg.payload).strip())/1000, 1)
    
    # Wohnzimmer
    if (msg.topic == "19a/wohnzimmer/lastwill"):
        WillWohnzimmer = int(str(msg.payload).strip())
    if (msg.topic == "19a/wohnzimmer/temperatur"):
        TempWohnzimmer = float(str(msg.payload).strip())
    if (msg.topic == "19a/wohnzimmer/feuchte"):
        FeuchteWohnzimmer = float(str(msg.payload).strip())
    if (msg.topic == "19a/wohnzimmer/cpusupply"):
        VoltWohnzimmer = round(float(str(msg.payload).strip())/1000, 1)
    
    # Keller
    if (msg.topic == "19a/keller/lastwill"):
        WillKeller = int(str(msg.payload).strip())
    if (msg.topic == "19a/keller/temperatur"):
        TempKeller = float(str(msg.payload).strip())
    if (msg.topic == "19a/keller/feuchte"):
        FeuchteKeller = float(str(msg.payload).strip())
    if (msg.topic == "19a/keller/cpusupply"):
        VoltKeller = round(float(str(msg.payload).strip())/1000, 1)

    # Kueche
    if (msg.topic == "19a/kueche/lastwill"):
        WillKueche = int(str(msg.payload).strip())
    if (msg.topic == "19a/kueche/temperatur"):
        TempKueche = float(str(msg.payload).strip())
    if (msg.topic == "19a/kueche/feuchte"):
        FeuchteKueche = float(str(msg.payload).strip())

        
#------------------- Label updaten --------------------------------------
def GetImage(file, size):
    try:
        oimage = Image.open(file)
    except:
        oimage = Image.open('/home/pi/Pictures/Ups.png')
    image = ImageOps.fit(oimage, size, Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    image.close()
    return photo

#Wetter
def GetOWM():       #OpenWeatherMap
    global WIm0, WIm1, WIm2, WIm3
    global logger
    logger.info("OpenWeatherMap Beginn")
    
    OWMIconPrefix = 'http://openweathermap.org/img/w/'    
    Wochentage = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
    try:
        response = requests.get("http://api.openweathermap.org/data/2.5/forecast/daily?q=Dresden,DE&mode=json&units=metric&cnt=4&appid=d8d6936d60093d03c1d425f34fc09338")
        wetter = response.json()
        Tag0.config(text='Heute')
        Wetter0.config(text=str(int(round(wetter['list'][0]['temp']['day']))) + '/' + str(int(round(wetter['list'][0]['temp']['night']))))
        WIm0 = GetImage(urllib2.urlopen(OWMIconPrefix + wetter['list'][0]['weather'][0]['icon'] + '.png'), WetterImageSize)
        WIcon0.config(image=WIm0)
        Tag1.config(text=Wochentage[time.localtime(wetter['list'][1]['dt']).tm_wday])
        Wetter1.config(text=str(int(round(wetter['list'][1]['temp']['day'])))+ '/' + str(int(round(wetter['list'][1]['temp']['night']))))
        WIm1 = GetImage(urllib2.urlopen(OWMIconPrefix + wetter['list'][1]['weather'][0]['icon'] + '.png'), WetterImageSize)
        WIcon1.config(image=WIm1)
        Tag2.config(text=Wochentage[time.localtime(wetter['list'][2]['dt']).tm_wday])
        Wetter2.config(text=str(int(round(wetter['list'][2]['temp']['day'])))+ '/' + str(int(round(wetter['list'][2]['temp']['night']))))
        WIm2 = GetImage(urllib2.urlopen(OWMIconPrefix + wetter['list'][2]['weather'][0]['icon'] + '.png'), WetterImageSize)
        WIcon2.config(image=WIm2)
        Tag3.config(text=Wochentage[time.localtime(wetter['list'][3]['dt']).tm_wday])
        Wetter3.config(text=str(int(round(wetter['list'][3]['temp']['day'])))+ '/' + str(int(round(wetter['list'][3]['temp']['night']))))
        WIm3 = GetImage(urllib2.urlopen(OWMIconPrefix + wetter['list'][3]['weather'][0]['icon'] + '.png'), WetterImageSize)
        WIcon3.config(image=WIm3)
        logger.info("OpenWeatherMap Ende")
    except:
        logger.error("OpenWeatherMap Fehler")


# Sonne
def SunValues():
    global Sunrise, Sunset, SunriseT, SunsetT, SunriseLong, SunsetLong, Hell
    logger.info('SunValues Beginn')
    (Sunrise, Sunset, SunriseT, SunsetT, SunriseLong, SunsetLong, Hell) = SunUpDown(location)
    logger.info('SunValues Ende')
    
def SunLabelUpdate():
    global SunCount
    if SunCount == 0:
        SunInfo.config(text='Sonnenaufgang heute: ' + Sunrise)
    elif SunCount == 1:
        SunInfo.config(text='Sonnenuntergang heute: ' + Sunset)
    elif SunCount == 2:
        SunInfo.config(text='Sonnenaufgang morgen: ' + SunriseT)
    elif SunCount == 3:
        SunInfo.config(text='Sonnenuntergang morgen: ' + SunsetT)
    else:
        SunCount = 4
    SunCount = SunCount + 1
    if SunCount > 3:
        SunCount = 0


def update_label():
    global TempCarport, DruckCarport, FeuchteCarport, VoltCarport, WillCarport
    global TempFront, VoltFront, WillFront
    global TempSchlafzimmer, FeuchteSchlafzimmer, WillSchlafzimmer, VoltSchlafzimmer
    global TempWohnzimmer, FeuchteWohnzimmer, WillWohnzimmer, VoltWohnzimmer
    global TempKeller, FeuchteKeller, WillKeller, VoltKeller
    global TempKuecheS, FeuchteKuecheS, DruckKuecheS
    global ShowState

    #(TempKuecheS, DruckKuecheS, FeuchteKuecheS) = readBME280All(0x76)
    #TempKuecheSVal.config(text=str(round(TempKuecheS, 1)) + u'°C', fg = 'white')
    #FeuchteKuecheSVal.config(text=str(int(round(FeuchteKuecheS, 0))) + u' %rH', fg = 'white')
    #TimeNow.config(text = datetime.datetime.now().strftime("%H:%M:%S") + '  ' + str(IP))    
    
    if (WillCarport == 0):
        CarportText.config (text=u'Carport', fg = 'lightblue')
        TempCarportVal.config(text=str(TempCarport) + u'°C', fg = 'lightblue')
        FeuchteCarportVal.config(text=str(int(round(FeuchteCarport, 0))) + u' %rH', fg = 'lightblue')
        DruckCarportVal.config(text=str(round(DruckCarport, 1)) + u'hPa', fg = 'white')
    else:
        CarportText.config (text=u'Carport', fg = 'red')
        TempCarportVal.config(text=str(TempCarport) + u'°C', fg = 'red')
        FeuchteCarportVal.config(text=str(int(round(FeuchteCarport, 0))) + u' %rH', fg = 'red')
        DruckCarportVal.config(text=str(round(DruckCarport, 1)) + u'hPa', fg = 'red')

def UpdateVarialeData ():
    #print ("ShowState = " , ShowState)
    if(ShowState0 == 0):
        if (WillSchlafzimmer == 0):
            if (VoltSchlafzimmer < 2.4):
                VariableText0.config (text=u'Schlafz.', fg = 'yellow')
                TempVariableVal0.config(text=str(TempSchlafzimmer) + u'°C', fg = 'yellow')
                FeuchteVariableVal0.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'yellow')
            else:
                VariableText0.config (text=u'Schlafz.', fg = 'white')
                TempVariableVal0.config(text=str(TempSchlafzimmer) + u'°C', fg = 'white')
                FeuchteVariableVal0.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'white')
        else:
            VariableText0.config (text=u'Schlafz.', fg = 'red')
            TempVariableVal0.config(text=str(TempSchlafzimmer) + u'°C', fg = 'red')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'red')
    elif(ShowState0 == 1):
        if (WillWohnzimmer == 0):
            VariableText0.config (text=u'Wohnz.', fg = 'white')
            TempVariableVal0.config(text=str(TempWohnzimmer) + u'°C', fg = 'white')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteWohnzimmer, 0))) + u' %rH', fg = 'white')
        else:
            VariableText0.config (text=u'Wohnz.', fg = 'red')
            TempVariableVal0.config(text=str(TempWohnzimmer) + u'°C', fg = 'red')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteWohnzimmer, 0))) + u' %rH', fg = 'red')
    elif(ShowState0 == 2):
        if (WillKeller == 0):
            VariableText0.config (text=u'Keller', fg = 'white')
            TempVariableVal0.config(text=str(TempKeller) + u'°C', fg = 'white')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteKeller, 0))) + u' %rH', fg = 'white')
        else:
            VariableText0.config (text=u'Keller', fg = 'red')
            TempVariableVal0.config(text=str(TempKeller) + u'°C', fg = 'red')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteKeller, 0))) + u' %rH', fg = 'red')
    elif(ShowState0 == 3):
        if (WillKueche == 0):
            VariableText0.config (text=u'Küche', fg = 'white')
            TempVariableVal0.config(text=str(TempKueche) + u'°C', fg = 'white')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteKueche, 0))) + u' %rH', fg = 'white')
        else:
            VariableText0.config (text=u'Küche', fg = 'red')
            TempVariableVal0.config(text=str(TempKueche) + u'°C', fg = 'red')
            FeuchteVariableVal0.config(text=str(int(round(FeuchteKueche, 0))) + u' %rH', fg = 'red')
    # -------------------------------------------
    if(ShowState == 0):
        if (WillSchlafzimmer == 0):
            if (VoltSchlafzimmer < 2.4):
                VariableText.config (text=u'Schlafz.', fg = 'yellow')
                TempVariableVal.config(text=str(TempSchlafzimmer) + u'°C', fg = 'yellow')
                FeuchteVariableVal.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'yellow')
            else:
                VariableText.config (text=u'Schlafz.', fg = 'lightblue')
                TempVariableVal.config(text=str(TempSchlafzimmer) + u'°C', fg = 'lightblue')
                FeuchteVariableVal.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'lightblue')
        else:
            VariableText.config (text=u'Schlafz.', fg = 'red')
            TempVariableVal.config(text=str(TempSchlafzimmer) + u'°C', fg = 'red')
            FeuchteVariableVal.config(text=str(int(round(FeuchteSchlafzimmer, 0))) + u' %rH', fg = 'red')
    elif(ShowState == 1):
        if (WillWohnzimmer == 0):
            VariableText.config (text=u'Wohnz.', fg = 'lightblue')
            TempVariableVal.config(text=str(TempWohnzimmer) + u'°C', fg = 'lightblue')
            FeuchteVariableVal.config(text=str(int(round(FeuchteWohnzimmer, 0))) + u' %rH', fg = 'lightblue')
        else:
            VariableText.config (text=u'Wohnz.', fg = 'red')
            TempVariableVal.config(text=str(TempWohnzimmer) + u'°C', fg = 'red')
            FeuchteVariableVal.config(text=str(int(round(FeuchteWohnzimmer, 0))) + u' %rH', fg = 'red')
    elif(ShowState == 2):
        if (WillKeller == 0):
            VariableText.config (text=u'Keller', fg = 'lightblue')
            TempVariableVal.config(text=str(TempKeller) + u'°C', fg = 'lightblue')
            FeuchteVariableVal.config(text=str(int(round(FeuchteKeller, 0))) + u' %rH', fg = 'lightblue')
        else:
            VariableText.config (text=u'Keller', fg = 'red')
            TempVariableVal.config(text=str(TempKeller) + u'°C', fg = 'red')
            FeuchteVariableVal.config(text=str(int(round(FeuchteKeller, 0))) + u' %rH', fg = 'red')
    elif(ShowState == 3):
        if (WillKueche == 0):
            VariableText.config (text=u'Küche', fg = 'lightblue')
            TempVariableVal.config(text=str(TempKueche) + u'°C', fg = 'lightblue')
            FeuchteVariableVal.config(text=str(int(round(FeuchteKueche, 0))) + u' %rH', fg = 'lightblue')
        else:
            VariableText.config (text=u'Küche', fg = 'red')
            TempVariableVal.config(text=str(TempKueche) + u'°C', fg = 'red')
            FeuchteVariableVal.config(text=str(int(round(FeuchteKueche, 0))) + u' %rH', fg = 'red')

def UpdateDruck():
    global DruckCarportvor3h, DruckCarportvor3hNew, DruckDelta, DruckDeltaFirst
    logger.info('UpdateDruck Beginn')
    if(DruckDeltaFirst == 0):
        DruckDelta = DruckCarport - DruckCarportvor3h
        DruckDeltaVal.config(text=u'DeltaP3h ist ' + str(round(DruckDelta, 1)) + u'hPa', fg = 'white')
        DruckCarportvor3h = DruckCarport
        if (DruckDelta > 3.0):
            DruckIcon.config(image=DruckSteigtStark)
        elif (DruckDelta > 1.0):
            DruckIcon.config(image=DruckSteigt)
        elif (DruckDelta < -3.0):
            DruckIcon.config(image=DruckFaelltStark)
        elif (DruckDelta < -1.0):
            DruckIcon.config(image=DruckFaellt)
        else:
            DruckIcon.config(image=DruckGleich)
    else:
        DruckDeltaFirst = 0
        logger.info('Erster Durchgang, keine Diff. berechnen')
    logger.info('UpdateDruck Ende')

def TimerTick():
    global SecCount, FlipColor
    global DruckCarport, DruckCarportvor3h
    global ShowState, ShowState0
    
    if ((SecCount % 1800) == 0): #alle 30 Minuten
        GetOWM()    
        SunValues()
        Response = os.system("ping -c 1 " + "192.168.2.1")
        if (Response == 0):
            WiFi.config(image = WiFiOn)
            logger.info("Netzwerk ok")
        else:
            WiFi.config(image = WiFiOff)
            logger.error("Netzwerkfehler")
            
    if ((SecCount % 60) == 0): #jede Minuten
        update_label()
        
    if ((SecCount % 3) == 0): #alle 3 Sekunden
        SunLabelUpdate()
        
    if ((SecCount % 10) == 0):  #alle 10 Sekunden
        ShowState = ShowState + 1
        if(ShowState >= 4):
            ShowState = 0
        ShowState0 = ShowState0 + 1
        if(ShowState0 >= 4):
            ShowState0 = 0
        UpdateVarialeData()

    if (((SecCount % 10800) == 0) and (DruckCarportvor3hNew == 0)): # alle 3 Stunden
        UpdateDruck()

    if (FlipColor == 0): # jede Sekunde
        TimeNow.config(text = datetime.datetime.now().strftime("%H:%M"), fg = 'lightblue')
        FlipColor = 1
    else:
        TimeNow.config(text = datetime.datetime.now().strftime("%H:%M"), fg = 'white')
        FlipColor = 0
    SecCount = SecCount + 1 
    TimerLabel.after(1000, TimerTick)



# --------------------- Hauptprogramm Start ---------------------------------
root = Tk() # Fenster erstellen
root.wm_attributes("-fullscreen", True)
root.wm_title("Raspberry Pi GUI") # Fenster Titel
root.config(background = 'black') # Hintergrundfarbe des Fensters, grau
root.config(cursor="none")

# Edgar holen
EdgarP = ImageTk.PhotoImage(Image.open('Pictures/Edgar50.png'))
DruckGleich = ImageTk.PhotoImage(Image.open('Pictures/Stable100.png'))
DruckSteigt = ImageTk.PhotoImage(Image.open('Pictures/Up100.png'))
DruckSteigtStark = ImageTk.PhotoImage(Image.open('Pictures/UpSharp100.png'))
DruckFaellt = ImageTk.PhotoImage(Image.open('Pictures/Down100.png'))
DruckFaelltStark = ImageTk.PhotoImage(Image.open('Pictures/DownSharp100.png'))
WiFiOn = ImageTk.PhotoImage(Image.open('Pictures/WiFi40Black.png'))
WiFiOff = ImageTk.PhotoImage(Image.open('Pictures/WiFi40Red.png'))
WIm0 = WIm1 = WIm2 = WIm3 = GetImage(IconPrefix + 'ups.png', WetterImageSize)

# Timed Rotating Logger
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler("/home/pi/logs/wetter.log",
                                    when="d",
                                    interval=1,
                                    backupCount=3)
handler.setLevel(logging.INFO)

# create a logger format
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

#Ende einfacher Logger
logger.info('-------- Programm gestartet --------')

# Sonnenauf- und untergang
location = Location(('Dresden', 'Germany', 51.062229, 13.658073, 'Europe/Berlin', 0))
(Sunrise, Sunset, SunriseT, SunsetT, SunriseLong, SunsetLong, Hell) = SunUpDown(location)

# IP-Addresse
cmd = "hostname -I | cut -d\' \' -f1"
IP = str(subprocess.check_output(cmd, shell = True )).strip('\n')

# BME280
(TempKuecheS, DruckKuecheS, FeuchteKuecheS) = readBME280All(0x76)


#----------------- Fenster definieren ---------------------
#Carport
CarportText = Label(root, text='Carport', font=CaptionFont, anchor="e", bg = Background, fg = 'lightblue')
CarportText.place(x = XMin, y = YMin, height=TempH, width=TempW)

TempCarportVal = Label(root, text=str(TempCarport) + u'°C', font=VeryBigFont, anchor="e", bg = Background, fg = 'lightblue')
TempCarportVal.place(x=(XMax-HumW-TempW), y=YMin, height =TempH, width = TempW)

FeuchteCarportVal = Label(root, text=str(int(round(FeuchteCarport, 0))) + u' %rH', font=VeryBigFont, anchor="e", bg = Background, fg = 'lightblue')
FeuchteCarportVal.place(x=(XMax-HumW), y=YMin, height =HumH, width = HumW)

# # Variable Daten 1
## Variable Daten
VariableText0 = Label(root, text=u'-------', font=CaptionFont, anchor="e", bg = Background, fg = 'white')
VariableText0.place(x = XMin, y = YMin+TempH, height=TempH, width=TempW)

TempVariableVal0 = Label(root, text='--.-' + u'°C', font=VeryBigFont, anchor="e", bg = Background, fg = 'white')
TempVariableVal0.place(x=(XMax-HumW-TempW), y=YMin+TempH, height =TempH, width = TempW)

FeuchteVariableVal0 = Label(root, text='--' + u' %rH', font=VeryBigFont, anchor="e", bg = Background, fg = 'white')
FeuchteVariableVal0.place(x=(XMax-HumW), y=YMin+HumH, height =HumH, width = HumW)

# Variable Daten 2
VariableText = Label(root, text=u'-------', font=CaptionFont, anchor="e", bg = Background, fg = 'lightblue')
VariableText.place(x = XMin, y = YMin+2*TempH, height=TempH, width=TempW)

TempVariableVal = Label(root, text="--.-" + u'°C', font=VeryBigFont, anchor="e", bg = Background, fg = 'lightblue')
TempVariableVal.place(x=(XMax-HumW-TempW), y=YMin+2*TempH, height =TempH, width = TempW)

FeuchteVariableVal = Label(root, text="---" + u' %rH', font=VeryBigFont, anchor="e", bg = Background, fg = 'white')
FeuchteVariableVal.place(x=(XMax-HumW), y=YMin+2*HumH, height =HumH, width = HumW)

DruckIcon = Label(image=DruckGleich, anchor="center", bg = Background)
DruckIcon.place(x=650, y=250, height =100, width = 100)

DruckCarportVal = Label(root, text='' + u'hPa', font=SmallFont, anchor="center", bg = Background, fg = 'white')
DruckCarportVal.place (x=640, y=355, height=40, width=120)

#-------------- Wetter ------------------
XPos = 0
XPosI = XPos+50
TextW = 180
TextH = 22
YPosT = 250
YPosI = YPosT+TextH
YPosW = YPosI+100
IconHeight = 80
IconWidth = 130

WIcon0 = Label(image=WIm0, anchor="center", bg = 'black')
WIcon0.place(x=XPosI, y=YPosI, height =IconHeight, width = IconWidth)
Tag0 = Label(root, text='...bald', font=WetterTagFont, anchor="center", bg= 'black', fg = 'white')
Tag0.place(x=XPosI, y=YPosT, height =TextH, width = IconWidth)
Wetter0 = Label(root, text='...bald', font=WetterZahlFont, anchor="center", bg = 'black', fg = 'white')
Wetter0.place(x=XPosI, y=(YPosT + TextH + IconHeight), height =TextH, width = IconWidth)

WIcon1 = Label(image=WIm1, anchor="center", bg = 'black')
WIcon1.place(x=XPosI+IconWidth, y=YPosI, height =IconHeight, width = IconWidth)
Tag1 = Label(root, text='...bald', font=WetterTagFont, anchor="center", bg = 'black', fg = 'white')
Tag1.place(x=XPosI+IconWidth, y=YPosT, height =TextH, width = IconWidth)
Wetter1 = Label(root, text='...bald', font=WetterZahlFont, anchor="center", bg = 'black', fg = 'white')
Wetter1.place(x=XPosI+IconWidth, y=(YPosT + TextH + IconHeight), height =TextH, width = IconWidth)

WIcon2 = Label(image=WIm3, anchor="center", bg = 'black')
WIcon2.place(x=XPosI+2*IconWidth, y=YPosI, height =IconHeight, width = IconWidth)
Tag2 = Label(root, text='...bald', font=WetterTagFont, anchor="center", bg = 'black', fg = 'white')
Tag2.place(x=XPosI+2*IconWidth, y=YPosT, height =TextH, width = IconWidth)
Wetter2 = Label(root, text='...bald', font=WetterZahlFont, anchor="center", bg = 'black', fg = 'white')
Wetter2.place(x=XPosI+2*IconWidth, y=(YPosT + TextH + IconHeight), height =TextH, width = IconWidth)

WIcon3 = Label(image=WIm0, anchor="center", bg = 'black')
WIcon3.place(x=XPosI+3*IconWidth, y=YPosI, height =IconHeight, width = IconWidth)
Tag3 = Label(root, text='...bald', font=WetterTagFont, anchor="center", bg = 'black', fg = 'white')
Tag3.place(x=XPosI+3*IconWidth, y=YPosT, height =TextH, width = IconWidth)
Wetter3 = Label(root, text='...bald', font=WetterZahlFont, anchor="center", bg = 'black', fg = 'white')
Wetter3.place(x=XPosI+3*IconWidth, y=(YPosT + TextH + IconHeight), height =TextH, width = IconWidth)



#DruckDeltaText = Label(root, text= u'Druckdifferenz in 3 Stunden ist ', font=SmallFont, anchor='w', bg=Background, fg='white')
#DruckDeltaText.place(x=300, y=420, height= 30, width=400)
DruckDeltaVal = Label(text=u'DeltaP3h ist ' + '-.-' + u'hPa', font=SmallFont, anchor='e', bg=Background, fg='white')
DruckDeltaVal.place(x=XMax-250, y=420, height= 30, width=250)

#TimeNow = Label(root, text = datetime.datetime.now().strftime("%H:%M:%S") + '  ' + IP, font=SmallFont, anchor="se", bg = Background, fg = 'white')
#TimeNow.place(x=500, y=450, height =30, width = 300)
TimeNow = Label(root, text = datetime.datetime.now().strftime("%H:%M"), font=BigTimeFont, anchor="c", bg = Background, fg = 'lightblue')
TimeNow.place(x=41, y=400, height =80, width = 309)

SunInfo = Label(root, text = 'Here comes the sun', font=SmallFont, anchor="se", bg = Background, fg = 'white')
SunInfo.place(x=XMax-380, y=450, height =30, width = 380)

button = Button(image=EdgarP, font=BigFont, command=root.destroy)
button.place(x=0, y=440, height =40, width = 40)
WiFi = Label(image = WiFiOn)
WiFi.place(x=0, y=399, height =40, width = 40)

TimerLabel = Label(root, text = '', font=LittleFont, anchor="e", bg='black', fg='black')
TimerLabel.place(x=799, y=479, height =1, width = 1)

# ----------------- Ende Fenster definieren ------------------

# MQTT starten
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#client.tls_insecure_set(true)
client.username_pw_set("tkbuser1", "debpasswd")
client.connect("192.168.2.13", 1883, 60)

client.loop_start()

#update_label()
#update_label_10s()
GetOWM()
TimerTick()

# Tkinter starten
root.mainloop()
# am Ende...
#SaveConfig()
logger.info('-------- Programm beendet --------')
print 'Ende'

