# WetterPi
WetterPi ist eine Wetterstation auf Basis Raspberry Pi, IPS-Display und MQTT.
Es ist geschrieben in Python 2.7

Der MQTT-Broker ist eine VM auf dem Server auf Basis Mosquitto
Zusätzlich wird Temp/Pres/Hum-Sensor BME280 im Programm pubkueche.py
ausgelesen und über den Broker publiziert.
Das Programm pir.py steuert die Hintergrundbeleuchtung des Displays über einen
PIR-Sensor am GPIO. muss als root (sudo) gestartet werden.
