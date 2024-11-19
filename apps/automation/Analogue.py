# File name: Analogue.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 9 January 2019
# Date last modified: 11 June 2023 - ADC read changed to 16bit (as 10bit reads are deprecated)
# Version 1.6
# MicroPython Version: 1.20 for the Kookaberry V4-06
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
# Demonstration of reading an analogue input and displaying it on a histogram
# A level detector is also supplied which drives an output.  
# The output is off below the threshhold and on above the threshhold.
# The threshhold can be adjusted with the C and D buttons
# A lightbulbicon was added to show when the output is activated.
# On Kookaberry Ver 4-05 the Orange LED is also activated above the threshhold.

# Begin code
# Initial conditions
import machine, kooka, fonts, time, framebuf
s_plug = 'P4' # input port to use for the light sensor - change this to suit
r_plug = 'P2'    # output port for the relay module - change this to suit
sc_reading = 100 # set to 100 initially then reading with pins shorted - depends on the sensor supply voltage
gain = 100 / sc_reading
t_input = 50 # bright threshhold - change this to suit
r_status = ['Off', 'On']

adc = machine.ADC(machine.Pin(s_plug))  # create the analogue input for the sensor
relay = machine.Pin(r_plug, machine.Pin.OUT)    # create the digital output for the relay
kooka.radio.disable()         # turn off bluetooth to save battery power
# Create a light bulb icon
bitmap = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x38, 0x70, 0x00, 0x00, 0x80, 0x80, 0x8E, 0x9E, 0x8E,
0x80, 0x80, 0x00, 0x00, 0x70, 0x38, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x06,
0x0E, 0x0C, 0x0C, 0x00, 0xF8, 0xFC, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
0xFE, 0xFC, 0xF8, 0x00, 0x0C, 0x0C, 0x0E, 0x06, 0x04, 0x00, 0x00, 0x00, 0x06, 0x06, 0x03, 0x02,
0x80, 0xC1, 0xE7, 0x4F, 0x3F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x1F, 0x4F, 0xE7, 0xC1,
0x80, 0x02, 0x03, 0x06, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00,
0x00, 0x00, 0x25, 0x2D, 0x6D, 0xED, 0x6D, 0x2D, 0x05, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

bulb = framebuf.FrameBuffer(bitmap, 29, 32, framebuf.MONO_VLSB)

disp = kooka.display

relay.low() # switch the relay off to begin

while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Analogue', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('C-Dn  D-Up', 50, 60)
    disp.setfont(fonts.mono5x5)
    disp.text('Inp %s Out %s' % (s_plug, r_plug), 0, 50)
# Adjust the threshhold using the C and D keys
    if kooka.button_c.was_pressed():
        t_input = max(5, t_input - 5)    # decrement threshhold
    if kooka.button_d.was_pressed():
        t_input = min(95, t_input + 5)    # increment threshhold
        
# Read and process the analogue input
    disp.setfont(fonts.mono8x13)
    input = adc.read_u16() / 65535 * 100 * gain #Convert raw ADC to percentage scale
# Display the reading as a percentage and the category
    disp.setfont(fonts.sans12)
    disp.text('%.0f %%' % input, 40, 30)
# Display a bar chart with the treshholds marked
    r_width = 20
    r_height = 45
    r_x = 100
    r_y = 5
    disp.rect(r_x,r_y,r_width,r_height,1)    # outline rectangle
    # Display the threshhold line
    t_y = int(r_y + r_height - t_input * r_height / 100)
    t_x1 = r_x - 5
    t_x2 = r_x + r_width + 5
    disp.line(t_x1 , t_y, t_x2 , t_y, 1)
    disp.setfont(fonts.mono5x5)
    disp.text('%.0f' % t_input, r_x+5, t_y - 2)
    # Display the analogue measurement histogram line
    t_y = int(r_y + r_height - input * r_height / 100)
    t_h = int(input * r_height / 100)
    disp.fill_rect(r_x , t_y, r_width , t_h, 1)
# Control the output
    if input >= t_input: 
        relay.high()
        kooka.led_orange.on()
    else: 
        relay.low()
        kooka.led_orange.off()
    if relay.value(): disp.blit(bulb, 6, 10)

#    print(servo_angle)
    disp.show()

# Clean up and exit
relay.low()
kooka.led_orange.off()