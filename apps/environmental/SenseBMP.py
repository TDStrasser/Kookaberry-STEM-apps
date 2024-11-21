# File name: *** RETIRED *** bmp280.py driver is too large - causes memory allocation errors
__name__ = 'SenseBMP'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 9 April 2020
# Date last modified: 4 November 2020
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
# Measure temperature using a non-contact infra-red digital temperature sensor
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [GY906,AmbTemp,ObjTemp]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: BMP280 probe plugged into P3
# /lib files: Kapputilspy, logger.py, doomsday.py, mlx90614.py
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#------------------------------------------
# Begin code
# Initial conditions

import kooka, fonts, time, ujson
from machine import I2C, Pin, RTC
from bmp280 import BMP280
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
#import doomsday    # works out the day of the week from the date (supressed temporarily)

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
params = config('Kappconfig.txt')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file
kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=40) # set up the radio
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'BMP280','T','P']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,AmbT-degC,Pressure-hPa')    # Create the datalogger instance
dlog.start()    # Start the datalogger

# Set up the BMP280 interface
dspin = 'P3'
i2c = I2C(scl=Pin('P3B'), sda=Pin('P3A'), freq=50000)
s_flag = False
valid_adx = [0x76, 0x77]    # range of potential addresses
sensors = i2c.scan()
for adx in sensors:
    if adx in valid_adx: 
        bmp = BMP280(i2c, addr=adx)
        s_flag = True
#        print('BMP280:', hex(adx))
        break

if not s_flag: 
    print('No BMP280')    # Sensor not found

temp = 0
press = 0

dsinterval = 2000
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples
txinterval = params['INTV'] * 1000
_timer_tx = time.ticks_ms() + txinterval    # timer used for radio transmissions

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        _timer_ds += dsinterval    # only take a sample every period
        t_read = False
        try:
#            print(bmp.temperature, bmp.pressure)
            temp = bmp.temperature
            press = bmp.pressure/100
            t_read = True
            sndmsg[2] = '%0.2f' % temp
            sndmsg[3] = '%0.2f' % press
#            print(t_read, timestr, sndmsg)
            dlog.update('%s,%0.1f' % (timestr,temp,press))    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due

        except:
            pass
# Send latest reading over the radio            
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += txinterval    # nex radio interval
        if t_read: kooka.radio.send(ujson.dumps(sndmsg))

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,dspin), 90, 6)
    disp.text('A-exit', 0, 62)
    disp.text('Log in %d' % dlog.log_counter, 60, 55)
    disp.text('%s' % timestr, 0, 45)
    if t_read: 
        disp.text('Amb = %0.2f C' % temp, 12, 17)
        disp.text('Obj = %0.2f hPa' % press, 12, 26)
    else: disp.text('No sensor', 0, 20)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
#        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
#            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


