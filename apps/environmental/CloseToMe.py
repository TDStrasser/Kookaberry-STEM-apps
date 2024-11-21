# File name: CloseToMe.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 23 July 2019
# Date last modified: 4 December 2023 - update to adc.read_u16() function
# Version 1.3
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
# Reading an analogue ultrasonic proximity sensor and displaying go/warning/stop lights
# A threshhold distance for stop can be adjusted with the C and D buttons
# An output signal is activated when it is safe to proceed.
# On Kookaberry Ver 4-05 the Green, Orange, and Red LEDs are used as a traffic light.

# Begin code
# Initial conditions
import machine, kooka, fonts, time
s_plug = 'P4' # input port to use for the proximity sensor - change this to suit
r_plug = 'P2'    # output port for the relay module - change this to suit
# the Gravity Ultrasonic sensor reads 0V when an object is close and increases voltage with distance
cal_distance = 158 # calibration distance in cm
cal_reading = 20140    # A/D raw reading at calibration distance
cal_offset = 0	# distance when the A/D raw reading is zero
gain = cal_distance / cal_reading
max_distance = 300 # maximum range - used to filter out spurious values when sensor is very close to an object (below 2cm it stops ranging)
threshold = 10 # stop distance threshhold - change this to suit
r_status = ['Off', 'On']

adc = machine.ADC(machine.Pin(s_plug))  # create the analogue input for the sensor
relay = machine.Pin(r_plug, machine.Pin.OUT)    # create the digital output for the relay
kooka.radio.disable()         # turn off radio to save battery power

disp = kooka.display

relay.low() # switch the relay off to begin

while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('CloseToMe', 10, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('C-Dn  D-Up', 50, 60)
    disp.setfont(fonts.mono5x5)
    disp.text('Inp %s Out %s' % (s_plug, r_plug), 0, 50)
# Adjust the threshhold using the C and D keys
    if kooka.button_c.was_pressed():
        threshold = max(2, threshold - 1)    # decrement threshhold
    if kooka.button_d.was_pressed():
        threshold = min(100, threshold + 1)    # increment threshhold
    warning = threshold + 10    # level at which the warning comes on
# Read and process the analogue input
    input = min(max_distance,adc.read_u16() * gain + cal_offset) # Convert raw ADC to distance scale
#    print(adc.read_u16())
# Display the distance and the threshold and the status
    disp.setfont(fonts.mono6x7)
    disp.text('D=%.0fcm' % input, 80, 20)
    disp.text('T=%dcm' % threshold, 80, 30)

# Control the outputs
    if input < threshold: 
        relay.low()
        kooka.led_red.on()
        kooka.led_orange.off()
        kooka.led_green.off()
        status = 'STOP!'
    elif input < warning:
        relay.high()
        kooka.led_red.off()
        kooka.led_orange.on()
        kooka.led_green.off()
        status = 'SLOW'
    else: 
        relay.high()
        kooka.led_red.off()
        kooka.led_orange.off()
        kooka.led_green.on()
        status = '  GO!'
# Show the distance status
    disp.setfont(fonts.sans12)
    disp.text('%s' % status, 0, 30)
    disp.setfont(fonts.mono5x5)
    disp.text('%s' % r_status[relay.value()], 60, 50)
    disp.show()

# Clean up and exit
relay.low()
kooka.led_red.off()
kooka.led_orange.off()
kooka.led_green.off()