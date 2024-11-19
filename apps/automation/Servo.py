# File name: 
__name__ = 'Servo'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 8 Sep 2021
# Version 1.0
# Date last modified: 4 December 2023 - Updated ADC.read() to ADC.read_u16()
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
# Description
# Controls a servo in response to button commands or analogue input
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: 9g servo on P1, potentiometer on P4
# /lib files: shapes_lib.mpy
# /root files: nil
# Other dependencies: nil
# Complementary apps: nil
#------------------------------------------

# Begin code

import machine, kooka, fonts, time
import shapes_lib as shape

# Set up objects
anlg_pin = 'P4'    # The analogue input pin
servo_pin = 'P1'    # The servo output pin
disp = kooka.display    # initialise the OLED display
adc = machine.ADC(machine.Pin(anlg_pin))  # create the analogue input
servo = kooka.Servo(servo_pin)    # create the servo object
# Initial conditions
mode = 0    # 0 = button control, 1 = analogue input control
angle = 0    # the servo angle (-90 to +90)
angle_delta = 5    # the change in angle per button press
angle_time = 500    # the rate of angle change in msecs
menus = ['A-x  C-ang+D  B-anlg','A-x Anlg-Inp  B-btn']
# The main loop
while not kooka.button_a.was_pressed():
# Read buttons and set parameters
    if kooka.button_b.was_pressed():
        mode = not mode    # Toggle the mode between 0 and 1

# Read inputs
    if mode == 0:    # Use buttons to change angles
        if kooka.button_d.is_pressed():
            angle += angle_delta
            angle = round(min(angle, 90)/angle_delta) * angle_delta   # round and limit 
        if kooka.button_c.is_pressed():
            angle -= angle_delta
            angle = round(max(angle, -90)/angle_delta) * angle_delta    # round and limit

    if mode == 1:    # Use the analogue input
        angle = adc.read_u16() / 65535 * 180 -90 #Convert raw ADC to angle scale

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('Angle %d' % angle, 70, 6)
    disp.setfont(fonts.mono6x7)
    disp.text(menus[mode], 0, 63)
    shape.arc(disp, 60, 50, 40, -90, 90, 1)
    x,y = shape.line(disp, 60, 50, 35, angle, 1)
    shape.fill_polygon(disp, x, y, 5, 3, angle, 1)
    shape.fill_circle(disp, 60, 50, 5, 1)
    disp.setfont(fonts.mono5x5)
    disp.text('Servo:%s' % servo_pin, 0, 14)
    disp.text('Anlg:%s' % anlg_pin, 0, 20)
    disp.show()

# Set outputs
    servo.angle(angle, angle_time)    # drive the servo
# Clean up and exit