# FILENAME: PCA9685.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 30 June 2026
# DATE-MODIFIED: 9 July 2026 - added extra servo channels, motor driver, and stepper motor code
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE:
'''
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
#
# DESCRIPTION:
# Controls the Quokka Motor-Servo Driver Module based on the PCA9685 PWM controller chip.
# Contains classes and methods for:
#  Servos (angle and continuous speed) on channels 1-8. Methods Servo.angle= (degrees), Servo.speed= -1 to +1
#  Motors (1 to 4). Method is Motor.speed= -100 to +100
#  Steppers (1 to 2). Methods are:
#                         Stepper.step(n, rpm) where n is the number of steps (+ or -), rpm is stepper speed.
#                         Stepper.angle(a, rpm) where a is the rotation angle (+ or -), rpm is the stepper speed
#
# The script is derived from the Core Electronics PiicoDev Servo Driver code, extended to 8 servo channels.
# Code for the Motor and Steeper Motor driver is modelled on the code supporting the Kitronic Robotics board.
# Original Repositories:
# https://github.com/CoreElectronics/CE-PiicoDev-Servo-Driver-MicroPython-Module/blob/main/PiicoDev_Servo.py
# https://raw.githubusercontent.com/KitronikLtd/Kitronik-Pico-Robotics-Board-MicroPython/refs/heads/main/PicoRobotics.py
#
# 2026 JUN 30 - Modified for use by Kookaberry (only) by T.Strasser at AustSTEM
# Usage: https://github.com/CoreElectronics/CE-PiicoDev-Servo-Driver-MicroPython-Module/tree/main/examples
# Differences: No dependency on the PiicoDev Unified Library - uses Kookaberry MicroPython firmware
#
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: Quokka Motor-Servo Driver module connected to any I2C capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

try: from ustruct import pack, unpack
except: from struct import pack, unpack
from time import sleep_ms
from math import copysign

def remap(old_val, old_min, old_max, new_min, new_max):
    """Remap one range of values to another range and saturate for out-of-bounds"""
    x = (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min
    return min(new_max,max(x,new_min))

_I2C_ADDRESS = 0x40

class PCA9685:
    """
    A Class to drive the PCA9685 PWM driver
    """
    def __init__(self, i2c, address=_I2C_ADDRESS, freq=50):
        self.i2c = i2c
        self.address = address
        self.reset()
        self.frequency = freq # Hz

    def _write(self, address, value):
        self.i2c.writeto_mem(self.address, address, bytearray([value]))

    def _read(self, address):
        return self.i2c.readfrom_mem(self.address, address, 1)[0]

    def reset(self):
        self._write(0x00, 0x00)
    
    @property
    def frequency(self):
        return self._frequency        
    @frequency.setter
    def frequency(self,f):
        """Set the pulse frequency"""
        prescale = int(25000000.0 / 4096.0 / f + 0.5)
        old_mode = self._read(0x00) # Mode 1
        self._write(0x00, (old_mode & 0x7F) | 0x10) # Disable oscillator
        self._write(0xfe, prescale) # Apply prescale
        self._write(0x00, old_mode) # Start oscillator
        sleep_ms(1)
        self._write(0x00, old_mode | 0xa1) # Mode 1, autoincrement on
        self._frequency = 1/((prescale-0.5)*4096/25e6)
        
    def pwm(self, index, on=None, off=None):
        if on is None or off is None:
            data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
            return unpack('<HH', data)
        data = pack('<HH', on, off)
        self.i2c.writeto_mem(self.address, 0x06 + 4 * index,  data)

    def duty(self, index, value=None, invert=False):
        if value is None: # get the duty cycle
            pwm = self.pwm(index)
            if pwm == (0, 4096):
                value = 0
            elif pwm == (4096, 0):
                value = 4095
            value = pwm[1]
            if invert:
                value = 4095 - value
            return value
        if not 0 <= value <= 4095:
            raise ValueError("Out of range")
        if invert:
            value = 4095 - value
        if value == 0:
            self.pwm(index, 0, 4095)
        elif value == 4095:
            self.pwm(index, 4095, 0)
        else:
            self.pwm(index, 0, value)
            
class Servo:
    """
    A Servo class with methods for angle and continuous speed servos using the PCA9685 PWM driver
    """

    def __init__(self, controller, channel, min_us=600, max_us=2400, degrees=180, midpoint_us=None, range_us=None):
        self.freq = controller.frequency
        self.period = 1_000_000/self.freq # microseconds
        if midpoint_us is not None and range_us is not None: # option to define the servo timing with a midpoint and a range
            min_us = midpoint_us - range_us/2
            max_us = midpoint_us + range_us/2
        self.min_duty = self._us2duty(min_us) 
        self.max_duty = self._us2duty(max_us)
        self._degrees = degrees
        self.controller = controller
        if channel < 1 or channel > 8:
            raise Exception("Invalid Servo Channel %d" % channel)
#        self.channel = {4:0,3:1,2:2,1:3}[channel] # original PiicoDev channel mapping
        self.channel = int(channel)-1 # map to PCA9685 channels 0-7 inclusive
        
    def _us2duty(self, value):
        return int(4095 * value / self.period + 0.5)
    
    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, x):
        duty = self.min_duty + (self.max_duty - self.min_duty) * x / self._degrees
        duty = min(self.max_duty, max(self.min_duty, int(duty)))
        self.controller.duty(self.channel, duty)
        self._angle = min(self._degrees,max(x,0)) # saturate the property
        
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self,x):
        self._speed = x
        duty = int(remap(x, -1, 1, self.min_duty, self.max_duty)+0.5)
        self.controller.duty(self.channel, duty,)

    def release(self):
        self.controller.duty(self.channel, 0)

class Motor:
    """
    A Motor class with methods for speed over a range -100 to +100 using the PCA9685 PWM driver
    Each motor uses two PWM channels, one for forward speed, the second for reverse speed
    """

    def __init__(self, controller, motor):
        # Check motor number is in range
        if motor < 1 or motor > 4:
            raise Exception("Invalid Motor No %d" % motor)
        # Map motor forward and reverse PWM channels to PCA9685 channels
        # Motor 1 (fwd=8, rev=9) etc
        self.channel_fwd = 8 + (motor-1) * 2
        self.channel_rev = 9 + (motor-1) * 2
        self.freq = controller.frequency
        self.controller = controller

    # Motor speed control - valid range is -100 to +100
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self,x):
        self._speed = x
        duty = int(remap(abs(x), 0, 100, 0, 4095)) # Map the speed to the duty cycle (0-100 -> 0->4095)
        if x > 0:
            self.controller.duty(self.channel_rev, 0)
            self.controller.duty(self.channel_fwd, duty,invert=True)
        elif x < 0:
            self.controller.duty(self.channel_fwd, 0)
            self.controller.duty(self.channel_rev, duty,invert=True)
        else: # x = 0
            self.release()

    # Stop the PWM to both channels = zero speed
    def release(self):
        self.controller.duty(self.channel_fwd, 0)
        self.controller.duty(self.channel_rev, 0)

def calculate_pulse(rpm,steps_per_rev,freq):
    pulse_length = int(60000 / rpm / steps_per_rev + 0.5) # pulse length in milliseconds
    if pulse_length < int(1000 / freq + 0.5): # Pulse cannot be less than PWM period
        raise Exception("Stepper Motor RPM too high %d" % rpm)
    return pulse_length


class Stepper:
    """
    A Stepper motor class with methods for steps and angle translation using the PCA9685 PWM driver
    Each motor uses four PWM channels
    """

    def __init__(self, controller, stepper, steps_per_rev=512, rpm=6):
        # Check motor number is in range
        if stepper < 1 or stepper > 2:
            raise Exception("Invalid Stepper Motor No %d" % stepper)
        # Map motor forward and reverse PWM channels to PCA9685 channels
        # Motor 1 (fwd=8, rev=9) etc
        self.coil_1_fwd = 8 + (stepper-1) * 4
        self.coil_1_rev = 9 + (stepper-1) * 4
        self.coil_2_fwd = 10 + (stepper-1) * 4
        self.coil_2_rev = 11 + (stepper-1) * 4
        self.freq = controller.frequency
        self.controller = controller
        self.rpm = rpm
        self.steps_per_rev = steps_per_rev
        self.step_angle = 360 / self.steps_per_rev
        self.pulse_length = calculate_pulse(self.rpm, self.steps_per_rev, self.freq) # Stepper pulse length in milliseconds
        
    def step(self, steps, hold=False, rpm=None):  # Move the Stepper by n steps where n is a positive or negative integer
                                                # hold indicates if power is retained (True) or released (False)
        steps = int(steps)
        if steps > 0:
            channels = [self.coil_1_fwd,self.coil_2_fwd,self.coil_1_rev,self.coil_2_rev] # Order of coil energisation
        elif steps < 0:
            channels = [self.coil_2_rev,self.coil_1_rev,self.coil_2_fwd,self.coil_1_fwd]
        else:
            return
        
        # Update motor speed if specified
        if rpm is not None and rpm > 0:
            self.pulse_length = calculate_pulse(rpm, self.steps_per_rev, self.freq)
            self.rpm = rpm

        # print("Steps =",steps, " RPM =", self.rpm, " Delay =", self.pulse_length)
            
        for coil in range(0, abs(steps)): # Repeat for the number of steps
            self.controller.duty(channels[(coil+2)%4],0) # Switch complementary H-Brideg output off
            self.controller.duty(channels[coil%4],4095) # Switch first coil on
            # print(channels[(coil+2)%4],0, ":",channels[coil],4095)
            sleep_ms(self.pulse_length) # Delay to match desired RPM (see initialisation)
                
        if hold == False: # Release all coils
            for coil in channels:
                self.controller.duty(coil, 0)
                
    def angle(self, degrees, hold=False, rpm=None): # Move the specified angle and hold if hold=True
        steps = int(degrees / self.step_angle + copysign(0.5, degrees)) # Work out how many steps are needed
        self.step(steps, hold, rpm) # Move the stepper
        



# Test script
from machine import SoftI2C, Pin
import time

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PCA9685(i2c,address=0x40)
'''
servo = Servo(controller, 8,midpoint_us=1600, range_us=2600, degrees=180)
# Step the servos
servo.angle = 0
sleep_ms(1000)
servo.angle = 90
sleep_ms(1000)
servo.angle = 180
sleep_ms(1000)
servo.angle = 0
sleep_ms(1000)

# Sweep the servo slowly 0->180°
for x in range(0,90,5):
    servo.angle = x
    sleep_ms(40)
'''
'''
motor = Motor(controller,4)
for s in range(-100, 105, 5):
    motor.speed = s
    sleep_ms(1000)
motor.release()
'''
'''
stepper = Stepper(controller,2)
# Measure the time taken for one revolution
start = time.ticks_ms()
stepper.angle(360, rpm=6)
end = time.ticks_ms()
print("Elapsed:",time.ticks_diff(end,start)/1000)
'''