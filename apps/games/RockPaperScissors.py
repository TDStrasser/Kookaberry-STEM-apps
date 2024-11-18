# File name: RockPaperScissors.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 17 July 2018
# Date last modified: 11 June 2023 - changed blank bitmap to framebuf type
# Version 1.3
# MicroPython Version: 1.20 for the Kookaberry
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
# Rock paper scissors game for Kookaberry
# Dec 2020 - modified display so winner score blinks and game over indicated
# Begin code

import time, kooka, fonts, math, random, framebuf
disp = kooka.display


# Initialise Scores
kscore = 0	# Kooka's score
uscore = 0	# User's score
maxscore = 5
maxscore = max(2,min(9, maxscore)) # limit to a single digit and to more than 1
draw = '='
uwins = '>'
kwins = '<'
uchoice_r = [draw, kwins, uwins] # User = Rock, Kooka = Rock, Paper, Scissors
uchoice_p = [uwins, draw, kwins]    # User = Paper, Kooka = Rock, Paper, Scissors
uchoice_s= [kwins, uwins, draw]    # User = Scissors, Kooka = Rock, Paper, Scissors
decider = [uchoice_r, uchoice_p, uchoice_s]    # Winner logic matrix
kchoice = " "	# Kooka's selection generated randomly
uchoice = " "	# User's selection according to buttons
winner = " "	# Symbol indicating which player won the selection round

# Create bitmaps for the implements
# Blank
nomap = framebuf.FrameBuffer(bytearray(32), 16, 16, framebuf.MONO_HLSB)
nomap.fill(0)
# Paper
papermap = framebuf.FrameBuffer(bytearray(32), 16, 16, framebuf.MONO_HLSB)
papermap.fill(0)
papermap.rect(1,1,14,14,1)
papermap.line(1,14,14,1,1)
# Rock
rockmap = framebuf.FrameBuffer(bytearray(32), 16, 16, framebuf.MONO_HLSB)
rockmap.fill(0)
rockmap.fill_rect(1,1,8,8,1)
rockmap.fill_rect(4,4,8,8,1)
rockmap.fill_rect(8,8,8,8,1)
rockmap.fill_rect(2,8,6,6,1)
# Scissors
scissormap = framebuf.FrameBuffer(bytearray(32), 16, 16, framebuf.MONO_HLSB)
scissormap.fill(0)
scissormap.fill_rect(1,12,4,4,1)
scissormap.fill_rect(12,12,4,4,1)
scissormap.line(1,14,14,1,1)
scissormap.line(1,1,14,14,1)
# Array of choice icons
choice_maps = [ rockmap, papermap, scissormap ]
# User's choice
usermap = nomap
# Kookaberry's choice
kookamap = nomap
# Initialise timers for text blinking and game state waits
blink_t = 250    # Half periodforblinking pulse
blink_dur_t = 2500    # Duration of blinking text
kchoice_t = 1000    # Time delay to Kooka making a choice
_t_dur = time.ticks_ms() + blink_dur_t
_t_blink = time.ticks_ms() + blink_t
_t_kchoice = 0
blink = True
ublink = False
kblink = False
# Game state machine
# 1 New game 2 User Choice 3 Kooka Choice 4 Display Results 5 Game End
game_state = 1

while not kooka.button_a.was_pressed():	#Keep going until the A key is pressed

# Run the blink timer
    if time.ticks_diff( time.ticks_ms(), _t_blink) >= 0:
        _t_blink = time.ticks_ms() + blink_t
        blink = not blink
        
# Set up the fixed text on the screen
    disp.fill(0)	#Clear the display
    disp.setfont(fonts.mono6x7)	#Select small font
    disp.text('Rock Paper Scissors', 0, 6)
    disp.text('You',0,15)
    disp.text('Kooka', 92, 15)
    if time.ticks_diff( time.ticks_ms(), _t_dur) <=0 and game_state == 1: disp.text('New Game', 30, 15, blink)
    elif game_state == 6: disp.text('%s' % wins, 30, 15, blink)
    disp.text('exit', 0, 57)	#A Key = Exit
    disp.text('R', 48, 57)	#C Key = Rock
    disp.text('P', 80, 57)	#D Key = Paper
    disp.text('S', 112, 57)	#B Key = Scissors
