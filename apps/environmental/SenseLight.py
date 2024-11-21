# File name: 
__name__ = 'SenseLight'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 27 July 2020
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
# Measures light level using a Gravity analogue light sensor (photo-transistor)
# Logs the measurements into a file at an interval specified in Kookapp.cfg
# Broadcasts the sensor readings over the packet radio in the format [ID,Ill,Sensor Reading, Estimated Lux]
# A calibration facility occurs first in which the user specifies the nominal lighting environment (indoor light, overcast, clear sky, direct sun)
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: analogue light sensor plugged into P5
# /lib files: Kapputils.mpy, logger.mpy, (doomsday.mpy is embedded in Kookaberry firmware)
# /root files: Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json
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
sndmsg = [id,'Ill','Sens','Lux']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,Sensor-%,Light-lux')    # Create the datalogger instance

s_pin = 'P5'
light = 0
l_condition = ['indoor','o-cast','clear','sun']    # lighting condition
l_calibrate = [400,1500,20000,100000]    # calibration values
l_ptr = 0
calibration = l_calibrate[l_ptr]    # the default calibration of the sensor
state = 0    # 0=calibrate, 1=logging
samples = [0] * 5    # array used to filter light samples to remove flicker

# Initialise the timers
s_interval = 100
_timer_s = time.ticks_ms()    # timer used for delays and timing samples
tx_interval = params['INTV'] * 1000    # interval between radio update in milliseconds
_timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer

# The main loop
while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, prepare the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_s) >= 0:
        _timer_s += s_interval    # only take a sample every period
        for i in range(0,len(samples)):
            samples[i] = int(machine.ADC(s_pin).read(_u16) * 100 / 65535)    # sensor 0-100
            time.sleep_ms(4)
        signal = sum(samples) / i
        light = int(signal * calibration / 100)    # estimated Lux
        sndmsg[2] = '%d' % signal
        sndmsg[3] = '%d' % light
#            print(timestr, sndmsg)    # Diagnostic use (uncomment)
        logstr = '%s,%d,%d' % (timestr,signal,light)
        if state == 1:
            dlog.update(logstr)    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due

# send the radio update
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0 and state == 1:
        _timer_tx += tx_interval    # transmit every period
        print(sndmsg)
        kooka.radio.send(json.dumps(sndmsg))

# Calibration 
    if state == 0:
        if kooka.button_c.was_pressed():
            l_ptr -= 1
            if l_ptr < 0: l_ptr = len(l_calibrate) - 1
        if kooka.button_d.was_pressed():
            l_ptr += 1
            if l_ptr >= len(l_calibrate): l_ptr = 0
        if kooka.button_b.was_pressed():
            state = 1
            calibration = l_calibrate[l_ptr]
            dlog.start()    # Start the datalogger
            _timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer
            
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,s_pin), 90, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-ex', 0, 60)
    if state == 0:
        disp.text('C-cond-D  B-cal', 34, 60)
    else:
        disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono6x7)
    if state == 0:
        disp.text('Cal: %s %d lux' % (l_condition[l_ptr], l_calibrate[l_ptr]), 0, 17)
    else:
        disp.text('Sig:%3d L:%6d lux' % (signal,light), 0, 17)
    disp.rect(10, 27, 110, 10, 1)
    disp.fill_rect(10, 27, int(signal*1.1), 10, 1)

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
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


