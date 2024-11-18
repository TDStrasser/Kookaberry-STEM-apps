# File name: MoveMusic.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 2 October 2018
# Date last modified: 22 November 2020
# MicroPython Version: 1.9.4 for the Kookaberry V4-05
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
# Play musical notes using gestures tracked by the accelerometer
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: P4 amplified loudspeaker, P5 button (optional)
# /lib files: nil
# /root files: nil
# Other dependencies: nil
# Complementary apps: nil
#------------------------------------------

# Begin code
import machine, kooka, math, time, fonts
from array import array
# create a sine waveform with two octave overtones
buf = array('H', 2048 + int(1170*math.sin(2*math.pi*i/128)+585*math.sin(4*math.pi*i/128)+292*math.sin(8*math.pi*i/128)) for i in range(128))
# the musical scale from C4 to B4
notes = [261.63,293.66,329.63,349.23,392,440,493.88]
names = ['C','D','E','F','G','A','B']
scale = len(notes)
octaves = [0.125, 0.25, 0.5, 1, 2, 4, 8]    # multipliers for each octave
mod_state= ['Off','On']
note_min = 125    # Minimum note length
tkey = time.ticks_ms()    # Initialse the key pressed timer
# Create an initialise other variables
t_since = 0
key = 0
last_f = 0
f_changed = 0
f_vary = 0
pin_DAC = 'P4'
pin_btn = 'P5'
# Set up the DAC
dac = machine.DAC(machine.Pin(pin_DAC),bits=12)
# Set up the external play button
button = machine.Pin(pin_btn, machine.Pin.IN, machine.Pin.PULL_DOWN)    # create digital input for button or other digital device
# Set up the display
disp = kooka.display
# Main loop
while not kooka.button_a.was_pressed():
    if kooka.button_c.was_pressed():
        f_vary = not(f_vary)    # Turn pitch modulation on / off
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Move Music', 0, 10)
    disp.setfont(fonts.mono5x5)
    disp.text('Spkr %s' % pin_DAC, 94, 8)
    disp.text('Btn %s' % pin_btn, 98, 14)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 63)
    disp.text('Gli=%s' % mod_state[f_vary], 25, 63)
    disp.text('D-Play', 85, 63)
# Read the accelerometer and set up pitch and octave
# Forward and backward tilt adjusts the note
# Left and right tilt adjusts the octave
# Up and down vibration adds glissando (pitch variation)
    x, y, z = kooka.accel.get_xyz()
    pitch = int(-x / 9.8 * 12)    # pitch goes from -12 to 12
    p_octave = pitch // scale
    pitch = min(max(0,pitch - p_octave * scale), scale-1)    # bring pitch back into range
    octave = min(max(0,int(-y / 9.8 * 3) + 3 + p_octave),len(octaves)-1)    # octave goes from 0 to 8
    vary = 1
    if f_vary:
        vary = (z+9.8) / 9.8 * 1.06 + 1    # vary the pitch up or down by up to 6% per g-force subtracting gravity first
    f = int(notes[pitch] * octaves[octave] * vary)
    if not f == last_f:    # has the frequency changed?
        f_changed = 1
        last_f = f
# Display the note and octave and the frequency
    disp.setfont(fonts.sans12)
    disp.text('%s%d' % (names[pitch],octave+1), 40, 36)
    disp.setfont(fonts.mono6x7)
    disp.text('Freq: %d Hz' % f, 25, 52)
    disp.show()
# Press button D or the external button to play the note(s)
    if kooka.button_d.is_pressed() or button.value():
        if not key:
            dac.write_timed(buf, f * len(buf), mode=machine.DAC.CIRCULAR)    # Outputs the sine wave to the D/A Converter
            key = 1    # Remember the key was pressed
            tkey = time.ticks_ms()    # Remember when the key was pressed
    else: 
        dac.write(2048)    # Silence - output half DAC scale
        key = 0    # Remember the key release
    time.sleep_ms(50)
#Work out if the minimum note timer has elapsed
    tnow = time.ticks_ms()
    t_since = time.ticks_diff(tnow, tkey)
    if t_since > note_min and f_changed: 
        key = 0  # Allow new note after minimum time
        f_changed = 0    # reset freq changed flag
# Go round the loop again.
# On exit reset the DAC
dac.deinit()