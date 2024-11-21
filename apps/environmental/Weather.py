# FILENAME: Weather.py
__name__ = 'Weather'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 4 June 2022
# DATE-MODIFIED: 24 June 2022
# VERSION: 1.0
# SCRIPT: MicroPython Version: 1.12 for the Kookaberry V4-05
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# DESCRIPTION:
# Weather Station app that reads windspeed, wind direction and rainfall from a
# Shenzen Fine Offset SEN15901 sensor tree,
# as well as temperature, relative humidity, and barometric pressure
# from a BME280 sensor
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: 
#    P4 wind vane, P1 anemometer, P2 rain gauge, P3 BME280
# /lib files: bme280.mpy
# /root files:
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS: #weather #temperature #humidity #pressure #wind #rain
# BEGIN-CODE:

# Initial conditions

import machine, kooka, fonts, time, ujson, os
import bme280
from ds3231 import DS3231
from sen15901 import SEN15901
disp = kooka.display    # initialise the OLED display
disp.print(__name__)
#disp.print('Initialising...')

# Function to check whether a file exists
def fileExists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
        
# Read the configuration parameters
fname = 'Kookapp.cfg' # The name of the configuration file
if fileExists(fname):    # Test the JSON configuration file
    f = open(fname,'rt')
    fl =f.readline()    # Reads the first line
    params = ujson.loads(fl)    # Decode the JSON dictionary
    f.close()
    disp.print('Config read')
else:
    disp.print('Run _Config first')
    disp.print('Exiting')
    time.sleep(2) # Give time for user to read the display
    raise SystemExit    # Quit the program

# The radio is kept off until needed to save power
def radio_init():    # Function turns on and initialises the radio
    global params
    kooka.radio.enable()
    chan = int(params['CHANNEL'])      # use channel from the configuration file
    baud = int(params['BAUD'])      # use data rate from the configuration file
    pwr = int(params['POWER'])      # use transmit power from the configuration file
    kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=150) # set up the radio
    
id = params['ID']    # Identifies the CubeSat

# set up the datalogging file
log_fname = __name__ + '.json'
f = open(log_fname,'w+')         # open a text file for writing
f.write('[\n')    # write JSON delimiter
f.close()

# Set up the main I2C bus containing: DS3231 @ 0x68, BME280 @ 0x77
i2c = machine.I2C(scl='PA9', sda='PA10')

# ------ Sets up the Real Time Clock --------

rtc = machine.RTC()    # Kookaberry internal Real Time Clock

# Reads an external DS3231 RTC if available and the Kookaberry's own RTC.
# Pick the one with the latest time to set the Kookaberry's RTC

ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
etime = [0]*8    # DS3231 RTC time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]

# Read the Kookaberry real time clock and decode
rtc = machine.RTC()
ktime = rtc.datetime()

# Read the external RTC
try: 
    ds3231 = DS3231(i2c)
    etime = ds3231.datetime()
    ds3231_present = True
    disp.print('DS3231 found...')
except:
    ds3231_present = False
    disp.print('DS3231 missing!')

# Decide which clock is later and more likely to be correct
k_time = e_time = int(0)
t_ptrs = [0,1,2,4,5,6]    # pointers to time tuples
for i in range(0,6):    # Make ordinals from the various times
    k_time = (k_time + ktime[t_ptrs[i]]) * 100
    e_time = (e_time + etime[t_ptrs[i]]) * 100
# print('Kooka %d, DS3231 %d' % (k_time,e_time))
# Decide which time source to use
if k_time <= e_time and ds3231_present: 
    rtc.datetime(ds3231.datetime())    # Update RTC from external RTC
    print('RTC updated from DS3231')
# Default is the RTC is the latest time so leave as is (do nothing)
else: print('RTC already correct')
# Save the time to the external RTC
if ds3231_present: ds3231.datetime(rtc.datetime())  # Set DS3231 from RTC
# print(rtc.datetime())

# ------ Sets up the sensors --------
# Sensor status strings
sensor_status = ['Fault','OK']

