# File name: 
__name__ = 'STELR_IRT'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 26 September 2020
# Date last modified: 1 March 2021 added Serial Studio compatible console output
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
# Measures two temperatures using a MLX90614 IR temperature sensor
# The IR sensor measures target object temperature and the sensor's ambient temperature
# Logs the measurements into a file at an interval specified in the configuration file
# If a sensor is not present then a default value (-100) is recorded for that sensor.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: MLX90614 sensor plugged into P3
# /lib files: Kapputilspy, logger.py, screenplot.py, (mlx90614.py is embedded in the Kookaberry firmware)
# /root files: Kappconfig.cfg or Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: GraphCSV - converts CSV files to a html Graph page
#------------------------------------------
# Begin code
# Initial conditions

from machine import SoftI2C, Pin
import kooka, fonts, time, screenplot
import mlx90614
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
#import doomsday    # works out the day of the week from the date (supressed temporarily)
import screenplot    # plots trend graphs on the Kookaberry's display

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    

disp = kooka.display    # initialise the OLED display
params = config('Kookapp.cfg')   # read the configuration file
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Timer-hh:mm:ss,TAmb-degC,TObj-degC')    # Create the datalogger instance
dlog.start()    # Start the datalogger
# Set up the sensors
temps = [-100] * 2    # The temperatures
tstrs = [''] * 2    # String renditions of temperatures
i2c = SoftI2C(sda=Pin('PA9'), scl=Pin('PA10'), freq=50000)    # Note Gravity and Quokka boards have opposite SCL and SDA - set for Quokka
if len(i2c.scan()) is 0:    # check for any I2c response
    i2c = SoftI2C(scl=Pin('PA9'), sda=Pin('PA10'), freq=50000)    # if none swap pins
ir_ok = False

def val2str(v):    # Render value as string
    if v <= -50: return('-')    # Invalid values
    else: return ('%0.1f' % v)    # Render as string

ds_interval = int(params['INTV']*1000)    # milliseconds between DHT sensor reads
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples
_time_zero = time.ticks_ms()    # time at which logging began

# Set up the plotting area
plot = screenplot.area(disp, 0, 10, 128, 36)    # The area on the display for the trend plots
trends = [0] * len(temps)    # One trend for each sensor
for i in range(0,len(temps)):
    trends[i] = screenplot.trend(plot, 100, 10, 50)    # Scale each trend

while not kooka.button_a.was_pressed():
# Construct the time string
    timer_run = int(time.ticks_diff(time.ticks_ms(), _time_zero) / 1000) # seconds since beginning
    timestr = '%0.2d:%0.2d:%0.2d'% (int(timer_run/3600),int((timer_run/60)%60), int(timer_run%60))
# Read and process the sensor, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        temps= [-100,-100]    # Defaults to sensor not present data
        sensors = i2c.scan()    # scan the I2C bus for addresses
        if 0x5a in sensors: # IRT sensor detect
            timeout = 5
            while not ir_ok and timeout:    # Try to connect with IR sensor
                try:
                    ir = mlx90614.MLX90614(i2c)
                    ir_ok = True
                except:
                    timeout -= 1
                    ir_ok = False
                    print(ir_ok, timeout)
                    time.sleep_ms(500)
            if ir_ok:    # get the temperatures
               temps[0] = ir.read_ambient_temp()
               temps[1] = ir.read_object_temp()
               
        else: ir_ok = False

        for i in range(0,len(temps)):    # For each sensor
            trends[i].value(temps[i])    # Update trend data
            tstrs[i] = val2str(temps[i])    # Render as string
        logstr = '%s,%s' % (timestr,','.join(tstrs))
        dlog.update('%s,%s' % (timestr,','.join(tstrs)))    # update the string to be logged
        dlog.write()    # writes the datalogger string when next due
     # set up for next sample
        _timer_ds += ds_interval
        print("/*%s*/" % ",".join(tstrs))    # Serial Studio compatible console ouput

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono6x7)
    disp.text('%s' % __name__, 0, 6)
    disp.text('A-ex', 0, 63)
    disp.text('I:%ds' % params['INTV'], 32, 63)
    disp.text(timestr, 76, 63)
    disp.setfont(fonts.mono5x5)
    disp.text('%s %s' % ('P3', id), 104, 6)
    disp.text('TA-O:%s degC' % ", ".join(tstrs), 0, 54)
    plot.draw_area()
    for i in range(0,len(trends)): trends[i].draw_trend(plot)
    disp.show()
    time.sleep_ms(250)

        
# Clean up and exit
dlog.kill()    # disables the datalogger


