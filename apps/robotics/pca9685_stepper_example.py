__name__ = 'PCA9685_Stepper'
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
# Example script for setting up and using a stepper motor
# with a PCA9685 motor driver board
# Documentation see: https://github.com/TDStrasser/Kookaberry-STEM-apps/blob/master/lib/pca9685_motors_servos_guide.md
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Quokka PCA9685 motor-servo board plugged into P3
# /lib files: pca9685.mpy
# /root files: Nil
# Other dependencies: Pico RP2040/RP2350 with Kookaberry firmware, stepper motor wired to motor 3 and 4 outputs
# Complementary apps: Nil
#------------------------------------------
# Begin code
from pca9685 import PCA9685, Stepper
from machine import SoftI2C, Pin
import time

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B')) # Set up an I2C bus on P3
controller = PCA9685(i2c,address=0x40,freq=50) # Initialise the PCA9685 chip

# Set up a stepper motor on the 3rd and 4th motor H-bridge driver channels which uses PCA9685 channels 13, 14, 15 and 16
stepper = Stepper(controller,2) # The default is a 512 steps/rev motor
# To change the steps/rev to 200 use: stepper = Stepper(controller,2,steps_per_rev=200)

# Rotate the stepper motor 360 degrees (one revolution)
# Measure the time taken for one revolution
start = time.ticks_ms() # Record the starting time
stepper.angle(360, rpm=6)  # Move the stepper by the given angle (+ or - allowed, no limit),
                            # at the specified RPM (limited by a minimum step period of 20msecs)
end = time.ticks_ms() # Record the ending time
print("Elapsed time:", time.ticks_diff(end,start)/1000, "seconds")