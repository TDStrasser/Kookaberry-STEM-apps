# File name: 
__name__ = 'Firefly'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 15 December 2020
# Date last modified: 17 December 2020
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
# Emulates a Firefly by signalling using the radio, and flashing a LED.
# Firefly gender is chosen at random on initialisation, as is the number of flashes that distinguish the Firefly.
# Gender can be forced by button C (male / female)
# Listeners, acting as females, will respond if the flashes matches their own.
#  Fireflies can be choosy or fickle and respond to any number of flashes (selected by button D)
# Use two or more Kookaberries with the same app. All will receive the transmissions and report accordingly.
# Dependencies
#    in \lib    KappUtils.mpy
#    in root    Kookaapp.cfg
# Begin code
import os, time, json, machine, kooka, fonts, framebuf, random
from Kapputils import config    # utility to read the configuration file

output = machine.Pin('P2', machine.Pin.OUT)    # create the digital output
# Firefly symbols
firefly_on = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x40, 0x60, 0x70, 0x78, 0x7C, 0x78, 0x70, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x07,
0x0F, 0x1F, 0x3F, 0x7F, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0x7F, 0x3F, 0x3F, 0xBF, 0xDF, 0xFF, 0xFF,
0xFF, 0xFF, 0xFF, 0xDF, 0xBF, 0x3F, 0x3F, 0x7F, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x1F,
0x0F, 0x07, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x01, 0x00, 0x00, 0x08, 0x1C, 0x3E, 0x7F, 0x7F, 0x3F, 0x0F, 0x07, 0x83, 0x07, 0x0F, 0x3F, 0x7F,
0x7F, 0x3E, 0x1C, 0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x08, 0x3C, 0xFE, 0xFF, 0xFF, 0xFF, 0xFE, 0x3C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x03, 0x0F, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
firefly_off = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x40, 0x60, 0x70, 0x78, 0x7C, 0x78, 0x70, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x07,
0x0F, 0x1F, 0x3F, 0x7F, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0x7F, 0x3F, 0x3F, 0xBF, 0xDF, 0xFF, 0xFF,
0xFF, 0xFF, 0xFF, 0xDF, 0xBF, 0x3F, 0x3F, 0x7F, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x1F,
0x0F, 0x07, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x01, 0x00, 0x00, 0x08, 0x1C, 0x3E, 0x7F, 0x7F, 0x3F, 0x0F, 0x07, 0x83, 0x07, 0x0F, 0x3F, 0x7F,
0x7F, 0x3E, 0x1C, 0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x08, 0x28, 0xAA, 0xAB, 0xAB, 0xAB, 0xAA, 0x28, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x02, 0x0E, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
ffly = [framebuf.FrameBuffer(firefly_off, 43, 40, framebuf.MONO_VLSB),framebuf.FrameBuffer(firefly_on, 43, 40, framebuf.MONO_VLSB)]

disp = kooka.display    # instantiate the display
params = config('Kookapp.cfg')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file

kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # set up the radio
id = ''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
valid_gen = ['F','M']
gender = ['Fem','Male']
constant = ['Constant','Fickle']
rcv_OK = False    # Valid message received flag
rcv_new = False    # New valid message flag
male = random.randint(0,1)    # Gender selected randomly
b_min = 2
b_max = 6
sndmsg = [id,'FF',valid_gen[male],'%d' % random.randint(b_min,b_max)]    # Template message [ID,FF,F or M, number] all strings for compatibility with SenseRx
fickle = False    # Whether, if female, one responds to all males
blink_time = 500    # Half period of blinking
t_blink = time.ticks_ms() + blink_time    # Initialse the blinker timer
blinker = True    # Flag toggles every blink half period
blinking = False
blink = False    # Flag blinks when blinking is needed
blinks = 0    # The number of blinks when blinking
ffly_send_time = random.randint(b_max+2,b_max*2) * 1000    # Male send interval
t_ffly_send = time.ticks_ms() + ffly_send_time
do_blink = False    # Flag controls the blinking cycle
do_tx = False    # Flag controls radio transmission
tx_count = 0    # Counters to keep reply statistics
rx_count = 0
ffly_nx = 10    # Variable used to position and move the firefly
ffly_dx = 10
ffly_ny = 12
ffly_dy = 12
ffly_ax = ffly_nx
ffly_ay = ffly_ny

