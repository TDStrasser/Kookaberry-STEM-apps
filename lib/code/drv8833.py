# FILENAME: drv8833.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 26 August 2026
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# DESCRIPTION:
# Helper class to set up a motor controller using the DRV8833 H-Bridge motor driver chip.
# This module will also work with L9110 H-Bridge chip which supports power supply voltages up to 12 volts.
# Contains classes and methods for driving a single motor given the Kookaberry GPIO pins and PWM frequency.
# The Kookaberry generates the PWM signal directly using the method in its firmware.
# Use two instances of the DRV8833 class to drive each half of the DRV8833 chip.
# Usage:
#  from drv8833 import DRV8833
#  motor1 = DRV8833(gpio1,gpio2,freq=50) # Initialises a DRV8833 H-Bridge configuration
#  motor1 = DRV8833(gpio3,gpio4,freq=50) # Initialises a second DRV8833 H-Bridge configuration
#  Methods:
#     DRV8833.speed = n (-99 to +99) sets the motor speed 
#     speed = DRV8833.speed fetches the motor speed 
#     DRV8833.frequency = f (10 to 10000 default 50) sets the PWM frequency 
#     f = RV8833.frequency fetches the motor PWM frequency 
#     DRV8833.stop() stops the motor
#
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: Quokka Motor Driver DRV8833 / L9110 module connected to any two PWM-capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

from time import sleep_ms
from math import copysign
from machine import Pin, PWM

freq_min = 10 # Minimum permitted PWM frequency
freq_max = 10000 # Maximum permitted PWM frequency
speed_max = 99 # Maximum permitted speed

# A class to set up the DRV8833 motor driver chip using PWM inputs

class DRV8833:
    
    def __init__(self, in1=None, in2=None, freq=50):
        # Initialises two given GPIOs in PWM mode at the specified frequency with zero duty cycle
        self.freq = min(max(freq, freq_min), freq_max) # Limit check the PWM frequency
        self.pwm1 = PWM(Pin(in1),freq=self.freq, duty=0) # Initialise DRV8833 input 1
        self.pwm2 = PWM(Pin(in2),freq=self.freq, duty=0) # Initialise DRV8833 input 2
        self.spd = 0

    # Read and set the PWM frequency
    @property
    def frequency(self):
        self.freq = self.pwm1.freq()
        return self.freq     
    @frequency.setter
    def frequency(self,frequency):
        """Set the PWM frequency"""
        frequency = min(max(frequency, freq_min), freq_max) # Limit check the PWM frequency
        self.pwm1.freq(frequency) # Set the frequency to both DRV8833 H-Bridge inputs
        self.pwm2.freq(frequency)
        self.frequency() # Read back the frequency

    # Read and set the motor speed by manipulating the H-Bridge inputs xIN1 and xIN2
    '''
    Truth Table:PWM Control of Motor Speed
        xIN1  xIN2  FUNCTION
        PWM   0     Forward PWM, fast decay
        1     PWM   Forward PWM, slow decay
        0     PWM   Reverse PWM, fast decay
        PWM   1     Reverse PWM, slow decay
    '''
    @property
    def speed(self):
        speed_fwd = self.pwm1.duty()
        speed_rev = self.pwm2.duty()
        if speed_rev % 100 == 0: self.spd = speed_fwd    # xIN2 is steady 0 or steady 1 - forward speed
        elif speed_fwd % 100 == 0: self.spd = -speed_rev # xIN1 is steady 0 or steady 1 - reverse speed
        else: # invalid both xIN1 and xIN2 have 1-99 duty cycle - stop the motor
            print("PWM on both H-Bridge inputs - stopping motor",speed_fwd, speed_rev)
            self.pwm1.duty(0)
            self.pwm2.duty(0)
            self.spd = 0
        # print(speed_fwd,speed_rev)
        return self.spd
    @speed.setter
    def speed(self,speed):
        """Set the motor speed in the range -99 to +99 by setting the duty cycle of xIN1 (fwd) and xIN2 (rev)
           per the truth table above"""
        speed_target = min(max(speed, -speed_max), speed_max) # Limit check the PWM frequency
        speed = int(speed_target + copysign(0.5, speed_target)) # Convert back to integer in range -99 to +99
        # print(speed_target, speed)
        if (speed * self.spd) < 0: # Check for motor reversal
            # First stop the motor for a while to avoid large induced current which may damage the H-Bridge
            self.pwm1.duty(0)
            self.pwm2.duty(0)
            sleep_ms(50) # Give time for the motor to stop and current to decay
            # print('Reversal')
        if speed > 0:
            self.pwm2.duty(0) # Use fast decay PWM
            self.pwm1.duty(speed) # xIN1 duty cycle sets the forward speed
        else: # Motor speed is reverse
            self.pwm1.duty(0) # Use fast decay PWM
            self.pwm2.duty(-speed)
        return self.speed # Read back the speed and return it
    
    def stop(self): # Stop the motor
        self.pwm1.duty(0) # Apply to the H-Bridge inputs
        self.pwm2.duty(0)
        return self.speed # Read back and return the speed to confirm
    

''' Test script''' '''
motor = DRV8833('P3A','P3B') # Initialise motor
speeds = [0,-10,-20,-30,-40,-50,-60,-70,-80,-90,-99,-50,10,20,30,40,50,60,70,80,90,99,50,0] # Set up a list of speeds to run through
for s in speeds:
    motor.speed = s # Set the motor's speed
    # Print the speed and PWM duties on the REPL console
    print('Speed Command =',s, 'Read Back =',motor.speed )
    
    sleep_ms(1500) # let the motor run before looping to the next value
print('Stopping')
motor.stop()
'''