# File name: 
__name__ = 'SenseMe'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 18 Aug 2018
# Date last modified: 4 December 2023 - update to adc.read_u16() function
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
# Sensor light using the Gravity Passive Infra-Red (PIR) Sensor which gives a digital reading when motion of a warm body is detected
# together with a Gravity Switch Module that switches a separately supplied light on and off.
# The algorithm switches the output on for an adjustable period when motion is detected
# A datalogging function has been added which is configured by the file Kookapp.cfg

# Initial conditions
import machine, kooka, fonts, time
from Kapputils import config    # utility to read the configuration file

s_plug = 'P5' # input port to use for the PIR sensor - change this to suit
r_plug = 'P2'    # output port for the relay module - change this to suit
l_plug = 'P4'    # input port for the light sensor - change this to suit
r_status = ['Off', 'On']
p_status = ['Still', 'Motion!']
l_status = ['Drk', 'Dim', 'Lit']
l_dark = 25 # dim threshhold - change this to suit
l_light = 50 # lit threshhold - change this to suit
timings = [2, 5, 10, 15, 20, 30, 60]  
t_on_ptr = 3    # pointer to the array of timings
t_on = timings[t_on_ptr]    # the number of seconds the output stays on
t_off_ptr = 1    # pointer to the array of timings
t_off = timings[t_off_ptr]    # the number of seconds the output stays off
on_timer = 0
dur_timer = 0
on_flag = 0
l_flag = 0
l_cat = 0

pir = machine.Pin(s_plug, machine.Pin.IN, machine.Pin.PULL_UP)    # create digital input for PIR
relay = machine.Pin(r_plug, machine.Pin.OUT)    # create the digital output for the switch
adc = machine.ADC(machine.Pin(l_plug))  # create the analogue input for the light sensor
kooka.radio.disable()         # turn off bluetooth to save battery power

disp = kooka.display
params = config('Kookapp.cfg')   # read the configuration file
fname = __name__ + '.CSV'
f = open(fname,'w+')         # open a text file for writing
f.write('Kookaberry Log for %s\n' % params['NAME'])
f.write('Time,Switch,Illumination\n')   # write the heading line
f.close()    # close file to guard against corruption

relay.low() # switch the relay off to begin

while not kooka.button_a.was_pressed():
    t0 = time.ticks_ms() # mark the time in ticks at the beginning of the loop
    t_on = timings[t_on_ptr]    # the number of seconds the output stays on
# Take a light reading
    if l_flag:
        light = adc.read_u16() / 65535 * 100  #Convert raw ADC to percentage scale
# Categorise the light reading
        l_cat = 0
        if light >= l_dark: l_cat = 1
        if light >= l_light: l_cat = 2
# Populate the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    disp.text('PIR:%s Sw:%s Ls:%s' % (s_plug, r_plug, l_plug), 0, 20)
    disp.text('X', 6, 63)	    # A Key = Exit
    disp.text('On-Timer', 24, 63)	    # C Key = On-Timer
    disp.text('L-Sens', 86, 63)	    # B Key = Light Sensor
    t_disp = t_on        # work out value to display for on delay (preset or active)
    if on_timer: t_disp = on_timer
    disp.text('%d' % t_disp, 24, 52)
    l_disp = r_status[l_flag]
    if l_flag: l_disp = l_status[l_cat]
    disp.text('%s' % l_disp, 108, 52)
    disp.setfont(fonts.mono8x13)
    disp.fill_rect(0, 26, 128, 17, 1)
    disp.text('%s' % p_status[pir.value()], 6, 38, 0)
    disp.text('Sw: %s' % r_status[relay.value()], 64, 38, 0)
#   Adjust timer presets by scrolling through the timings array
    if kooka.button_c.was_pressed(): 
        t_on_ptr += 1
        if (t_on_ptr >= len(timings)): t_on_ptr = 0
    if kooka.button_b.was_pressed(): 
        l_flag = not l_flag # toggle light sensor flag
        l_cat = 0  # set to dark
# Detect sensors and control the output
    if(pir.value() and not on_timer and not l_cat):    # PIR has detected motion and  it is dark
        relay.high()    # turn on the output
        on_timer = timings[t_on_ptr]    # start timer for output
        f = open(fname,'a+')         # open a text file for writing
        f.write('%d,%s,%s\n' % (dur_timer, r_status[relay.value()],l_status[l_cat]))
        f.close()   # Close to save from corruption by power interruptions
    if (on_timer == 1): on_flag = 1    # on timer about to expire
    if (on_timer == 0 and on_flag == 1):    # on delay has expired
        relay.low()    # turn the output off
        on_flag = 0    # reset the on delay expiry flag
        f = open(fname,'a+')         # open a text file for writing
        f.write('%d,%s,%s\n' % (dur_timer, r_status[relay.value()],l_status[l_cat]))
        f.close()   # Close to save from corruption by power interruptions
    if (l_cat == 2):    # if it gets bright turn the output off
        relay.low() 
        on_timer = 0    # reset the on timer
        f = open(fname,'a+')         # open a text file for writing
        f.write('%d,%s,%s\n' % (dur_timer, r_status[relay.value()],l_status[l_cat]))
        f.close()   # Close to save from corruption by power interruptions
    disp.show()
# Manipulate the timers
    t1 = time.ticks_ms() # mark the time in ticks after the loop work is done
    t_sleep = 1000 - time.ticks_diff(t1, t0)    #calculate how long before 1 second is up
    time.sleep_ms(t_sleep)
    dur_timer += 1    # overall run timer
    if (on_timer > 0): on_timer -= 1    # decrement on timer
# Clean up and exit
f.close()    # close the log file (if it is open)
relay.low() # Switch the relay off when exiting