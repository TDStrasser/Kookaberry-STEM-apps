# File name: 
__name__ = 'ListenLog'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 1 Sept 2018
# Date last modified: 22 November 2020
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
# This program listens to the packet radio, identifies the lesson reports,
# and logs any messages received for the first-identified lesson
# Lesson ID can be fixed by the Kookapp.cfg file or 
# else is taken to be the first received valid lesson ID
# Modified to open and close the logging file for each message to minimise
# the likelihood of data loss on improper exit (such as power loss).
# Modified to check the battery status - removed
# Updated for new configuration parameters
# Begin code

import machine, kooka, time, json, fonts
from Kapputils import config    # utility to read the configuration file
disp_lines = ['']*4
disp_length = len(disp_lines) - 1
disp_locs = [26,34,42,50]
headings ={
    'KLP001':'Name,Y,G,B,R,W',
    'KLP002':'Name,Angle,Time,Drops',
    'DEFAULT':'Name,V1,V2,V3,V4,V5'}
lesson = ''    #set lesson designator to default string as config no longer supports the LESSON key
params = config('Kapputils.cfg')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file
kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # set up the radio
disp = kooka.display    # initialise the display
# Create the logging file
fname = __name__ + '.CSV'
f = open(fname,'w+')    # open file for writing
f.close()
# Select and write the correct headings
#lesson = params['LESSON'] # Deprecated
if lesson in headings: heading = headings[lesson]
else: 
    lesson = ''
    heading = 'Pending'
h_written = False
msg_count = 0
# Set up a timer for flashing text
blinker = True
timer_val = 50
timer = timer_val    


while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 6, 63)	   # A Key = Exit
    disp.text('%s' % heading,0,18)
    disp.text('Msg: %d' % msg_count, 60, 63)	   # No of messages received
    for i,line in enumerate(disp_lines):
        disp.text('%s' % line, 4, disp_locs[i])    # display last received messages
    msg = kooka.radio.receive()    #listen for a message
    if msg:
        print(msg)
        f = open(fname,'a+')         # open log file for appending
        msg_parts = msg.split(',',1)    # first parameter is the lesson, second the payload
        if lesson and not h_written:    # lesson predefined in Kappconfig file
            f.write('%s\n' % heading)
            h_written = True
            print(heading)
        elif not lesson and msg_parts[0] and not h_written:    # only if no lesson  identified so far
            lesson = msg_parts[0]
            if lesson in headings: # only process if the lesson is in the list of defined headings
                heading = headings[lesson]
                f.write('%s\n' % heading)
                h_written = True
                print(heading)
            else: 
                lesson = ''
                heading = 'Pending'
        if msg_parts[0] == lesson:    # retrieves the message payload only if matching lesson
            msg_count += 1
            disp_lines[0] = disp_lines[1]
            disp_lines[1] = disp_lines[2]
            disp_lines[2] = disp_lines[3]
            disp_lines[disp_length] = msg_parts[1]
            f.write('%s\n' % msg_parts[1])
            print(msg_count,msg_parts[1])
        f.close()    # close log file to minimise data loss on power loss
# This code manages the battery warning
    timer -= 1    # timer used for blinking the warning
    if timer <= 0:
        blinker = not blinker
        timer = timer_val

    disp.show()
    
# Clean up and exit
kooka.radio.disable()    # turn packet radio off
f.close()

