# File name: 
__name__ = 'BalanceMe'
# Lesson Plan: KLP002
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 29 August 2018
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
# Egg and Spoon emulator for Balance lesson with logging to a CSV file
# Begin code
import math, machine, kooka, fonts, time, json
from Kapputils import config    # utility to read the configuration file
lesson = 'KLP002'    # Kookaberry Lesson Plan No

# connect an active buzzer to P2
b_plug = 'P2' # port to use for the buzzer - change this to suit
buzzer = machine.Pin(b_plug, machine.Pin.OUT, value=0)
buzzer.value(0)    # turn the buzzer off

# the limit in degrees at which the device will sound
limit_angle = 10

# how big the circle display is
sensitivity = 20

# initialise the out of limit counter
oops_counter = 0
oops_last = 0
racing = 0
racing_timer = 0
racing_start = 0
r_states = ['Go','Stp']
buz_timer = 0
buz_length = 125    # length of buzzer sound in milliseconds
buz_start = 0
reset_timer = 0    # timer resets the race if excursion is too long
reset_length = 5000    # maximum excursion time
reset_start = 0

params = config('Kookapp.cfg')   # read the configuration file

# initialise
kooka.radio.enable()         # turn radio on
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file

kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # set up the radio

disp = kooka.display    # initialise the display
# Prepare the logging file
fname = __name__ + '.CSV'
f = open(fname,'w+')    # open file for writing
f.write('ID,Angle,Time,Count\n')  # write headings
f.close()    # Close file to guard against corruption
radio_msg = [lesson, '%d' % params['ID'],'10','0','0']    # initialise the radio message

while not kooka.button_a.was_pressed():
    t0 = time.ticks_ms()    # mark the time at loop start
    if racing: racing_timer = t0 - racing_start    # update length of race
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    disp.text('Buz:%s' % (b_plug), 80, 10)
    disp.text('X', 6, 62)	   # A Key = Exit
    disp.text('-', 30, 62)    # C Key = Reduce Angle
    disp.text('+', 90, 62)    # D Key = Increase Angle
    disp.text('%s' % r_states[racing], 106, 62)  # B Key = Go / Stop
    disp.text('<%2.0fdeg>' % limit_angle, 40, 62)    # The angle
    disp.text('Count', 4, 20)
    disp.text('Time', 90, 20)
    disp.setfont(fonts.sans12)
    disp.text('%d' % oops_counter, 4, 40)
    disp.text('%d' % int(racing_timer/1000), 90, 40)

    # adjust limit angle with buttons or start/stop the race
    if kooka.button_c.was_pressed():
        limit_angle = max(1, limit_angle - 1)
    if kooka.button_d.was_pressed():
        limit_angle = min(45, limit_angle + 1)
    if kooka.button_b.was_pressed() and not outside_limit:    # start or stop the race
        racing = not racing    # toggle racing state
        if racing: 
            racing_start = t0    # record when race started
            oops_counter = 0    # reset the excursion counter
        else:
            f = open(fname,'a+')    # record results when race stopped
            f.write('%s,%d,%d,%d\n' % (params['ID'],limit_angle,int(racing_timer/1000),oops_counter))
            f.close()
            # broadcast the results via the radio
            radio_msg[2] = str(limit_angle)
            radio_msg[3] = str(int(racing_timer/1000))
            radio_msg[4] = str(oops_counter)
            msg = ""
            for s in radio_msg:
                msg += s + ","
            kooka.radio.send(msg)

    # calculate the angle of the device
    x, y, _ = kooka.accel.get_xyz()
    x = min(1, max(-1, x / 9.8))
    y = min(1, max(-1, y / 9.8))
    x_angle = math.degrees(math.asin(x))
    y_angle = math.degrees(math.asin(y))
    total_angle = (x_angle**2 + y_angle**2)**0.5

    # check if angle is outside limit and apply hysteresis to prevent multiple excursions
    if not oops_last : outside_limit = total_angle > limit_angle
    else: outside_limit = total_angle > (0.8 * limit_angle)
    if outside_limit and not oops_last and racing: # when excursion first occurs
        oops_counter += 1    # count excursions
        buz_timer = buz_length    # sound the buzzer
        buz_start = t0        # mark the time of buzzer start
        reset_timer = 1
        reset_start = t0 - 1    # -1 to prevent deadlock later
    oops_last = outside_limit
    
    if not outside_limit: reset_timer = 0

    # sound the buzzer for a time following an excursion
    if buz_timer:  
        buzzer.value(1)
        buz_timer -= (t0 - buz_start)    # decrement timer
        buz_start = t0
        buz_timer = max(0, buz_timer)    # limit to positive numbers
    else: buzzer.value(0)
    # update the excursion timer as long as the excursion remains active
    if reset_timer and outside_limit:
        reset_timer = (t0 - reset_start)
        reset_timer = max(0, reset_timer)
    if reset_timer >= reset_length: 
        racing = 0
        reset_timer = 0
        buz_timer = buz_length * 8   # sound the buzzer for a longer beep
        buz_start = t0        # mark the time of buzzer start

    # update the display of the circle and the egg
    square = 2 * sensitivity + 1
    disp.fill_rect(64 - sensitivity, 32 - sensitivity, square, square, outside_limit)
    for phi in range(0, 361, 24):    # the circle
        u2 = 64 - int(sensitivity  * math.sin(math.radians(phi)))
        v2 = 32 - int(sensitivity  * math.cos(math.radians(phi)))
        if phi != 0:
            disp.line(u, v, u2, v2, 1 - outside_limit)
        u, v = u2, v2
    u = 64 - int(sensitivity / limit_angle * y_angle)
    v = 32 - int(sensitivity / limit_angle * x_angle)
    disp.line(u - 1, v, u + 1, v, 1 - outside_limit)
    disp.line(u, v - 1, u, v + 1, 1 - outside_limit)
    disp.show()

# Clean up and exit
buzzer.value(0)    # Turn the buzzer off
f.close()        # close any open file
kooka.radio.disable()    # turn packet radio off
