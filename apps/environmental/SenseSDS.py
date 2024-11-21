# File name: 
__name__ = 'SenseSDS'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 26 February 2020
# Date last modified: 30 November 2020
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
# Measure air particles using a SDS011 particulate sensor
# Logs the measurements into a file at an interval specified in Kookapp.cfg
# Broadcasts the sensor readings over the packet radio in the format [SDS011,PM2.5,PM10]
# If the sensor is not present or not answering a prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: SDS011 plugged into P3
# /lib files: Kapputilspy, kcpu.py, logger.py, doomsday.py, onewire.py, sds011.py
# /root files: Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json
from machine import UART
import sds011
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # works out the day of the week from the date (supressed temporarily)

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
params = config('Kookapp.cfg')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file
kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=40) # set up the radio
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'SDS011','PM2','PM10']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,PM2.5,PM10')    # Create the datalogger instance
dlog.start()    # Start the datalogger

SDSpin = 'P3'
sens_interval = 4000    # milliseconds between DHT sensor reads
uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)
dust_sensor = sds011.SDS011(uart)
sens_reading = False

_timer_sens = time.ticks_ms()    # timer used for delays and timing samples

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d-%02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        # scan for devices on the bus
        kooka.led_orange.on()    # signal attempted read
        if dust_sensor.read():
            kooka.led_orange.off()
            kooka.led_red.off()
            kooka.led_green.on()
            sens_reading = True
            pm25 = dust_sensor.pm25
            pm10 = dust_sensor.pm10
            sndmsg[2] = '%.2f' % pm25
            sndmsg[3] = '%.2f' % pm10
            print(timestr, sndmsg)
            kooka.radio.send(json.dumps(sndmsg))
            dlog.update('%s,%.2f,%.2f' % (timestr,pm25,pm10))    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due
        else:
            kooka.led_orange.off()
            kooka.led_green.off()
            kooka.led_red.on()
            sens_reading = False
            
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,SDSpin), 90, 6)
    disp.text('A-exit', 0, 63)
    disp.text('Log in %d' % dlog.log_counter, 60, 63)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono6x7)
    if sens_reading: 
        disp.text('PM2.5=%5.2f ug/m^3' % pm25, 10, 20)
        disp.text('PM10 =%5.2f ug/m^3' % pm10, 10, 30)
    else: disp.text('No reading', 12, 20)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
kooka.led_orange.off()
kooka.led_green.off()
kooka.led_red.off()
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


