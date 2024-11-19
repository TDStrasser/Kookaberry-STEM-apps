# FILENAME: HexNumbers.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 28 February 2022
# DATE-MODIFIED: 28 February 2022
# VERSION: 1.0
# SCRIPT-TYPE: MicroPython Version: 1.12 for the Kookaberry V4-05
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
# A decimal to hexadecimal number conversion demonstration and puzzle setter
# There are three modes:
#    1. The user can adjust a decimal number up and down and see the hexadecimal equivalent
#    2. The user picks a random decimal number and manually solves the hexadecimal - a show button displays the answer
#    3. The user picks a random hexadecimal number and manually solves the decimal - a show button displays the answer
# TAGS: #dt #digital_technology #codes #hex #hexadecimal
# DEPENDENCIES:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------

# BEGIN-CODE:

import kooka, fonts, random, time
disp = kooka.display
mode_ptr = 0
modes = ['Show','Dec','Hex']
controls = ['-   No   +','Pick  Show','Pick  Show']
mode_max = len(modes)
values = [256,16,1]
hex_no = [0] * 3    # The computed octal number as digits
userhex_no = [0] * 3    # The user's octal data entry
dec_no = 0    # The decimal number
userd_no = 0    # User entered decimal number
dec_max = 16 ** len(hex_no) - 1   # maximum decimal catered for
show_dec = 1    # flag to hide/show the decimal number
show_hex = 1    # flag to hide/show the binary number
random.seed(time.ticks_ms())    # seed the random number generator using the time

# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Hex Numbers', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 63)
    disp.text('%s' % modes[mode_ptr], 94, 63)
    disp.text('%s' % controls[mode_ptr], 20, 63)
# Change the mode of operation between showing and solving numbers
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        if mode_ptr == mode_max: mode_ptr = 0
        if mode_ptr == 0: show_hex = show_dec = 1
        else: show_hex = show_dec = 0
# Adjust the numbers according to the mode using the C and D keys
    if kooka.button_c.was_pressed():
        if mode_ptr == 0:
            dec_no = max(0, dec_no - 1)
        elif mode_ptr == 1:    # Random decimal, user solves binary
            dec_no = random.getrandbits(12)
            show_hex = 0
            show_dec = 1
        else:    # Random binary, user solves decimal
            dec_no = random.getrandbits(12)
            show_dec = 0
            show_hex = 1
    if kooka.button_d.was_pressed():
        if mode_ptr == 0:
            dec_no = min(dec_max, dec_no + 1)
        else: show_hex = show_dec = 1
# Compute the hex number from the decimal
    remainder = dec_no
    for i in range(0,3): 
        hex_no[i] = int(remainder/values[i])
        remainder = remainder % values[i]
# Display the results
    disp.setfont(fonts.sans12)
    if show_dec: disp.text('%4d' % dec_no, 10, 27)
    disp.setfont(fonts.mono6x7)
    disp.text('Decimal', 70, 25)
    disp.setfont(fonts.sans12)
    if show_hex:
        for i in range(0,3): disp.text(('%s' % hex(hex_no[i]))[2:].upper(), 20 + 26*i, 47)
    disp.setfont(fonts.mono5x5)
    for i in range(0,3): disp.text('%d' % values[i], 34 + 26*i, 52)
    
    disp.show()
# Exit

