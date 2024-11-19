# File name: BinaryNumbers.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 8 January 2019
# Date last modified: 27 April 2019
# Version 1.2
# MicroPython Version: 1.10 for the Kookaberry V4-05
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
# A decimal to binary number conversion demonstration and puzzle setter
# There are three modes:
#    1. The user can adjust a decimal number up and down and see the binary equivalent
#    2. The user picks a random decimal number and manually solves the binary - a show button displays the answer
#    3. The user picks a random binary number and manually solves the decimal - a show button displays the answer

# Begin code
import kooka, fonts, random, time
disp = kooka.display
mode_ptr = 0
modes = ['Show','Dec','Bin']
controls = ['-   No   +','Pick  Show','Pick  Show']
mode_max = len(modes)
values = [16,8,4,2,1]
binary_no = [0] * 5    # The computed binary number as digits
userb_no = [0] * 5    # The user's binary data entry
dec_no = 0    # The decimal number
userd_no = 0    # User entered decimal number
dec_max = 2 ** len(binary_no) - 1   # maximum decimal catered for
show_dec = 1    # flag to hide/show the decimal number
show_bin = 1    # flag to hide/show the binary number
random.seed(time.ticks_ms())    # seed the random number generator using the time

# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Binary Numbers', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('%s' % modes[mode_ptr], 94, 60)
    disp.text('%s' % controls[mode_ptr], 20, 60)
# Change the mode of operation between showing and solving numbers
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        if mode_ptr == mode_max: mode_ptr = 0
        if mode_ptr == 0: show_bin = show_dec = 1
        else: show_bin = show_dec = 0
# Adjust the numbers according to the mode using the C and D keys
    if kooka.button_c.was_pressed():
        if mode_ptr == 0:
            dec_no = max(0, dec_no - 1)
        elif mode_ptr == 1:    # Random decimal, user solves binary
            dec_no = random.getrandbits(5)
            show_bin = 0
            show_dec = 1
        else:    # Random binary, user solves decimal
            dec_no = random.getrandbits(5)
            show_dec = 0
            show_bin = 1
    if kooka.button_d.was_pressed():
        if mode_ptr == 0:
            dec_no = min(dec_max, dec_no + 1)
        else: show_bin = show_dec = 1
# Compute the binary number from the decimal
    remainder = dec_no
    for i in range(0,5): 
        binary_no[i] = int(remainder/values[i])
        remainder = remainder % values[i]
# Display the results
    disp.setfont(fonts.sans12)
    if show_dec: disp.text('%2d' % dec_no, 30, 27)
    disp.setfont(fonts.mono6x7)
    disp.text('Decimal', 60, 25)
    disp.setfont(fonts.sans12)
    if show_bin:
        for i in range(0,5): disp.text('%d' % binary_no[i], 11 + 23*i, 47)
    disp.setfont(fonts.mono5x5)
    for i in range(0,5): disp.text('%d' % values[i], 23 + 23*i, 47)
    
    disp.show()
# Exit

