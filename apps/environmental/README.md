# Kookaberry Environmental Apps
This is a repository of MicroPython environmental sensing apps in MicroPython for use with the Kookaberry micro-computer.

These are divided into several groups as described below.

## SenseXXX Apps
This is a portfolio of apps that have basically the same structure, but each one uses a different sensor.
They all share these characteristics:
- All of them log the sensor data into a CSV (Comma Separated Variables) file that is stored in the root folder of the Kookaberry's file store
- The name of the CSV file is the same as the app in the form SenseXXX.CSV.
- They broadcasts the collected data samples over the Kookaberry's radio.  The intention is that such data is then collected and collated by the complementary SenseRx app.  This app and its description can be found in the datalogging folder of this repository.
- All the apps require the Kapputils.mpy library module to be in the Kookaberry's lib folder.  This is used to properly read the configuration file previously set by the _Config app.
- The _Config app should be used to properly set up:
  - the Kookaberry's radio channel (nominally at 83) so that all the Kookaberries participating can communicate.
  - the logging interval at which sensor data is to be sampled. This will vary with the rate at which the sensor is expected to change.
  - each Kookaberry should have a unique ID number so that it's data can be distinguished from that collected by other Kookaberries.
- The SenseXXX apps are:
  - **SenseACC** - Measure overall acceleration using the Kookaberry's inbuilt accelerometer.
    - Logs average and peak acceleration into a file at an interval specified in the Kookapp.cfg configuration file.
    - Broadcasts the average and maximum accelerationss over the packet radio in the format [ID,SHK,AccAvg,AccMax].
  - **SenseAnlg** - Measures 1 or 2 analogue signals (scales of 0 to 100, or 0 to 3.3V, or 0 to 4095 selected via button C) for signals connected to plugs **P4** and **P5**.
    - Logs the analogue readings into a file at an interval specified in Kookapp.cfg or and on significant change.
    - Broadcasts the analogue signals over the packet radio in the format [ID,Anlg,P1,P4,P5].
  - **SenseBME** - Measures temperature, relative humidity and air pressure using a BME280 sensor connected to plug **P3**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,BME,AmbTemp,RH,Press]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
  - **SenseCO2** - Measures total eCO2 in ppm (parts per million) and VOCs (Volatile Organic Compounds) in ppb (parts per billion) using a CCS811 digital gas sensor connected to plug **P3**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,CO2,VOC]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
  - **SenseDHT** - Measures temperature and humidity using a DHT11 or DHT22 sensor connected to plug **P2**.
    - Initially it attempts to detect which type of sensor is connected (DHT11 or DHT22)
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,DHT,Temp,Humid]
    - Relays sensor reading data via UART 1 (plug **P3**)
    - See the description here https://learn.auststem.com.au/app/sensedht-app/
  - **SenseDS18** - Measures temperature using a DS18B20 onewire digital temperature sensor connected to plug **P4**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,DS18B20,Temp]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
    - See the description here https://learn.auststem.com.au/app/senseds18/
  - **SenseIRT** - Measures temperature using a GY-906 non-contact infra-red digital temperature sensor connected to plug P3.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,GY906,AmbTemp,ObjTemp]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
    - Requires the library module *mlx90614.mpy* to be present in the Kookaberry's *lib* folder.
  - **SenseLight** - Measures light level using a Gravity analogue light sensor (photo-transistor) connected to plug **P5**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,Ill,Sensor Reading, Estimated Lux]
    - A calibration facility occurs first in which the user specifies the nominal lighting environment (indoor light, overcast, clear sky, direct sun)
    - There is no way to tell if a sensor is not present.
  - **SenseLux** - Measures light level in Lux using a VEML7700 digital light sensor connected to plug **P3**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,Lux,Light]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
  - **SenseNTCT** - Measures temperature using a negative temperature coefficient thermistor (NTCT) sensor connected to plug **P5**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,NTCT,Temp]
    - There is no way to tell if a sensor is not present.
  - **SensePT100** - Measures temperature using a high-temperature PT100 resistance temperature detector (RTD) sensor connected to plug **P4**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,PT10,Temp]
    - There is no way to tell if a sensor is not present.
    - Requires the library module *pt100.mpy* to be present in the Kookaberry's *lib* folder.
  - **SenseSDS** - Measures air particles using a SDS011 particulate sensor connected to plug **P3**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,SDS011,PM2.5,PM10]
    - If the sensor is not present or not answering a prompt is displayed. Logging suspends until a sensor is present.
    - Requires the library module *sds011.mpy* to be present in the Kookaberry's *lib* folder.
    - See the description here https://learn.auststem.com.au/app/sensesds/
  - **SenseUV** - Measures UV light level in milliwatts/sqcm using a VEML6070 digital UV sensor connected to plug **P3**.
    - Logs the measurements into a CSV file at an interval specified in Kookapp.cfg
    - Broadcasts the sensor readings over the packet radio in the format [ID,UV,watts]
    - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
    - Requires the library module *veml6070_i2c.mpy* to be present in the Kookaberry's *lib* folder.
  - **SenseUVI** - Measures UV intensity using the GUVA-S12SD analogue sensor attached to plug **P5**.
    - Logs into a CSV file at an interval specified in Kookapp.cfg and on significant change.
    - Broadcasts the analogue signals over the packet radio in the format [ID,UVI,UV]
    - There is no way to tell if a sensor is not present.
    - See the description here https://learn.auststem.com.au/app/senseuvi/

