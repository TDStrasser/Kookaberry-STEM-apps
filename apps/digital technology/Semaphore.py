# File name: Semaphore.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 11 Mar 2019
# Date last modified: 5 December 2020
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
# Sends and receives one of three signals over the radio: a wave, a like, and a digital output (LED, Buzzer etc)
# Buttons C, D and B initiate the respective transmissions
# Use two or more Kookaberries with the same app. All will receive the transmissions and report accordingly.
# December 2020 - modified message formats to coexist with the SenseXX apps
# Dependencies
#    in \lib    KappUtils.py
#    in root    Kookapp.cfg
# Begin code
import os, time, json, machine, kooka, fonts, framebuf
from Kapputils import config    # utility to read the configuration file

buz_pin = 'P2'
output = machine.Pin(buz_pin, machine.Pin.OUT)    # create the digital output
beeps_snd = [200,50,100,50,100,50,200,50,200]
beeps_rcv = [200,50,200]
# Create bitmaps
icons = [0] * 3

# Wave symbol
wave = bytearray([0x0C, 0x02, 0x05, 0x01, 0xF0, 0x08, 0xF8, 0x04, 0xFC, 0xF8, 0x08, 0xF8, 0x11, 0xE5, 0x02, 0x0C,
0x00, 0x03, 0x05, 0x09, 0x33, 0xC0, 0x81, 0x80, 0x81, 0x81, 0x80, 0x83, 0xE0, 0x1F, 0x00, 0x00])
icons[0] = framebuf.FrameBuffer(wave, 16, 16, framebuf.MONO_VLSB)

# Like symbol
like = bytearray([0x00, 0x00, 0x00, 0x80, 0x40, 0x18, 0x06, 0x72, 0x5E, 0xC0, 0x40, 0x40, 0x40, 0x80, 0x00, 0x00,
0x00, 0x00, 0x3F, 0x43, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7F, 0x55, 0x55, 0x75, 0x1D, 0x03, 0x00])
icons[1] = framebuf.FrameBuffer(like, 16, 16, framebuf.MONO_VLSB)

# Signal symbol
signal = bytearray([0x00, 0x80, 0x00, 0xC0, 0xF8, 0x00, 0xFC, 0x00, 0x00, 0x80, 0x00, 0xE0, 0xC0, 0x00, 0xF0, 0x00,
0x00, 0x01, 0x00, 0x03, 0x1F, 0x00, 0x3F, 0x00, 0x00, 0x01, 0x00, 0x07, 0x03, 0x00, 0x0F, 0x00])
icons[2] = framebuf.FrameBuffer(signal, 16, 16, framebuf.MONO_VLSB)

disp = kooka.display    # instantiate the display
params = config('Kookapp.cfg')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file

kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # set up the radio
validsigs = ['1','2','3']    # allowable signal payloads
sndmsg = [params['NAME'],'Sem4','0']
rcvbuf = ['0',' ','0']
rcvmsg = ['0',' ','0']
rcv_OK = False
rcv_new = False
# The main loop begins here
while not kooka.button_a.was_pressed():
# Set up some key variables
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Semaphore', 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('Buz:%s' % buz_pin, 100, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('Wave', 20, 60)
    disp.text('Like', 60, 60)
    disp.text('Sig', 100, 60)
# Process any message received
    msg = kooka.radio.receive()    # Check for radio messages
    if msg:
        rcvbuf = json.loads(msg)
        rcv_OK = rcvbuf[1] == sndmsg[1] and rcvbuf[2] in validsigs
        if rcv_OK: # if a valid message
            for i in range(0,len(rcvbuf)): rcvmsg[i] = rcvbuf[i]    # update received
            rcv_new = True

# Process the key presses
    if kooka.button_c.was_pressed(): # Wave
        sndmsg[2] = validsigs[0]
        kooka.radio.send(json.dumps(sndmsg))
    if kooka.button_d.was_pressed(): # Like
        sndmsg[2] = validsigs[1]
        kooka.radio.send(json.dumps(sndmsg))
    if kooka.button_b.was_pressed(): 
        sndmsg[2] = validsigs[2]
        output.value(0)
        for i in range(0,len(beeps_snd)):
            output.value(not output.value())
            time.sleep_ms(beeps_snd[i])
        output.value(0)
        kooka.radio.send(json.dumps(sndmsg))

# Display semaphore messages
    disp.text('Tx: %s' % sndmsg[2], 0, 25)
    disp.text('%s' % sndmsg[0], 70, 25)
    disp.text('Rx: %s' % rcvmsg[2], 0, 45)
    disp.text('%s' % rcvmsg[0], 70, 45)
# Display icons
    snd_ptr = int(sndmsg[2])-1
    if snd_ptr >= 0: disp.blit(icons[snd_ptr], 40, 15)
    rcv_ptr = int(rcvmsg[2])-1
    if rcv_ptr >= 0: disp.blit(icons[rcv_ptr], 40, 35)
    disp.show()
# Process receive action
    if rcv_new:
        if rcvmsg[2] == validsigs[2]:
            output.value(0)
            for i in range(0,len(beeps_rcv)):
                output.value(not output.value())
                time.sleep_ms(beeps_rcv[i])
            output.value(0)
        rcv_new = False

# Clean up and exit
kooka.radio.disable()
