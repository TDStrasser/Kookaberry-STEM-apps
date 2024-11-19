# File name: TrafficLights.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 25 October 2019
# Date last modified: 26 October 2019
# MicroPython Version: 1.10 for the Kookaberry V4-05 after 2019-08-08
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
# A simulation of an intersection employing approach sensors and multi-coloured LEDs
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: NeoPixel array on P2.  Call digital sensors on P4 and P5 (optional)
# /lib files: neopixel.py
# /root files: nil
# Other dependencies: NeoPixel firmware 2019-08-08 or after
# Complementary apps: NeoPixelTest.py to test NeoPixel functions
#------------------------------------------

# Begin code
pixels_in_array = 4    #Number of NeoPixels used for traffic lights
import kooka, neopixel, machine, fonts
np = neopixel.NeoPixel(machine.Pin('P2'), pixels_in_array)
import time
callinp = [0,0]
call0 = machine.Pin('P4', machine.Pin.IN, machine.Pin.PULL_DOWN)    # create digital input for button or other digital device
call1 = machine.Pin('P5', machine.Pin.IN, machine.Pin.PULL_DOWN)    # create digital input for button or other digital device
disp = kooka.display

# Initial conditions
path = [0,0]    # states of each path through the intersection
call = [0,0]    # call latches for each path
grant = [0,0]    # grant token to indicate safe
pixels = [0,1]    # Neopixel addresses for each path
# parameters for state machine display
block_width = 20
block_space = 25
block_height = 13
block_x = 5
block_y = [10,38]
block_char_x = 2
block_char_y = block_height-3
states_y = 23
blink = 0

# Set up objects
states = ['Red','clr','Gn','Amb']    # traffic light states
red = (32,0,0)    # colour definitions for NeoPixel LEDs
green = (0,32,0)
amber = (24,8,0)
white = (11,11,11)
black = (0,0,0)
lights = [red,red,green,amber]    # light colours corresponding to each state
times = [10,6,10,3]
timers = [10,6,10,3]
for i in range(0,len(times)): timers[i] = times[i]
calltimes = [20,20]
calltimers = [20,20]
for i in range(0,len(calltimes)): calltimers[i] = calltimes[i]

# Set up interrupts to handle digital inputs as button press may be missed during loop delay
def calldetect(p):
    if p == call0: call[0] = True
    if p == call1: call[1] = True

call0.irq(trigger=machine.Pin.IRQ_RISING, handler=calldetect)
call1.irq(trigger=machine.Pin.IRQ_RISING, handler=calldetect)

# Start loop
while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('TrafficLights', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-ex  C-ca1  D-ca2', 0, 60)


# Read inputs
    for i in range(0,len(path)):
        if kooka.button_c.was_pressed(): call[0] = True
        if kooka.button_d.was_pressed(): call[1] = True
        if not calltimers[i]: call[i] = True    # generate call after call timeout
# Perform calculations - criteria for state machine transitions
    for i in range(0,len(path)):
        if path[i] == 0:    # Stop state
            next = i+1
            if next >= len(path): next = 0
            grant[next] = True
            if call[i] and not timers[path[i]]:    # if call and timer expired
                timers[path[i]] = times[path[i]]    # reset state timer
                path[i] += 1    # advance to next state
            pass
        elif path[i] == 1:    # Wait state - safety pause and wait for grant
            next = i+1
            if next >= len(path): next = 0
            grant[next] = True
            if grant[i] and not timers[path[i]]:    # if clear and timer expired
                timers[path[i]] = times[path[i]]    # reset state timer
                path[i] += 1    # advance to next state       
            pass
        elif path[i] == 2:    # Go state (green light)
            next = i+1
            if next >= len(path): next = 0
            grant[next] = False
            if call[next] and not timers[path[i]]:    # if call from next and timer expired
                timers[path[i]] = times[path[i]]    # reset state timer
                path[i] += 1    # advance to next state       
            pass
        elif path[i] == 3:    # Slow state (amber light)
            next = i+1
            if next >= len(path): next = 0
            grant[next] = False
            if not timers[path[i]]:    # if call from next and timer expired
                timers[path[i]] = times[path[i]]    # reset state timer
                call[i] = False
                calltimers[i] = calltimes[i]
                path[i] = 0    # advance to stop state       
            pass
# Display variables
# Draw the state machine blocks bar and fill active state timers
    for j,y in enumerate(block_y):
        for i in range(0,len(states)):
            x = block_x + i * block_space
            disp.rect(x,y,block_width,block_height,1)    # outline rectangles
            if i == path[j]:
                disp.fill_rect(x,y,block_width,block_height, 1)
                disp.text('%2d' % timers[path[j]],x+block_char_x,y+block_char_y,0)
# Draw the state labels
    for i,s in enumerate(states):
        x = block_x + i * block_space + block_char_x
        y = states_y + block_char_y
        disp.text('%s' % s, x, y)
# Draw the call states and timers
    blink = not blink
    for i,y in enumerate(block_y):
        x = block_x + len(states) * block_space
        if call[i]: disp.fill_rect(x+2,y+2,block_width-4,block_height-4,blink)
        else: disp.text('%2d' % calltimers[i],x+block_char_x,y+block_char_y)
    x = block_x + len(states) * block_space
    y = states_y + block_char_y
    disp.text('Call', x, y)

    disp.show()
# Set outputs
    np.fill(black)    # clear pixels
    for i in range(0,len(path)):
        for j in range(0,pixels_in_array/2):
            np[2*j+i] = lights[path[i]]    # set signal lights
    np.write()
# Adjust timers and counters
    time.sleep_ms(980)    # run loop at approximately 1 second intervals (not precise)
    for i in range(0,len(path)):
        timers[path[i]] = max(0,timers[path[i]]-1)
        calltimers[i] = max(0,calltimers[i]-1)

# Clean up and exit
np.fill(black)
np.write()