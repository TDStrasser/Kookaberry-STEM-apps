__name__ = 'PCA9685_Motor'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 11 July 2026
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
# Example script for setting up and using motor
# with a PCA9685 motor driver board
# Documentation see: https://github.com/TDStrasser/Kookaberry-STEM-apps/blob/master/lib/pca9685_motors_servos_guide.md
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Quokka PCA9685 motor-servo board plugged into P3
# /lib files: pca9685.mpy
# /root files: Nil
# Other dependencies: Pico RP2040/RP2350 with Kookaberry firmware
# Complementary apps: Nil
#------------------------------------------
# Begin code
from pca9685 import PCA9685, Motor
from machine import SoftI2C, Pin
from time import sleep_ms

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B')) # Set up an I2C bus on P3
controller = PCA9685(i2c,address=0x40,freq=50) # Initialise the PCA9685 chip

# Set up a motor on the 4th motor H-bridge driver chip which uses PCA9685 channels 15 and 16
motor = Motor(controller,4)

# Run the motor through its range
speeds = [0,-25,-50,-75,-100,-50,0,25,50,75,100,50,0] # Set up a list of speeds to run through
for s in speeds:
    motor.speed = s # Set the motor's speed
    # Advanced topic -
    # Work out the H-Bridge arm duty cycles by delving into the PCA9685 channel modulation data
    pwm_plus_duty = (4095-controller.duty(14))/40.95 # PCA9685 channel 14 duty is 4095->0 (0->100%)
    pwm_minus_duty = (4095-controller.duty(15))/40.95 # PCA9685 channel 15 duty is 4095->0 (0->100%)
    
    # Print the speed and PWM duties on the REPL console
    print('Speed =',motor.speed,'PWM Duty (+,-) = %d%%,%d%%' % (pwm_plus_duty, pwm_minus_duty) )
    
    sleep_ms(2000) # let the motor run before looping to the next value

# Finish up by stopping the motor and removing power
motor.release()
