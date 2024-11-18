# File name: kbtimer.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 9 Aug 2018
# Date last modified: 9 Aug 2019
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
# Module to measure the length of a button press and return a flag if preset time is expired
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Code snippet can be used in any app
#------------------------------------------
# Usage:
    #    import kbtimer
    #    b_timer = kbtimer.KBTimer(kooka.button_a, 1000) # instantiate a buttom timer object
    #    if b_timer.isexpired(): do something  # test for button expiry
    #    time_pressed = b_timer.button_time  # record of button millisecond if pressed else zero
    #    time_since_pressed = b_timer.timer()  # returns the time since pressed or ero if not pressed
    #    time_to_expiry = b_timer.toexpiry() # returns time to expiry in milliseconds or zero if not pressed
    #    b_timer.reset()  # housekeeping to reset the expired flag if used multiple times - ie. must be reset every time

# Begin code
import time

class KBTimer:

    def __init__(self, k_btn, exp_time):
# initialises the object data
        self.button = k_btn    # button being monitored
        self.exit_time = exp_time # required press duration time to exit in milliseconds
        self.button_time  = 0  # initialise the button pressed time - zero is no press
        self.expired = False # initialise the expiry flag

# test for button delay having expired
    def isexpired(self):
        if self.button.is_pressed():   # detect a current button press
            if not self.button_time: self.button_time = time.ticks_ms()  # if not previously pressed, record when the button initially pressed
            elif time.ticks_ms() - self.button_time >= self.exit_time: self.expired = True # if a time recorded test for button time elapsed to set exit flag
        else:  # if the button not pressed, or was released
            self.button_time = 0  # reset the button pressed time
        return self.expired

# measure time since pressed
    def timer(self):
        self.timerval = 0
        if self.button_time: self.timerval = time.ticks_ms() - self.button_time
        return self.timerval

# measure time to expiry
    def toexpiry(self):
        return self.exit_time - self.timer()

# resets the timer system if multiple expiries
    def reset(self):
        self.expired = False  # reset the expiry flag
        self.button_time  = 0  # initialise the button pressed time - zero is no press

