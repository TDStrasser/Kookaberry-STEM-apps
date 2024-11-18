# File name: 
__name__ = 'Ricochet'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 11 July 2021
# Date last modified: 14 July 2021 added penalty for moving paddle while paused, improved points display
# Version 1.4
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
# A single player paddle game.
# The aim is to keep the ball in play as it ricochets off the walls.
# Each time you hit the ball you score points.
# The game gets faster and the paddle narrower after each ten hits and the scores per hit increase too.
# If you can hit the ball with the bottom corner of the paddle you will get
# multiple hits and points.  It's actually a script bug which was kept deliberately.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------

# Begin code
import kooka, machine, fonts, time, random

# Initial conditions
ball = [0,0,0,0,4] * 5  # Ball [x,y,xvel,yvel,size] in pixels
court = [0,10,127,40,2]    # Court [x,y,width,height,border]
paddle = [0,0,0,5]    # Paddle [x,y,width,height] in pixels
level = 0
play = False
score = 0
score_delta = 1
score_count = 0
# Objects
disp = kooka.display

# Functions
def draw_court(dims):    # Draws the court area
    disp.fill_rect(dims[0],dims[1],dims[2],dims[3],1)
    disp.fill_rect(dims[0]+dims[4],dims[1]+dims[4],dims[2]-2*dims[4],dims[3]-dims[4],0)
    
def init_ball():    # Initialises the ball position randomly
    global ball, court, level    # makes ball and court data accessible within function
    ball[0] = random.randint(court[0]+court[4], court[0]+court[2]-court[4]-ball[4])
    ball[1] = court[1]+court[4] + ball[4]
    ball[2] = -1 
    if random.randint(0,1): ball[2] = 1
    ball[3] = -1
    if random.randint(0,1): ball[3] = 1
    
def init_paddle():    # Initialises the paddle and positions it randomly
    global paddle, court # makes ball and court data accessible within function
    paddle[0] = random.randint(court[0]+court[4], court[0]+court[2]-court[4]-paddle[2])
    paddle[1] = court[1] + court[3] - paddle[3]
    paddle[2] = max(10,(40-2*level))    # Initial paddle size
    
def draw_ball(data):    # Draws the ball in current position
    disp.fill_rect(data[0],data[1],data[4],data[4],1)

def draw_paddle(data):    # Draws the paddle in its current position
    disp.fill_rect(data[0],data[1],data[2],data[3],1)
    
def ball_wall():    # Detects collisions between the ball and court walls
    global ball, court    # makes ball and court data accessible within function
    # if a collision is detected the appropriate velocities (x or y) of the ball are updated
    # work out the boundaries
    boundary_l = court[0] + court[4]    # left boundary
    boundary_r = court[0] + court[2] - court[4]    # right boundary
    boundary_t = court[1] + court[4]    # top boundary
    # detect wall collisions and adjust velocities
    if ball[0] < boundary_l: ball[2] = -ball[2]
    if (ball[0]+ball[4]) > boundary_r: ball[2] = -ball[2]
    if ball[1] <= boundary_t: ball[3] = -ball[3]
    
def ball_paddle():    # Detects collisions between the ball and paddle
    global ball, paddle    # makes ball and paddle data accessible within function
    # if a collision is detected the appropriate velocities (x or y) of the ball are updated
    # work out the boundaries
    boundary_l = paddle[0]    # left boundary
    boundary_r = paddle[0] + paddle[2]    # right boundary
    boundary_b = paddle[1]    # bottom boundary
    # detect paddle collision and adjust velocities
    result = False
    if (ball[1]+ball[3]) >= boundary_b and (ball[1]+ball[3]) <= (boundary_b+paddle[3]): # only if the ball has descended to being within the paddle
        if ball[0] < boundary_r and (ball[0]+ball[4]) > boundary_l: 
            ball[3] = -ball[3]
            result = True
    return result
    
def update_ball():    # Updates the position of the ball and displays it
    global ball, score, score_delta    # Makes the ball data accessible in the function
    ball[0] += ball[2]    # Update x-position
    ball[1] += ball[3]    # Update y-position
    ball_wall()    # Process and court boundary collisions
    if ball_paddle(): update_score()
    
def move_paddle(dir):    # Moves the paddle left or right within bounds
    global paddle
    boundary_l = court[0] + court[4]    # left boundary
    boundary_r = court[0] + court[2] - court[4] - paddle[2]   # right boundary
    paddle[0] += dir    # Update the paddle x position  
    paddle[0] = max(boundary_l, min(boundary_r, paddle[0])) # Enforce limits
    if not play and ball_in(): update_score(-1)    # Penalise paddle moves while paused

def ball_in():    # Works out if the ball is still in the court
    global ball, court    # Makes the ball data accessible in the function
    boundary_b = 70    # bottom boundary
    return (ball[1] < boundary_b)
    
def update_score(mode=0):    # Updates the score and play parameters
    global level, score, score_delta, score_count, ball_timer, paddle
    if mode < 0:    # Penalty mode
        if score > 200: score -= int(score_delta/10 + 0.5)    # Less severe points loss
        if level > 10: score_count -= 1    # But levels get affected
    else: # Normal positive mode
        score += score_delta
        score_count += 1
    score = max(0,score)
    score_count = max(0,score_count)
    level = int(score_count/10)    # Increases difficulty every 10 scores
    score_delta = level+1
    ball_timer = max(20, int(ball_timer * 0.98 + 0.5))    # Makes ball 2% faster
    if score >= 10: paddle[2] = max(10,int(paddle[2]*0.96+0.5))    # Make paddle 5% narrower
#    print(score,score_delta,ball_timer,paddle[2])
    
# Timers
ball_timer = 80    # Interval between moving the ball
timer_ball = time.ticks_ms()    # Initialise the ball updating timer
init_ball()    # Initialise the ball
init_paddle()    # Initialise the paddle
# Game main loop begins here
while not kooka.button_a.was_pressed():
# Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono6x7)
    disp.text('%s' % __name__, 0, 6)
    disp.text('Pts:', 64, 6)
    if score >= 1000: disp.setfont(fonts.mono5x5)
    disp.text('%5.3G' % score, 90, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-ex  C<-=->D', 0, 60)
    if play: disp.text('B-hold', 88, 60)
    else: disp.text('B-play', 88, 60)
    draw_court(court)
    if kooka.button_c.is_pressed(): move_paddle(-1)
    if kooka.button_d.is_pressed(): move_paddle(1)
    draw_paddle(paddle)
    if kooka.button_b.was_pressed(): 
        play = not play
        if play and not ball_in(): # Restart the game
            init_ball()
            paddle[2] = max(10,(40-2*level))    # Set paddle size
            ball_timer = max(20,80-5*level)
        
    if not ball_in(): play = False    # Ends round
    
    if play and time.ticks_diff(time.ticks_ms(), timer_ball) >= 0:
        timer_ball = time.ticks_ms() + ball_timer
        update_ball()
    draw_ball(ball)
    disp.show()

# Clean up and exit