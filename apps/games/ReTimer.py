# File name: 
__name__ = 'ReTimer'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 02 July 2020
# Date last modified: 22 November 2020
# Version 1.2
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
# Description
# A game to test the user's reaction time.
# The three Kookaberry LEDs are turned onin sequence at random intervals.
# All LEDs then switch off and the elapsed time to press button B is measured.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: nil
# /lib files: Kapputils.mpy, (doomsday.mpy is embedded in Kookaberry firmware)
# /root files: Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx or ListenLog receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, ujson, math, random
from Kapputils import config    # module to read the configuration file
import doomsday

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
sndmsg = [id,'ReT','time']

delay_timer = time.ticks_ms()    # timer used for delays and timing samples
state = 0     # 0 waiting to start, 1-3 LEDs sequence, 4 LEDs off, 5 timing
re_time = 0    # initialise the reaction time
kooka.led_green.off()    # turn all LEDs off
kooka.led_orange.off()
kooka.led_red.off()
# Prepare the logging file
fname = __name__ + '.csv'
f = open(fname,'w+')
f.write('Time,Reaction-ms\n')
f.close()

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if state == 0 and kooka.button_b.was_pressed():
        delay_timer = time.ticks_ms() + random.randint( 1000, 2000)
        state = 1
    if state == 1 and time.ticks_diff(time.ticks_ms(), delay_timer) >= 0:
        kooka.led_green.on()
        delay_timer = time.ticks_ms() + random.randint( 1000, 2000)
        state = 2
    if state == 2 and time.ticks_diff(time.ticks_ms(), delay_timer) >= 0:
        kooka.led_orange.on()
        delay_timer = time.ticks_ms() + random.randint( 1000, 2000)
        state = 3
    if state == 3 and time.ticks_diff(time.ticks_ms(), delay_timer) >= 0:
        kooka.led_red.on()
        delay_timer = time.ticks_ms() + random.randint( 1000, 2000)
        state = 4
    if state == 4 and time.ticks_diff(time.ticks_ms(), delay_timer) >= 0 and not kooka.button_b.value():    # Button B must not have been pressed
        kooka.led_green.off()
        kooka.led_orange.off()
        kooka.led_red.off()
        delay_timer = time.ticks_ms()
        if kooka.button_b.was_pressed(): pass    # clear and presses
        state = 5
    if state == 5 and kooka.button_b.was_pressed():    # Button B reaction time
        re_time = time.ticks_diff(time.ticks_ms(), delay_timer)
        f = open(fname, 'a+')    # log the reaction time
        f.write('%s,%d\n' % (timestr, re_time))
        f.close()
        sndmsg[2] = '%0.3f' % (re_time / 1000)    # send time in seconds
        kooka.radio.send(ujson.dumps(sndmsg))    # send the radio message
        state = 0
        
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    if state == 0: disp.text('Time: %dmsec' % re_time, 0, 20)
    disp.setfont(fonts.mono6x7)
    disp.text('%s' % id, 100, 10)
    disp.text('A-exit     B-start', 0, 63)
    disp.text('Press B -', 0, 30)
    if state == 0: disp.text('to start', 10, 40)
    if state > 0: disp.text('when LEDs out', 10, 40)
    disp.text('%s' % timestr, 0, 50)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = ujson.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
#            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
kooka.radio.disable()    # turn off the radio


