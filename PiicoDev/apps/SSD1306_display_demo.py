# FILENAME: SSD1306_display_demo.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 19 August 2025
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython Version: 1.19 for the Raspberry Pi Pico with RP2040
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# DESCRIPTION:
# Demonstrates the PiicoDev SSD1306 display module connected via I2C to the Kookaberry.
# Conducts a series of diaply tests including a pixel test, geometric patterns, and a range of text font sizes.
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: I2C bus on P3, PiicoDev SSD1306 Display Module
# /lib files: PiicoDev_SSD1306_Kookaberry
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

from machine import SoftI2C, Pin
import fonts, time
import kooka
from PiicoDev_SSD1306_Kookaberry import create_PiicoDev_SSD1306

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
disp = create_PiicoDev_SSD1306(bus=i2c, address=0X3C)
x = 0
stages = ['Pixel test...','Geometry test...','Fonts Test']
stage = 0
while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Display Test',20,6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit',6,60)
    disp.text(stages[stage], 0, 30)
    disp.show()
    time.sleep(1)
    if stage == 0:    # Pixel display test
        disp.fill(1)
        disp.show()
        stage += 1
        time.sleep(2)
        
    elif stage == 1:    # Geometry test 
        disp.fill(0)
        for x in range(0,128):    # draws a progressive diagonal line
            y = int(x/2)
            disp.line(0,0,x,y,1)
            disp.show()
        time.sleep(0.5)
        for x in range(0,64):    # draws progressively smaller rectangles
            disp.fill(0)
            y = int(x/2)
            disp.rect(x,y, 127-2*x, 63-2*y, 1)
            disp.show()
            time.sleep_ms(20)
        time.sleep(0.5)
        stage += 1

    elif stage == 2:    # Font test
        disp.fill(0)
        disp.pixel(0, 5, 1)
        disp.setfont(fonts.mono5x5)
        disp.text("5x5 Hello there Kookaberry!", 2, 5)

        disp.pixel(0, 13, 1)
        disp.setfont(fonts.mono6x7)
        disp.text("6x7 Hi Kookaberry!", 2, 13)

        disp.pixel(0, 23, 1)
        disp.setfont(fonts.mono8x8)
        disp.text("8x8 Kookaberry!", 2, 23)

        disp.pixel(0, 35, 1)
        disp.setfont(fonts.mono8x13)
        disp.text("8x13 Kookaberry!", 2, 35)

        disp.pixel(0, 56, 1)
        disp.setfont(fonts.sans12)
        disp.text("12 Kookaberry", 2, 56)
        
        disp.show()
        stage = 0
        time.sleep(1.5)
    else: pass
disp.fill(0)
disp.show()