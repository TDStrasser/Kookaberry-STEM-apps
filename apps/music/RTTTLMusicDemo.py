# File name: RTTLMusicDemo.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 20 Jun 2019
# Date last modified: 20 Jun 2019
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
# This demo plays RTTL format music on the Kookaberry
# The RTTL formatted tunes are in the library file songs.py
# The RTTL library is by D.Hayman
# A loudspeaker is attached to plug P2
# Begin code
import machine, kooka, fonts, time, music
from rttl import RTTTL
import songs
spkrpin = 'P2'

def play_tone(freq, msec):
#    print('freq = {:6.1f} msec = {:6.1f}'.format(freq, msec))
    if freq > 0:
        music.pitch(int(freq),int(msec*0.9),pin=machine.Pin(spkrpin))
    time.sleep_ms(int(msec * 0.1))

def play(tune):
    try:
        for freq, msec in tune.notes():
            play_tone(freq, msec)
    except KeyboardInterrupt:
        play_tone(0, 0)

def play_song(search):
    play(RTTTL(songs.find(search)))

ptr = 0
disp = kooka.display
# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('RTTL Music Demo', 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('Plug Speaker into %s' % spkrpin, 0, 16)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('Prev', 20, 60)
    disp.text('Next', 55, 60)
    disp.text('Play', 95, 60)
    disp.setfont(fonts.mono8x8)    # for key no display
    disp.text('%s' % songs.SONGS[ptr].split(':')[0]
, 0, 30)
    disp.text('%d of %d' % (ptr+1, len(songs.SONGS)), 20, 50)
# Adjust the input logic using the C and D keys
    if kooka.button_c.was_pressed(): ptr = max(0, ptr-1)
    if kooka.button_d.was_pressed(): ptr = min(len(songs.SONGS)-1, ptr+1)
    if kooka.button_b.was_pressed(): play(RTTTL(songs.SONGS[ptr]))
    disp.show()



