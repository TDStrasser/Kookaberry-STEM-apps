# File name: 
__name__ = 'SenseUVI'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 13 May 2020
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
# Measures UV intensity using the GUVA-S12SD sensor attached to P5
# Logs into a file at an interval specified in Kappconfig.txt or and on significant change
# Broadcasts the analogue signals over the packet radio in the format [Time,UV]
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: GUVA-S12SD breakout board on P5
# /lib files: Kapputils.py, logger.py, doomsday.py
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx.py receives data and transmits time updates
#                    _Config.py sets the Kookaberry parameters
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # converts date to day of week

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
rtc = machine.RTC()    # instantiate the Real Time Clock

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
sndmsg = [id,'UVI','0']

uv_pin = 'P5'    # input ports
uv_signal = 0    # the measured signals
last_sig = 0   # used for checking on sudden changes
delta_sig = 1    # threshhold for signal change detection
sens_interval = 2000    # milliseconds between samples
uv_levels = [50, 227, 318, 408, 503, 606, 696, 795, 881, 976, 1079, 1170, 3300]

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,UVindex' )    # Create the datalogger instance
dlog.start()    # Start the datalogger

_timer_sens = time.ticks_ms()    # initialise sample timer
tx_interval = params['INTV'] * 1000    # interval between radio update in milliseconds
_timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,uv_pin), 90, 10)
    disp.text('A-exit', 0, 63)
    disp.text('Log in %d' % dlog.log_counter, 70, 63)
    disp.text('%s' % timestr, 0, 54)

# Get the analogue input
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        uv_signal = int(machine.ADC(uv_pin).read_u16() * 3300 / 65535)
        for uv_index in range(0,len(uv_levels)):    # Select UV index
            if uv_signal < uv_levels[uv_index]: break
#        print(signal)    # uncomment to get diagnostic printout
# send the radio update
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += tx_interval    # transmit every period
        sndmsg[2] = '%d' % uv_index
        print(sndmsg)
        kooka.radio.send(json.dumps(sndmsg))

# Prepare the analogue signal displays
    disp.setfont(fonts.mono6x7)
    disp.text('UV', 0, 24) 
    kooka.display.rect(20, 15, 80, 10, 1)
    kooka.display.fill_rect(20, 15, int(uv_index*80/12), 10, 1)
    # Prepare the UV risk display
    if uv_index <= 2: uv_risk = "low"
    elif uv_index <= 5: uv_risk = "moderate"
    elif uv_index <= 7: uv_risk = "high"
    elif uv_index <=10: uv_risk = "very high"
    else: uv_risk = "extreme"
    disp.setfont(fonts.mono8x8)
    disp.text('%d' % uv_index, 110, 24)
    disp.text('Risk:%s' % uv_risk, 0, 43)
    disp.setfont(fonts.mono5x5)
    disp.text('Signal: %d mV' % uv_signal, 20, 34)

    disp.show()
# Update the datalogger with the signals
    if abs(uv_index-last_sig) >= delta_sig: 
        dlog.log_write = True # force datalogging if significant change
        print('Force Log')
    last_sig = uv_index    # store the current signals
    dlog.update('%s,%d' % (timestr,uv_index))    # update the string to be logged
    dlog.write()    # writes the datalogger string when next due

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore

# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


