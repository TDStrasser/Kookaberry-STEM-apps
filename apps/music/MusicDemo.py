# File name: MusicDemo.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 8 February 2019
# Date last modified: 28 April 2019
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
# Demonstration of the Kookaberry Music functionality
# A loudspeaker is attached to plug P2
# Begin code
import machine, kooka, musictunes, music, fonts
p = musictunes.tunes.keys()
names = sorted(list(p))
ptr = 0
disp = kooka.display
spkrpin = 'P2'
# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Music Demo', 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('Plug Speaker into %s' % spkrpin, 0, 16)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('Prev', 20, 60)
    disp.text('Next', 55, 60)
    disp.text('Play', 95, 60)
    disp.setfont(fonts.mono8x8)    # for key no display
    disp.text('%s' % names[ptr], 0, 30)
    disp.text('%d of %d' % (ptr+1, len(names)), 20, 50)
# Adjust the input logic using the C and D keys
    if kooka.button_c.was_pressed(): ptr = max(0, ptr-1)
    if kooka.button_d.was_pressed(): ptr = min(len(names)-1, ptr+1)
    if kooka.button_b.was_pressed(): music.play(musictunes.tunes[names[ptr]], pin=machine.Pin(spkrpin))
    disp.show()



