__name__ = 'PCA9685_C_Servo'
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
# Example script for setting up and using a continuous servo (such as the SG90R or FS90R)
# with a PCA9685 servo driver board
# Documentation see: https://github.com/TDStrasser/Kookaberry-STEM-apps/blob/master/lib/pca9685_motors_servos_guide.md
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: PCA9685 servo board plugged into P3
# /lib files: pca9685.mpy
# /root files: Nil
# Other dependencies: Pico RP2040/RP2350 with Kookaberry firmware
# Complementary apps: Nil
#------------------------------------------
# Begin code
from pca9685 import PCA9685, Servo
from machine import SoftI2C, Pin
from time import sleep_ms

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B')) # Set up an I2C bus on P3
controller = PCA9685(i2c,address=0x40,freq=50) # Initialise the PCA9685 chip
# Set up a servo (with all options specified) - adjust range_us to suit the servo speed pulse-width range
servo = Servo(controller,1,midpoint_us=1500, range_us=600, freq_compensation=12, clockwise=True, mid_zero=True)
# Simple setup with default values - servo = Servo(controller,1) with default pulse width range of 1msec to 2msecs

# Utility function to ramp between two speeds with a given step size and delay
def ramp(motor,s1,s2,step,delay):
    increments = int(abs((s2-s1)/step) + 0.5)
    s = s1
    for i in range(increments):
        motor.speed = s # Sets the servo speed
        s += step
        print('Speed = %0.2f' % s)
        sleep_ms(delay)

# Exercise the motor over its range
speed_max = 99
speed_step = 10
step_delay = 1000
ramp(servo,0,speed_max,speed_step,step_delay)
ramp(servo,speed_max,-speed_max,-speed_step,step_delay)
ramp(servo,-speed_max,0,speed_step,step_delay)

servo.stop()