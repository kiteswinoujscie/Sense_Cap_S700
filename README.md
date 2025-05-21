# Sense_Cap_S700
Sense Cap S700 weewx driver

Copyright 2025 Rafał Suchecki
Distributed under terms of the GPLv3

This is a driver for weewx that collects data from Sense Cap weather stations
using the Sense Cap S700 control module.


===============================================================================
Pre-requisites

- weewx (see weewx.com for details)

sudo apt-get install weewx

- the minimalmodbus python package

sudo pip install minimalmodbus


===============================================================================
Installation

1) download the driver

wget -O weewx-cm1.zip https://github.com/kiteswinoujscie/Sense_Cap_S700/archive/master.zip

2) install the driver

wee_extension --install weewx-cm1.zip

3) configure the driver

wee_config --reconfigure

4) start weewx

sudo /etc/init.d/weewx start
