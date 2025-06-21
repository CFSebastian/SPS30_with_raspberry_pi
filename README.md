# SPS30_with_raspberry_pi

## Introduction  
My project is a air quality senzor, that shows the concentration of PM particles in the air. The sensor, a sensirion SPS30, is controled with the help of a Raspberry pi Zero W throw the Serial0 interface that uses UART and the ttyAMA0 port. The Pi also sends the data from the sensor to ThingsBoard via the mqtt protocol. 

## Components  
- Raspberry Pi Zero W - for controling the sensor and sendig the sensor data to ThingsBoard
- Sensirion SPS30 - air quality sensor conected via uart

## Raspberry Pi configuration

The pi runs a image of Raspberry Pi OS (32-bits), that is a port of Debian Bookwarm.  
**The changes from the clen install are**:  
- Changed ssh credentials, the new user and password are "student" (the hostname is not changed)
- Activated serial interface withowt terminal on the uart pins
- Bluetooth is deactivated from config.txt to eliberate the ttyAMA0 port, the reason beeing a beter connection to the sensor compared to the miniUart port that uses the clock from the procesor and mai be instabel.
- GadgetMode is enableled, so you can conect to the pi via usb using the miniUsb port between the mini hdmi and the other miniUsb. You dont necessary need to power it ub with via PoweIn port if you dont use the sensor.
- the pi has a samba share folde named "smb_share" with the credential for name and password "student"
- Other: the VNC is active on the pi but i dont recomanded due to the high latency

## Code 
On the pi there are 2 programs that are used for this project. The phython code is the one that facilitates the conection whit the thingborad with the help of tb-mqtt-clientlibrari instaled on a python3 virtual environment, and also controls the second code that is writen in C as achild process, starting and reding or closing it depending on the actions in thingsboard. The second code is the one establises the uart connetion and tells the sensor what tom do, this C code uses the driver writen in C drom this git repository "[embedded-uart-sps](https://github.com/Sensirion/embedded-uart-sps/blob/master/docs/getting-started-on-the-raspberry-pi.md)".

## Bibliography/Resources  
**Documentations/datasheets**:  
- [embedded-uart-sps](https://github.com/Sensirion/embedded-uart-sps/blob/master/docs/getting-started-on-the-raspberry-pi.md)
- [Pi Zero W on ThingsBoard](https://thingsboard.io/docs/devices-library/raspberry-pi-zero-w/)
- [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [SPS30 datasheet](https://sensirion.com/media/documents/8600FF88/64A3B8D6/Sensirion_PM_Sensors_Datasheet_SPS30.pdf)  **Videous**:  
- [Seting Up the Pi](https://www.youtube.com/watch?v=l4VDWhKsFgs&list=LL&index=101)
- [Samba share file](https://www.youtube.com/watch?v=vrELBV-r4Aw&list=LL&index=37)
- [Python3 venv](https://www.youtube.com/watch?v=Kg1Yvry_Ydk&list=LL&index=47)
