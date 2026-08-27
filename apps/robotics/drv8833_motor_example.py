__name__ = 'DRV8833_Motor'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 27 August 2026
# Date last modified: 
# Version: 1.0
# MicroPython Version: 1.28 for the Kookaberry Pico RP2040/RP2350
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
# Example script for setting up and using a motor
# with a DRV8833 and 9110 H-Bridge motor driver board
# Documentation see: 
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Quokka DRV8833/9110 motor driver board plugged into P3
# /lib files: drv8833.mpy
# /root files: Nil
# Other dependencies: Pico RP2040/RP2350 with Kookaberry firmware
# Complementary apps: Nil
#------------------------------------------
# Begin code
from drv8833 import DRV8833
from machine import SoftI2C, Pin
from time import sleep_ms

motor = DRV8833('P3A','P3B') # Initialise motor

speeds = [0,-10,-20,-30,-40,-50,-60,-70,-80,-90,-99,-50,10,20,30,40,50,60,70,80,90,99,50,0] # Set up a list of speeds to run through

for s in speeds:
    motor.speed = s # Set the motor's speed
    # Print the speed and PWM duties on the REPL console
    print('Speed Command =',s, 'Read Back =',motor.speed )
    
    sleep_ms(1500) # let the motor run before looping to the next value
# Stop the motor and exit
print('Stopping')
motor.stop()