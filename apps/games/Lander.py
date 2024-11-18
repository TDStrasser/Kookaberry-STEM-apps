# File name: 
__name__ = 'Lander'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 1 September 2020
# Date last modified: 2 Sept 2020 2nd release
# version 1.1
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
# Description
# A simple Lunar Lander game.
# The aim is to land on the pad and to not crash.
# Controls A=exit B=vertical thrust C=left thrust D=right thrust
# Fuel is a constraint - if you use it up you may crash
# After landing or crash button B resets the game
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------

# Begin code
import machine, kooka, fonts, random, framebuf, time
disp = kooka.display
# The lander graphic
lander_w = 15
lander_h = 16
bitmap = bytearray([0x00, 0x00, 0x00, 0x70, 0xCC, 0x04, 0xFE, 0x02, 0xFE, 0x04, 
0x9C, 0x70, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x7C, 0x1F, 0x0F, 0x0F, 0x0F, 0x0E, 
0x0F, 0x0F, 0x0F, 0x1F, 0x78, 0xC0, 0x00])
lander = framebuf.FrameBuffer(bitmap, lander_w, lander_h, framebuf.MONO_VLSB)
# Initial conditions
acceleration = 0.05    # gravity pixels/period/period
thrust_y = -acceleration * 2    # descent thrust
thrust_x = -acceleration * 2    # traverse thrust
landing_x = 0.5    # Limit of traverse speed for landing
landing_y = 1.0    # Limit of descent speed for landing
fuel_x = 1    # fuel used per traverse thrust
fuel_y = 1.5    # fuel used per descent thrust
width = 127    # display width
height = 63    # display height
reset = True    # whether to reset the game
quit = False    # used to quit during rules display

# Introductory game display
rules = ['Simple Lunar Lander','Land on the pad',' without crashing','Max landing speed:',' descent %2.1f' % landing_y,' traverse %2.1f' % landing_x,'Watch your fuel','Control buttons:',' B- descent thrust',' C- left thrust',' D- right thrust','Press B to play','Press A to quit',' ']
disp.fill(0)
disp.setfont(fonts.mono6x7)
rule_ptr = 0
# Function to scroll display
def dscroll(pixel_lines):
    for i in range(10):    # scroll smoothly
        disp.scroll(0,-1)
        disp.show()
        time.sleep_ms(100)
        
while not kooka.button_b.was_pressed() and not quit:    # quit rules loop and go to game
    if rule_ptr == 0:    # show the lander first
        dscroll(20)
        disp.blit(lander, 50, 45)    # display the lander
        disp.show()
    dscroll(10)
    disp.text(rules[rule_ptr], 0, 60)
    rule_ptr += 1
    disp.show()
    time.sleep_ms(1000)
    if rule_ptr >= len(rules): rule_ptr = 0
    if kooka.button_a.was_pressed(): quit = True

