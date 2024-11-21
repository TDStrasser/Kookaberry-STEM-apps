# File name: 
__name__ = 'SensePT100'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 8 May 2021
# Date last modified: 8 May 2021
# MicroPython Version: 1.12 for the Kookaberry V4-06
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
# Measure temperature using a PT100 resistance temperature detector (RTD) sensor
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [PT10,Temp]
# There is no way to tell if a sensor is not present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: PT100 high temperature probe plugged into P4
# /lib files: Kapputilspy, logger.mpy, doomsday.mpy, pt100.mpy
# /root files: Kappconfig.txt or Kappconfig.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                    _Config sets up Kookaberry parameters
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, ujson
import pt100
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # works out the day of the week from the date (supressed temporarily)

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
disp.print(__name__)
disp.print('Initialising...')

params = config('Kappconfig.txt')   # read the configuration file
# set up the radio for later use
radio_on = False    # Indicates radio initialisation state
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'PT100','T','R']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,T-degC,Res-ohms')    # Create the datalogger instance
dlog.start()    # Start the datalogger

rtdpin = 'P4'
rtd_interval = 2000    # milliseconds between RTD sensor reads
rtd = pt100.PT100(rtdpin)

_timer_rtd = time.ticks_ms()    # timer used for delays and timing samples
temp = 0

radio_interval = params['INTV'] * 1000    # radio transmission interval
_timer_radio = time.ticks_ms() + radio_interval
radio_err = False

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_rtd) >= 0:
            
        resistance = rtd.resistance # get the RTD resistance
        temp = rtd.temperature    # read the temperature
        sndmsg[2] = '%0.1f' % temp    # update the radio buffer
        sndmsg[3] = '%0.1f' % resistance
        dlog.update('%s,%0.1f,%0.1f' % (timestr,temp,resistance))    # update the string to be logged
        dlog.write()    # writes the datalogger string when next due
        # set up for next sample
        _timer_rtd = time.ticks_ms() + rtd_interval 

# Initialise the radio if not already on
    if not radio_on:
        try:    # Restarting the radio
            print('Radio init ', timestr)
            kooka.radio.enable()
            chan = int(params['CHANNEL'])      # use channel from the configuration file
            baud = int(params['BAUD'])      # use data rate from the configuration file
            pwr = int(params['POWER'])      # use transmit power from the configuration file
            kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=50) # set up the radio
            radio_on = True
        except:
            radio_on = False
# Send a radio update per the programmed interval
    if radio_on and time.ticks_diff(time.ticks_ms(), _timer_radio) >= 0:
        _timer_radio += radio_interval
        print(timestr, sndmsg)
        try:
            if temp: kooka.radio.send(ujson.dumps(sndmsg)) # transmit if a reading taken
        except:    # radio error
            radio_on = False

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('%s %s' % (rtdpin, id), 90, 6)
    if radio_on: disp.text('OK Ch%s' % chan, 90, 14)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono8x13)
    disp.text('Temp = %.1f C' % temp, 12, 26)
    disp.setfont(fonts.mono6x7)
    disp.text('Res = %.2f ohms' % resistance, 12, 36)
    disp.show()

# Check for time updates
    if radio_on: 
        try:
            msg = kooka.radio.receive()    #listen for a message
        except:
            radio_on = False
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = ujson.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
#            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