# Display scores
    disp.setfont(fonts.sans12)
    disp.fill_rect(0, 20, 18, 24, 1)
    disp.text('%u' % uscore, 2, 38, ublink and blink)
    disp.fill_rect(110, 20, 128, 24, 1)
    disp.text('%u' % kscore, 112, 38, kblink and blink)
# Display last choices and result indicator
    disp.text('%s' % winner, 56, 38, 1)
    disp.blit(usermap, 22, 24)
    disp.blit(kookamap, 90, 24)
# Show the screen
    disp.show()
# If maximum score reached then stop checking user buttons and reset the game after a delay
    if game_state == 5: # Game round is finished
        _t_dur = time.ticks_ms() + blink_dur_t
        game_state = 6    # Hold state
        led_state = 1    # Initiate led flashing cycle
    if game_state == 6:
        if time.ticks_diff( time.ticks_ms(), _t_dur) >= 0: # Initialise the game
            kscore = 0
            uscore = 0
            kchoice = -1
            uchoice = -1
            winner = ""
            kooka.button_b.was_pressed()    # Clear any button presses
            kooka.button_c.was_pressed()
            kooka.button_d.was_pressed()
            usermap = nomap
            kookamap = nomap
            led_state = 0
            kooka.led_green.off()
            kooka.led_orange.off()
            kooka.led_red.off()
            _t_dur = time.ticks_ms() + blink_dur_t
            game_state = 1    # Start the new game
        else: # End of game timer is still running
            kooka.led_green.off()
            kooka.led_orange.off()
            kooka.led_red.off()
            if led_state == 1: kooka.led_green.on()
            if led_state == 2: kooka.led_orange.on()
            if led_state == 3: kooka.led_red.on()
            time.sleep_ms(100)
            led_state += 1
            if led_state >= 4: led_state = 1
                
# Check for user choice
    if game_state == 1:
        if kooka.button_b.was_pressed():	# User chose Scissors
            uchoice = 2
            winner = "?"
            game_state = 2
        if kooka.button_c.was_pressed():	# User chose Rock
            uchoice = 0
            winner = "?"
            game_state = 2
        if kooka.button_d.was_pressed():	# User chose Paper
            uchoice = 1
            winner = "?"
            game_state = 2
        
    if game_state == 2:    # User made a choice - update the symbol and initiateadelay
        usermap = choice_maps[uchoice]
        kookamap = nomap
        _t_kchoice = time.ticks_ms() + kchoice_t    # Initiate a delay
        game_state = 3
        
    if game_state == 3 and time.ticks_diff( time.ticks_ms(), _t_kchoice) >= 0: # Wait for timer then the Kooka chooses
        
        kchoice = random.randint(0,2)    # Kooka makes a random choice
        kookamap = choice_maps[kchoice]    # Map the choice icon
        winner = decider[uchoice][kchoice]    # Extract the winner
        if winner == uwins: 
            uscore += 1    # Adjust the scores
            ublink = True    # Make the score blink
        if winner == kwins: 
            kscore += 1
            kblink = True
        _t_dur = time.ticks_ms() + blink_dur_t
        kooka.button_b.was_pressed()    # Clear any button presses
        kooka.button_c.was_pressed()
        kooka.button_d.was_pressed()
        game_state = 4
        
    if game_state == 4 and time.ticks_diff( time.ticks_ms(), _t_dur) >= 0: # Wait for timer then the Kooka chooses
        ublink = False    # Reset the score blinking
        kblink = False
        game_state = 1
     # Check whether to stop the game
        if kscore >= maxscore:
            wins = 'K wins!'
            game_state = 5
        if uscore >= maxscore: 
            wins ='You win!'
            game_state = 5
# Small delay before polling again
    time.sleep_ms(50)