# The main loop begins here
while not kooka.button_a.was_pressed():
# Set up some key variables
    if time.ticks_diff(time.ticks_ms(), t_blink) >= 0:    # Toggle the blinker
        t_blink = time.ticks_ms() + blink_time
        blinker = not blinker
        if not blinker: blinks += 1
        
    if blinks >= int(sndmsg[3]):    # Is blinking period complete?
        if blinking: do_tx = True    # Transmit radio at end of blinking
        blinking = False    # Reset the blinking status
        
    blink = blinker and blinking    # Otherwise follow the blinker 
    
    rx_ratio = rx_count / max(tx_count, 1) * 100
    
# Adjust the firefly's display position to simulate hovering
    ffly_ax += random.randint(-1,1)
    ffly_ax = max(ffly_nx - ffly_dx, min(ffly_nx + ffly_dx, ffly_ax))
    ffly_ay += random.randint(-1,1)
    ffly_ay = max(ffly_ny - ffly_dy, min(ffly_ny + ffly_dy, ffly_ay))
    if blinking: time.sleep_ms(150)    # Slower speed of hovering
    else:    time.sleep_ms(50)    # Faster hovering


# Display the static text
    if male: gender = 'Male'
    else: gender = 'Fem'
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text(__name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s Bk %s' % (gender, sndmsg[3]), 70, 6)    # Gender and no of flashes
    disp.text(constant[fickle], 70, 20)
    if male: disp.text('Repl %0.0f%%' % rx_ratio, 70, 30)
    disp.text('A-exit', 0, 60)
    disp.text('C-Gender', 70, 40)
    disp.text('D-Const', 70, 50)
    disp.text('B-Blinks', 70, 60)
    disp.blit(ffly[blink], ffly_ax, ffly_ay, 0)
    
# Process any message received
    try:    msg = kooka.radio.receive()    # Check for radio messages
    except: 
        kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # initialise the radio
        print('Radio restarted')

    if msg:
#        print(msg)
        if not blinking:
            rcvbuf = json.loads(msg)
            rcv_OK = rcvbuf[1] == sndmsg[1] and rcvbuf[2] in valid_gen 
            if rcv_OK: # if a valid message
                rcvmsg = rcvbuf    # update last received message
                rcv_new = True

# Process the key presses
    if kooka.button_c.was_pressed(): # Change gender
        male = not male
        sndmsg[2] = valid_gen[male]
    if kooka.button_d.was_pressed(): # Constant or fickle
        fickle = not fickle
    if kooka.button_b.was_pressed(): 
        sndmsg[3] = '%d' % random.randint(b_min,b_max)    # Select number of flashes

    disp.show()
# Process receive action
    if rcv_new:
        if not male and rcvmsg[2] == 'M':    # For females reply to males if matching or all if fickle
            if fickle:
                sndmsg[3] = rcvmsg[3]    # Change own id to follow the sender
                blink_dur_time = blink_time * int(sndmsg[3]) * 2   # the duration of blinking
            if rcvmsg[3] == sndmsg[3]:
                do_blink = True    # Start response
                
        if male and rcvmsg[2] == 'F':    # Male receives a female message
            if rcvmsg[3] == sndmsg[3]:    # Male hears a matching response
                do_blink = True    # Responds to the response
                rx_count += 1
            elif fickle: do_blink = True    # Muscle in on conversation anyway
        rcv_new = False

# Courting time for males
    if male and time.ticks_diff(time.ticks_ms(), t_ffly_send) >= 0:
        t_ffly_send = time.ticks_ms() + ffly_send_time
        if not blinking: do_blink = True    # Start if not already sending

# Process radio transmission and blinking of LEDs
    if do_blink:    # If a reply is required
        blinking = True
        blinks = 0
        t_blink = time.ticks_ms() + blink_time    # Reset the blinker to avoid partial blinks
        blinker = False
        do_blink = False
        
    if do_tx:    # Set at the end of the blinking period
        try: 
            kooka.radio.send(json.dumps(sndmsg))    # Send the radio message
            tx_count += 1
#            print(sndmsg)
            t_ffly_send = time.ticks_ms() + ffly_send_time    # reset the courting timer
        except:
            kooka.radio.config(channel=chan, data_rate=baud, power=pwr) # initialise the radio
            print('Radio restarted')

        do_tx = False
        
    if blink: kooka.led_green.on()    # Control the green LED
    else: kooka.led_green.off()
    output.value(blink)    # Control the external ouput (LED)
    
# Clean up and exit
kooka.radio.disable()
