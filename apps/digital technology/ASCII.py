# File name: 
__name__ = 'ASCII'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 29 July 2021
# Date last modified: 29 July 2021
# Version 1.0
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
# Shows the printable ASCII character and their codes
#------------------------------------------
# Dependencies: nil
# I/O ports and peripherals: nil
# /lib files: nil
# /root files: nil
# Other dependencies: nil
# Complementary apps: nil
#------------------------------------------

# Begin code
import kooka, fonts, random, time
disp = kooka.display
# Initial conditions
ascii_lo = 0x20
ascii_hi = 0x7E
current_char = random.randrange(ascii_lo, ascii_hi)

# The main loop
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text(__name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('printable', 45, 6)
    disp.text('A-ex C-prev D-nxt', 0, 60)
# Select the character to be shown
    if kooka.button_c.was_pressed():
        current_char -= 1
        if current_char < ascii_lo: current_char = ascii_hi
    if kooka.button_d.was_pressed():
        current_char += 1
        if current_char > ascii_hi: current_char = ascii_lo
# Display the printable ASCII character
    if current_char > ascii_lo: 
        disp.setfont(fonts.sans12)
        disp.text('%s' % current_char.to_bytes(1,'big').decode('utf-8'), 100, 34)
    else:
        disp.setfont(fonts.mono8x8)
        disp.text('space', 90, 34)
    disp.setfont(fonts.mono6x7)
# Display the ASCII code in numeric representation
    disp.text('%8s bin' % bin(current_char).lstrip('0b'), 0, 20)
    disp.text('%s hex' % hex(current_char).lstrip('0x').upper(), 20, 30)
    disp.text('%3d dec' % current_char, 13, 40)
    disp.show()


# Perform calculations

# Display variables

# Set outputs

# Adjust timers and counters

# Clean up and exit