# File name: 
__name__ = 'Metronome'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 13 February 2019
# Date last modified: 10 August 2020
# MicroPython Version: 1.12 for the Kookaberry V4-05
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
# A simulated metronome for providing music tempo
# Port P1 is attached to a digital capacitive sensor or switch
# Port P2 is attached to a loudspeaker.  The metronome beat is a PWM signal
# Begin code
import machine, kooka, music, fonts, time
modes = ['BPM','Acc','Beep']
cbtn = ['Dn','Dn','On']
dbtn = ['Up','Up','Off']
mode_ptr = 0
bpm_array = [10, 20, 30, 40, 44, 48, 50, 52, 54, 56, 58, 60, 63, 66, 69, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 126, 132, 138, 144, 152, 160, 168, 176, 184, 192, 200, 208]
bpm_ptr = 22    # Initial BPM
bpm_len = len(bpm_array)
tempos = ['Larghissimo','Grave','Lento/Largo','Larghetto','Adagio','Adagietto','Andante','Moderato','Allegro','Vivace','Presto','Prestissimo']
tempo_limits = [20,40,60,66,76,80,108,120,140,168,200,400]
accent = 4    # Accent beat
accent_max = 8    # Limit of accent beat
accent_ctr = 1
play = 0    # Whether to play the metronome
intv_timer = 0  # initialise the interval timer
metro_y = 10
metro_h = 10
metro_x = 10
spkr_pin = 'P2'
bt_pin = 'P1'
disp = kooka.display
t0 = time.ticks_ms() # mark the time in ticks at the beginning of the program
# Set up the digital input for beat timing - any digital sensor is accepted
beat_pin = machine.Pin(bt_pin, machine.Pin.IN)
beat_timer =[0,0,0]    # bytearray time now, time last, time interval
tnow = tlast = time.ticks_ms()    # initialise the time
beat = 0    # Variable for beat
beat_limit = 300    # Maximum beats per minute - values greater will be ignored

def pulserate(p):    # handler for interrupt driven pulse rate
    beat_timer[0] = time.ticks_ms() # mark the time in ticks at the interrupt
    intv = beat_timer[0] - beat_timer[1]    # interval = tine now minus last time
    if intv >= 20:    # only react to pulses greater than 20ms apart
        beat_timer[2] = beat_timer[0] - beat_timer[1]  
        beat_timer[1] = beat_timer[0]
    return

beat_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulserate)

# The main loop begins here
while not kooka.button_a.was_pressed():
# Set up some key variables
    bpm = bpm_array[bpm_ptr]    # current beats per minute
    period_ms = 60000 / bpm    # milliseconds between beats
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('Spk %s Bt %s' % (spkr_pin,bt_pin), 74, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('%s' % cbtn[mode_ptr], 20, 60)
    disp.text('%s' % dbtn[mode_ptr], 55, 60)
    disp.text('%s' % modes[mode_ptr], 95, 60)
    disp.setfont(fonts.mono8x8)    # for BPM display
    disp.text('%3d BPM' % bpm, 10, 50)
    for i in range (0,len(tempo_limits)):    # Name the tempo
        tempo = tempos[i]
        if bpm <= tempo_limits[i] : break
    disp.text('%s' % tempo, 10, 40)
    disp.text('Acc: %d' % accent, 75, 50)
# Adjust the parameters using the C and D keys
    if kooka.button_c.was_pressed(): 
        if mode_ptr == 0: bpm_ptr = max(0, bpm_ptr-1)
        if mode_ptr == 1: accent = max(1, accent-1)
        if mode_ptr == 2: play = 1
    if kooka.button_d.was_pressed(): 
        if mode_ptr == 0: bpm_ptr = min(bpm_len-1, bpm_ptr+1)
        if mode_ptr == 1: accent = min(accent_max, accent+1)
        if mode_ptr == 2: play = 0
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        if mode_ptr > len(modes)-1: mode_ptr = 0
# Work out the external beat
    beat_last = beat    # remember the previous beat
    if beat_timer[2] > 0: beat = int(60000 / beat_timer[2])
    if beat > beat_limit: beat = beat_last    # ignore improbable beat samples
    beat_still = abs(t0 - beat_timer[1])    # time since the last interrupt
    if beat_still > 2000 : beat = 0 # if no interrupts received in 2 secs set beat to zero
    disp.text('Beat = %3d BPM' % beat, 10, 30)
# Draw the metronome bar
    metro_w = int((64-metro_x)/accent*2)
    for i in range(0,accent):
        x = metro_x + i * metro_w
        y = metro_y
        disp.rect(x,y,metro_w,metro_h,1)    # outline rectangle
        if i == accent_ctr - 1:
            disp.fill_rect(x+2 , y+2, metro_w-4 , metro_h-4, 1)

# Work out the timing and advance the metronome
    t1 = time.ticks_ms() # mark the time in ticks
    intv_timer += t1 - t0
    t0 = time.ticks_ms() # mark the time in ticks at the end of the loop
    if intv_timer >= period_ms:    # reset interval timer every interval
        intv_timer = 0
    if intv_timer == 0:    # advance the metronome
        note = 'A3:1'
        if accent_ctr == accent: note = 'A4:1'
        accent_ctr += 1
        if accent_ctr > accent: accent_ctr = 1
        if play: music.play(note, pin=machine.Pin(spkr_pin),wait=False)
    disp.show()