# Set up the BME280 sensor
bme_tags = ['Temperature','Pressure','Rel Humidity']
bme_values = [0] * len(bme_tags)
bme_units = ['deg C','hPa','%']
bme_read = False
try:
    bme = bme280.BME280(i2c=i2c)
    disp.print('BME280 found...')
    altitude = 0
except:
    bme = None
    disp.print('BME280 missing!')
    
# Function reads and processes the BME sensor data
def bme_read():
    global bme, bme_tags, bme_values, bme_units, bme_read
    # process the bme280 environmental sensor
    if bme: # only if the sensor has been initialised
        try:
            bme_values[0] = bme.values[0] # Temperature
            bme_values[1] = bme.values[1] # Pressure
            bme_values[2] = bme.values[2] # Humidity
            return True

        except:
            print('BME280 read failure')
            return False
                
# Set up the Fine Offset sensors
weather_tags = ['Windspeed','Direction','Azimuth','Rainfall']
weather_values = [0] * len(weather_tags)
weather_units = ['kph','','deg','mm']
weather_read = False

weather = SEN15901('P1','P2','P4')

# Function reads the windvane sensor and returns the wind heading
def weather_read():
    weather_values[0] = weather.windspeed # Wind speed in m/sec
    weather_values[1] = weather.direction # Wind direction
    weather_values[2] = weather.azimuth # Wind azimuth in degrees
    weather_values[3] = weather.rainfall # Total rainfall in mm
    return True

# Give time for user to read the display
time.sleep(2)    

# Define the sensor telemetry logging dictionary
sensor_data = {
    'date_time': '',
    'id' : id,
    'tag' : '',
    'value'  : 0,
    'units': ''
        }

# function that logs and transmits the sensor data
def log_data(data):
    global log_fname
    print(data)
    # Write to the local sensor logging file
    f = open(log_fname,'a+')         # open a text file for writing
    f.write('%s,\n' % ujson.dumps(data))    # write the latest record
    f.close()
    # Transmit the sensor data via radio
    radio_init()
    kooka.radio.send(ujson.dumps(data))    # send the data
    kooka.radio.disable()    # Turn the radio off to save power

tx_interval = params['INTV'] * 1000    # logging interval
_timer_tx = time.ticks_ms()    # timer that controls sensing and logging

# ------ this is the main loop --------

while not kooka.button_a.was_pressed():
# Construct the time string in ISO8601 format YYYY-MM-DDTHH:MM:SS
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%04d-%02d-%02dT%02d:%02d:%02d" % (ktime[0],ktime[1],ktime[2],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
    sensor_data['date_time'] = timestr    # timestamp the sensor data

# Read and process the sensors, send the radio messages, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += tx_interval    # only take a sample every period

        # process the bme280 environmental sensor
        if bme_read(): # only if the sensor has been successfully read
            for i in range(0, len(bme_values)):
                sensor_data['value'] = bme_values[i]
                sensor_data['tag'] = bme_tags[i]
                sensor_data['units'] = bme_units[i]
                log_data(sensor_data)
            
        # process the sen15901 weather sensors
        if weather_read(): # only if the sensor has been successfully read
            for i in range(0, len(weather_values)):
                sensor_data['value'] = weather_values[i]
                sensor_data['tag'] = weather_tags[i]
                sensor_data['units'] = weather_units[i]
                log_data(sensor_data)

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text(__name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('ID%s CH%s' % (id, params['CHANNEL']), 70, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-x', 0, 63)
    disp.text('Log in %d' % -int(time.ticks_diff(time.ticks_ms(), _timer_tx)/1000), 60, 63)
    disp.text('%s' % timestr, 0, 54)
    if bme:
        disp.text('%0.1fC %0.1f%%' % (bme_values[0],bme_values[2]), 0, 18)
        disp.text('%0.1fhPa' % bme_values[1], 0, 27)
    disp.text('Wind: %0.2fkph %s' % (weather_values[0],weather_values[1]), 0, 36)
    disp.text('Rainfall: %0.1fmm' % weather_values[3], 0, 45)
    disp.show()
