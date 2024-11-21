# File name: 
__name__ = 'SenseAnlg'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 28 February 2020
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
# Measure 1 or 2 analogue signals (scales of 0 to 100, or 0 to 3.3V, or 0 to 4095 selected via button C) attached to P4 and P5
# Logs into a file at an interval specified in Kappconfig.txt or and on significant change
# Broadcasts the analogue signals over the packet radio in the format [Anlg,P1,P4,P5]
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Analogue peripherals on P4 and optionally P5
# /lib files: Kapputils.py, kcpu.py, logger.py, doomsday.py
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx.py receives data and transmits time updates
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json
from micropython import const
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
sndmsg = [id,'Anlg','0','0']

inputs = ['P4','P5']    # input ports
signal = [0,0]    # the measured signals
last_sig = [0,0]   # used for checking on sudden changes
scale = [100/4095, 3.3/4095, 1]
scale_unit = ['%','V','r']
scale_ptr = 0
delta_sig = 50    # threshhold for signal change detection
no_signals = 1    # the number of signals
max_signals = len(inputs)    # the maximum number of signals
sens_interval = 100    # milliseconds between samples

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,Sig-P4,Sig-P5' )    # Create the datalogger instance
dlog.start()    # Start the datalogger

tx_interval = params['INTV'] * 1000    # interval between radio update in milliseconds

_timer_sens = time.ticks_ms()    # initialise sample timer
_timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s' % id, 115, 6)
    disp.text('A-x C-in D-sc', 0, 60)
    disp.text('Lg:%d' % dlog.log_counter, 86, 60)
    disp.text('%s' % timestr, 0, 50)
# Adjust the number of channels via button C
    if kooka.button_c.was_pressed():
        no_signals += 1    # increment
        if no_signals > max_signals: no_signals = 1
# Adjust the scale via button D
    if kooka.button_d.was_pressed():
        scale_ptr += 1    # increment
        if scale_ptr >= len(scale): scale_ptr = 0
# Get the analogue inputs
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        for i in range(0,max_signals): signal[i] = 0 # reset unused channels
        for i in range(0,no_signals):
            signal[i] = int(machine.ADC(inputs[i]).read_u16() >> 4)
#        print(signal)    # uncomment to get diagnostic printout
# send the radio update
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += tx_interval    # transmit every period
        for i in range(0,max_signals): sndmsg[i+2] = '%0.1f' % (signal[i]*scale[scale_ptr])    # update the radio buffer
        print(sndmsg)
        kooka.radio.send(json.dumps(sndmsg))

# Prepare the analogue signal displays
    disp.setfont(fonts.mono6x7)
    for i in range(0,no_signals): 
        disp.text('%s' % inputs[i], 0, 20+15*i) 
        kooka.display.rect(20, 12+15*i, 50, 10, 1)
        kooka.display.fill_rect(20, 12+15*i, int(signal[i]*50/4095), 10, 1)
        disp.text('%0.1f%s' % (signal[i]*scale[scale_ptr],scale_unit[scale_ptr]), 76, 20+15*i)

    disp.show()
# Update the datalogger with the signals
    for i in range(0, max_signals):
        if abs(signal[i]-last_sig[i]) >= delta_sig: 
            dlog.log_write = True # force datalogging if significant change
            print('Force Log')
        last_sig[i] = signal[i]    # store the current signals
    dlog.update('%s,%0.1f,%0.1f' % (timestr,(signal[0]*scale[scale_ptr]),(signal[1]*scale[scale_ptr])))    # update the string to be logged
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