# General Environmental Sensing Apps
These apps include:
- **Altimeter** - Calculates altitude from barometric pressure using a BMP280 or BME280  sensor connected to plug **P3**.
  - Local reference sea-level barometric pressure (known as QNH) can be adjusted using the C and D buttons. The default QNH is 1013hPa
  - A set altitude mode (pilot mode) is provided - toggle modes with the B button
  - If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
  - The configuration of the I2C scl and sda pins is also tested and swapped if necessary
- **BounceMe** - Measures instantaneous acceleration using the Kookaberry's inbuilt accelerometer.
  - Captures data for a short period selectable on the screen and when Start is pressed.
  - Buttons C and D adjust the logging period
  - Long press on button B starts logging at the end of which the graph on the display is frozen to enable viewing.
  - A short press on button B unfreezes the chart on the display.
  - Logs instantaneous acceleration into a BounceMeNN.CSV file at the full sample rate.
  - Successive captures generate separate logging files where NN is 00, 01, 02 etc.
  - Requires the library modules *Kapputils.mpy* and *kbtimer.mpy* to be present in the Kookaberry's *lib* folder.
  - A description of this app is here https://learn.auststem.com.au/app/bounceme-app/
- **Compass** - Compass using the Kookaberry's inbuilt magnetometer.  The compass needle points to magnetic North.
  - The accelerometer drives a set of cross hairs that should be kept over the compass axis.
  - The GREEN LED will show when the compass is level.
  - A "Level!" warning and RED LED is shown if the Kookaberry is not level.
  - The Kookaberry's heading is shown in degrees as is the general heading.
  - The B button moves the Kookaberry to a calibration mode. The ORANGE LED shows.
  - To calibrate rotate the Kookaberry through 360 degrees while it is level.
  - When calibration is complete (shown by a full circle) the app returns to compass mode.
  - Note that the magnetometer is sensitive to nearby ferrous metal objects which deflect the earth's magnetic field, leading to heading errors.
- **Weather** - Weather Station app that reads windspeed, wind direction and rainfall from a Shenzen Fine Offset SEN15901 sensor tree, as well as temperature, relative humidity, and barometric pressure from a BME280 sensor.
  - Component sensors are connected to the following plugs: **P4** wind vane, **P1** anemometer, **P2** rain gauge, **P3** BME280
  - The app writes a JSON-formatted data logging file *Weather.json* to the Kookaberry's file store.
  - The measurements are also transmitted as JSON-formatted messages over the Kookaberry's radio.
  - Requires the library modules *sen15901.mpy* to be present in the Kookaberry's *lib* folder.
  - A DS3231 battery clock can also be connected to plug **P3** to synchronise the time in stand-alone applications.
- **WeatherHere** - A local weather station reading temperature, absolute humidity and wind speed.
  - Temperature and Humidity using the Gravity DHT11 Sensor connected to plug **P2**.
  - Wind speed is derived from pulses read by photoelectric pulse sensor attached to an anemometer - limits have been placed to filter out improbable windspeeds.
  - The apparent temperature is calculated using equations from the Australian Bureau of Meteorology.
  - A datalogging function is provided to the file *WeatherHere.CSV* which is configured by the file Kookapp.cfg
  - A description of the weather station and app is here https://learn.auststem.com.au/app/weatherhere-app/