# Play the game
while not kooka.button_a.was_pressed() and not quit:    # Run loop until exit button pressed
    # Reset the game if called for
    if reset:
        lander_x = random.randint(2*lander_w,width-2*lander_w) # horizontal entry position
        lander_y = -lander_h    # vertical entry position (above the display)
        lander_xvel = random.random()- 0.5    # initial traverse velocity
        lander_yvel = random.random()    # initial descent velocity
        lander_xacc = 0    # initial traverse acceleration
        lander_yacc = acceleration    # initial descent acceleration
        crashed = False    # indicates if a crash occurred
        landed = False    # indicates if a safe landing
        lander_show = 0    # whether the lander is visible
        lander_xvel_show = True    # flashing flag for traverse velocity
        lander_yvel_show = True    # flashing flag for descent velocity
        fuel = 100    # initial fuel capacity
        target_x = random.randint(0,width-2*lander_w)
        target_y = height - 2
        reset = False    # reset the reset flag
    # Calculate lander speed, position, fuel limit and warning, and speed warnings
    lander_xvel += lander_xacc    # traverse velocity change
    lander_yvel += lander_yacc    # descent velocity change
    lander_x += lander_xvel    # traverse position
    lander_y += lander_yvel    # descent position
    fuel = max(0, fuel)    # limit the fuel when empty
    if fuel > 25: fuel_show = True    # fuel above warning level
    else: fuel_show = not fuel_show    # flashes fuel if below threshhold
    if lander_y > target_y - 2 * lander_h:
        if lander_yvel > landing_y: lander_yvel_show = not lander_yvel_show
        else: lander_yvel_show = True
        if lander_x > target_x - lander_w or lander_x < target_x + 3 * lander_w:
            if abs(lander_xvel) > landing_x: lander_xvel_show = not lander_xvel_show
            else: lander_xvel_show = True
    # Draw the display
    disp.fill(0)    # Clear the display
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)    # Display app title
    disp.setfont(fonts.mono6x7)
    disp.text('Desc:%3.1f' % lander_yvel, 72, 6, lander_yvel_show)    # Descent velocity display
    disp.text('Trav:%3.1f' % lander_xvel, 72, 16, lander_xvel_show)    # Traverse velocity display
    disp.text('Fuel:%0.1f%%' % fuel, 0, 16, fuel_show)    # Fuel display
    disp.fill_rect(target_x, target_y, 2*lander_w, 3, 1)    # landing pad
    # Reset accelerations before modification by controls
    lander_yacc = acceleration
    lander_xacc = 0
    # End of flight displays
    if crashed: # The lander crashed
        lander_show = not lander_show
        disp.setfont(fonts.sans12)
        disp.text('Crashed!', 15, 40, lander_show)
    if landed:    # Successful landing
        disp.setfont(fonts.mono8x8)
        disp.text('The Eagle', 0, 30)
        disp.text('has landed!', 20, 40)
    disp.blit(lander, int(lander_x), int(lander_y), lander_show)    # display the lander
    # Thrusters
    if fuel and not crashed and not landed:    # only if we have fuel and haven't finished the flight
        if kooka.button_b.is_pressed() or kooka.button_b.was_pressed(): # Vertical thruster - pulsed or continuous
            disp.fill_rect(int(lander_x+6),int(lander_y+14),3,7,1)
            lander_yacc += thrust_y
            fuel -= fuel_y
        if kooka.button_d.was_pressed(): # Right thruster (one pulse per press)
            disp.fill_rect(int(lander_x+14),int(lander_y+7),7,3,1)
            lander_xacc += thrust_x
            fuel -= fuel_x
        elif kooka.button_c.was_pressed(): # Left thruster (one pulse per press)
            disp.fill_rect(int(lander_x-7),int(lander_y+7),7,3,1)
            lander_xacc -= thrust_x
            fuel -= fuel_x
    # Work out if landed or crashed
    if not crashed and not landed:
        if lander_x < -lander_w or lander_x > width: crashed = True    # Out of traverse bounds
        if lander_y < -lander_h: crashed = True    # Went above the display
        if lander_y >= height - lander_h:    # At or below landing surface
            if abs(lander_xvel) > landing_x or lander_yvel > landing_y: crashed = True    # If approach velocity too high
            elif lander_x < target_x or lander_x > (target_x + lander_w + 1): crashed = True
            if not crashed: landed = True    # at position and velocities OK
            kooka.button_b.was_pressed()    # Reset button B
    if crashed or landed:    # Reset the game here
        lander_xacc = lander_xvel = 0    # Stop the lander moving
        lander_yacc = lander_yvel = 0
        disp.setfont(fonts.mono6x7)
        disp.text('A=exit', 0, 58)    # Display button options
        disp.text('B=reset', 80, 58)
        if kooka.button_b.was_pressed(): reset = True    # initiate reset
    disp.show()    # Show the display update
    time.sleep_ms(500)    # controls the speed of the game

