# SPS30_with_raspberry_pi

## Introduction  
My project is an air quality sensor that shows the concentration of particulate matter (PM) in the air. The sensor, a Sensirion SPS30, is controlled with the help of a Raspberry Pi Zero W through the Serial0 interface, which uses UART and the ttyAMA0 port. The Pi also sends the data from the sensor to ThingsBoard via the MQTT protocol.

## Components  
- Raspberry Pi Zero W – for controlling the sensor and sending the sensor data to ThingsBoard  
- Sensirion SPS30 – air quality sensor connected via UART

## Raspberry Pi Configuration

The Pi runs an image of Raspberry Pi OS (32-bit), which is a port of Debian Bookworm.  
**The changes from the clean install are:**  
- SSH credentials have been changed; the new username and password (the hostname remains unchanged)  
- Serial interface activated without terminal on the UART pins  
- Bluetooth disabled in `config.txt` to free the ttyAMA0 port. This provides a better connection to the sensor compared to using the miniUART, which depends on the processor clock and may be unstable.  
- Gadget mode is enabled, allowing you to connect to the Pi via USB using the mini-USB port between the mini-HDMI and the other mini-USB port. You don’t necessarily need to power it via the PowerIn port if you don’t use the sensor.  
- The Pi has a Samba shared folder named **"smb_share"**   
- Other: VNC is active on the Pi, but I don’t recommend it due to high latency.

## Code  
There are two programs used for this project on the Pi. The Python code facilitates the connection with ThingsBoard using the `tb-mqtt-client` library installed in a Python 3 virtual environment. It also controls the second program, written in C, by starting, reading, or closing it depending on actions triggered in ThingsBoard.  
The second program establishes the UART connection and communicates with the sensor, telling it what to do. This C code uses the driver written in C from this GitHub repository: [embedded-uart-sps](https://github.com/Sensirion/embedded-uart-sps/blob/master/docs/getting-started-on-the-raspberry-pi.md).  
To adapt the Python program to your ThingsBoard setup, change the values of the following variables at the start of the code with your respective values. For more details, see this link: [Pi Zero W on ThingsBoard](https://thingsboard.io/docs/devices-library/raspberry-pi-zero-w/).  
Code:  
  
```
ACCESS_TOKEN = "7tUZaVu6iZFxLUcYRc53"
THINGSBOARD_SERVER = 'demo.thingsboard.io'
```

## ThingsBoard

The custom dashboard I created is saved as **"proiectdashboard.json"**. It provides a comprehensive view of both the device and sensor data. The dashboard includes the following sections:

- **Raspberry Pi Information**  
  Displays system metrics such as:  
  - Local IP address  
  - Average system load

- **Device Information (ThingsBoard)**  
  Shows key details about the registered device:  
  - Uptime  
  - Connection status (active/inactive)  
  - Label and device type  
  - Creation timestamp

- **Sensor Data (SPS30)**  
  Provides real-time air quality measurements:  
  - Firmware version  
  - Mass concentration: PM1, PM2.5, PM10  
  - Number concentration: PM0.5, PM1, PM2.5, PM10  
  - Typical particle size

- **Control Panel**  
  Includes a button to **start** or **stop** the background process that communicates with the sensor.


## Bibliography / Resources  
**Documentation / Datasheets:**  
- [embedded-uart-sps](https://github.com/Sensirion/embedded-uart-sps/blob/master/docs/getting-started-on-the-raspberry-pi.md)  
- [Pi Zero W on ThingsBoard](https://thingsboard.io/docs/devices-library/raspberry-pi-zero-w/)  
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html)  
- [SPS30 Datasheet](https://sensirion.com/media/documents/8600FF88/64A3B8D6/Sensirion_PM_Sensors_Datasheet_SPS30.pdf)  

**Videos:**  
- [Setting Up the Pi](https://www.youtube.com/watch?v=l4VDWhKsFgs&list=LL&index=101)  
- [Samba Share Setup](https://www.youtube.com/watch?v=vrELBV-r4Aw&list=LL&index=37)  
- [Python 3 Virtual Environment](https://www.youtube.com/watch?v=Kg1Yvry_Ydk&list=LL&index=47)
