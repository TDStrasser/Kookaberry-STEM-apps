# File name: 
__name__ = 'Spira'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 10 July 2021
# Date last modified: 11 July 2021 - more efficient computations
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
# Demonstrates mathematical roulette graphs, such as are implemented by the Spirograph toy
# Reference https://en.wikipedia.org/wiki/Spirograph
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: nil
# /lib files: nil
# /root files: nil
# Other dependencies: nil
# Complementary apps: nil
#------------------------------------------

# Begin code

# Initial conditions

import machine, kooka, math, fonts

draw = False    # False = setup parameters, True = draw the figure
inputs = [30, 14, 12]    # Array of key inputs
limits = [1, 32] # Maximum excursions of circles
centre = [63, 32]    # Centre of the roulette on the Display
inp_ptr = 0    # index to the input array (for setup)
dotted = [10, 10, 10]    # Used to highlight the setup circle

# Function draws a circle of radius r centred on x and y all in pixels
def draw_circle(x, y, r, space=10):
    for i in range(0, 360, int(space)):
        rads = i / 180.0 * math.pi
        kooka.display.pixel(int(r * math.cos(rads) + x), int(r * math.sin(rads) + y), int(1))

# Function draws the roulette on the Display
def draw_spira(big_R, little_r, pixel_r):

    # Work out some common factors to simplify the mathematics
    k = little_r / big_R
    lk = pixel_r / big_R
    my_1_k = 1 - k
    _1_k__k = my_1_k / k
    t = 0
    kooka.display.fill(0)
    kooka.display.setfont(fonts.mono5x5)
    kooka.display.text('A-stop', 0, 63)
    kooka.display.show()
    # Continue drawing until button A was pressed
    while not kooka.button_a.was_pressed():
        rads = t / 180.0 * math.pi    # convert degrees to radians
        x = my_1_k * math.cos(rads) + lk * math.cos(_1_k__k * rads)
        y = my_1_k * math.sin(rads) + -lk * math.sin(_1_k__k * rads)
        kooka.display.pixel(int(63 + big_R * x), int(32 + big_R * y), int(1))
        t += 1
        kooka.display.show()

# Begin main loop here
while not kooka.button_a.was_pressed():
    # Prepare the static display
    kooka.display.fill(0)
    kooka.display.setfont(fonts.mono8x8)
    kooka.display.text('%s' % __name__, 0, 6)
    kooka.display.setfont(fonts.mono6x7)
    # Prepare the controls display
    if not draw:    # In setup mode
        kooka.display.text('A-exit', 0, 63)
        kooka.display.text('B-next', 90, 63)
        if inp_ptr < len(inputs):    # Specifying the sizes of the circles
            kooka.display.text('C +', 0, 20)
            kooka.display.text('D -', 0, 30)
            if kooka.button_b.was_pressed():    # Go to the next input
                inp_ptr += 1
                if inp_ptr <0: inp_ptr = 0
            if kooka.button_c.was_pressed():
                inputs[inp_ptr] = min(limits[1], inputs[inp_ptr]+1)
            if kooka.button_d.was_pressed():
                inputs[inp_ptr] = max(limits[0], inputs[inp_ptr]-1)
            for i in range(0, len(dotted)):
                dotted[i] = 10
            if inp_ptr < len(dotted): dotted[inp_ptr] = 1
        elif inp_ptr == len(inputs):    # Specifying the sizes of the circles
            kooka.display.text('C or D', 0, 20)
            kooka.display.text('draw', 0, 30)
            if kooka.button_b.was_pressed():    # Go to the next input
                inp_ptr += 1
                if inp_ptr > len(inputs): inp_ptr = 0
            if kooka.button_c.was_pressed() or kooka.button_d.was_pressed(): # Draw
                draw = True
        # Draw the circles specified
        draw_circle(centre[0], centre[1], inputs[0], dotted[0])    # Draw the big circle
        draw_circle(centre[0]-inputs[0]+inputs[1], centre[1], inputs[1], dotted[1]) # Small circle
        draw_circle(centre[0]-inputs[0]+inputs[1], centre[1], inputs[2], dotted[2]) # Pixel circle
        kooka.display.text('R:%d' % inputs[0], 100, 20)
        kooka.display.text('r:%d' % inputs[1], 100, 30)
        kooka.display.text('p:%d' % inputs[2], 100, 40)
        kooka.display.show()
    # This code draws the roulette - exits if button A is pressed
    elif draw:
        draw_spira(inputs[0], inputs[1], inputs[2])
        draw = False    # Reset to setup mode
        inp_ptr = 0    # Reinitialse the setup index
        # Reset all the Kookaberry buttons in case any were pressed
        kooka.button_a.was_pressed()
        kooka.button_b.was_pressed()
        kooka.button_c.was_pressed()
        kooka.button_d.was_pressed()

# Clean up and exit
kooka.display.fill(0)
kooka.display.show()