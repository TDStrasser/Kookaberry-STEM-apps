# File name: 
__name__ = 'STELR_LxUV'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 11 October 2020
# Date last modified: 4 December 2023 - updated to use ADC.read_u16() function
# MicroPython Version: 1.12 for the Kookaberry V4-05
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# Measures visible and UV light intensities using VEML7700 and analogue UV sensors
# Measurements are taken whenever button B is pressed and the values logged
# This allows changing of glass panels between comparative measurements
# If a sensor is not present then a default value (-100) is recorded for that sensor.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: VEML sensor plugged into P3, UV sensor into P4
# /lib files: Kapputilspy, veml7700.py, screenplot.py
# /root files: Kappconfig.cfg or Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: GraphCSV - converts CSV files to a html Graph page
#------------------------------------------
# Begin code
# Initial conditions

from machine import I2C, Pin, ADC
import kooka, fonts, time, screenplot
from veml7700 import *
from Kapputils import config    # module to read the configuration file
import screenplot    # plots trend graphs on the Kookaberry's display
from math import log10

disp = kooka.display    # initialise the OLED display
params = config('Kookapp.cfg')   # read the configuration file
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]

# set up the datalogging file
fname = __name__ + '.CSV'
f = open(fname, 'w+')
f.write('No.,Lux,UVI\n')    # Write the heading line
f.close()    # Closes the file
# Set up the sensors
samples = [-100] * 2    # The light measurements
sstrs = ['- '] * 2    # String renditions of measurements
i2c = I2C(sda=Pin('PA9'), scl=Pin('PA10'), freq=50000)    # Note Gravity and Quokka boards have opposite SCL and SDA - set for Quokka
if len(i2c.scan()) is 0:    # check for any I2c response
    i2c = I2C(scl=Pin('PA9'), sda=Pin('PA10'), freq=50000)    # if none swap pins
lx_ok = False

uv_pin = 'P5'    # input port for analogue UV sensor
uv_sensor = ADC(uv_pin)

def val2str(v):    # Render value as string
    if v <= -50: return('- ')    # Invalid values
    else: return ('%0.1f' % v)    # Render as string

# Set up the plotting areas
plot = [0] * 2    # array of two plots
plot[0] = screenplot.area(disp, 8, 10, 52, 36)    # The area on the display for the trend plots
plot[1] = screenplot.area(disp, 67, 10, 52, 36)
trends = [0] * len(samples)    # One trend for each sensor
trends[0] = screenplot.trend(plot[0], 10, 0, 100)    # Scale Lux trend
trends[1] = screenplot.trend(plot[1], 10, -1, 10)    # Scale UVI trend
trends[0].value(0)    # Make the first data point zero so it will plot the first measurement
trends[1].value(0)

m_ctr = 0    # Measurement counter for the logging file

while not kooka.button_a.was_pressed():
# Read and process the sensor, update the logger
    if kooka.button_b.was_pressed():    # Take measurements when Button B pressed
        samples = [-100] * 2    # Defaults to sensor not present data
        m_ctr += 1
        # Handle the visible light sensor
        sensors = i2c.scan()    # scan the I2C bus for addresses
        if 0x10 in sensors: # VEML7700 sensor detect
            timeout = 5
            while not lx_ok and timeout:    # Try to connect with IR sensor
                try:
                    lx_sensor = VEML7700(address=0x10, i2c=i2c, it=100, gain=1/8)
                    lx_ok = True
                except:
                    timeout -= 1
                    lx_ok = False
                    print(lx_ok, timeout)
                    time.sleep_ms(500)
            if lx_ok:    # get the light reading
               samples[0] = lx_sensor.read_lux()
               
        else: lx_ok = False
        # Handle the UV sensor
        samples[1] = max(0,uv_sensor.read_u16() * 3300 / 65535 * 0.0102 - 1.0578) 
#        print(uv_sensor.read())   
        # Convert to UV index per sensor data
        for i in range(0,len(samples)):    # For each sensor
            sstrs[i] = val2str(samples[i])    # Render as string
        trends[0].value(log10(max(samples[0],1))/log10(120000)*100)   # Log scale for Lux
        trends[1].value(log10(max(samples[1],0.1))/log10(11)*10) # Log scale
        
        # Update the logging file
        f = open(fname, 'a+')    # Append to the logging file
        logstr = '%3d,%s\n' % (m_ctr,','.join(sstrs))
        f.write(logstr)    # Write the log data
        f.close()    # Closes the file
        print("/*%s*/" % ",".join(sstrs))    # Serial Studio compatible console ouput

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono6x7)
    disp.text('%s' % __name__, 0, 6)
    disp.text('A-exit', 0, 63)
    disp.text('B-meas', 86, 63)
    disp.text('M:%2.0d' % m_ctr, 50, 63)
    disp.setfont(fonts.mono5x5)
    disp.text('%s %s %s' % ('P3',uv_pin, id), 80, 6)
    if lx_ok or m_ctr == 0: disp.text('L: %sLux' % sstrs[0], 6, 54)
    else: disp.text('No sensor', 6, 54)
    disp.text('UVI: %s' % sstrs[1], 80, 54)
    for i in range(0,len(trends)): 
        plot[i].draw_area()
        trends[i].draw_trend(plot[i])
    disp.show()
    time.sleep_ms(500)

        
# Clean up and exit


