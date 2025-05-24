# Sense_Cap_S700
Sense Cap S700 weewx driver

Copyright 2025 Rafał Suchecki
Distributed under terms of the GPLv3

This is a driver for weewx that collects data from Sense Cap weather stations
using the Sense Cap S700 control module via RS485


===============================================================================
Pre-requisites

- weewx (see weewx.com for details)

sudo apt-get install weewx

- the minimalmodbus python package

sudo pip install minimalmodbus


===============================================================================
Installation

1) cd /tmp
2) download the driver
wget https://github.com/kiteswinoujscie/Sense_Cap_S700/archive/refs/heads/main.zip
2) unzip Sense_Cap_S700-main.zip
3) cd /Sense_Cap_S700-main
4) cp sensecap.py /usr/share/weewx/weewx/drivers sensecap.py
6) edit file weewx.conf and add:<br>

    [Station]<br?
       station_type = SenseCAP
    [SenseCAP]
    driver = weewx.drivers.sensecap
    device = /dev/ttyUSB0
    baudrate = 9600
    timeout = 2

8) start weewx

sudo /etc/init.d/weewx start
