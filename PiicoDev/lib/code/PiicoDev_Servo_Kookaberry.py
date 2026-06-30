# FILENAME: PiicoDev_Servo_Kookaberry.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 30 June 2026
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE:
'''
Copyright 2020 Core Electronics Pty Ltd and 2026 The AustSTEM Foundation

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
# Controls the PiicoDev Servo Drive based on the PCA9685 PWM ED controller chip.
# Original Repository:
# https://github.com/CoreElectronics/CE-PiicoDev-Servo-Driver-MicroPython-Module/blob/main/PiicoDev_Servo.py
#
# 2026 JUN 30 - Modified for use by Kookaberry (only) by T.Strasser at AustSTEM
# Usage: https://github.com/CoreElectronics/CE-PiicoDev-Servo-Driver-MicroPython-Module/tree/main/examples
# Differences: No dependency on the PiicoDev Unified Library - uses Kookaberry MicroPython firmware
#
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: PiicoDev Servo Driver module connected to any I2C capable GPIOs
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

def remap(old_val, old_min, old_max, new_min, new_max):
    """Remap one range of values to another range and saturate for out-of-bounds"""
    x = (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min
    return min(new_max,max(x,new_min))

class PCA9685:
    """
    A Class to drive the PCA9685 PWM driver
    """
    def __init__(self, i2c, address=0x44):
        self.i2c = i2c
        self.address = address
        self.reset()
        self.frequency=50 # Hz

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
            
_I2C_ADDRESS = 0x44
class PiicoDev_Servo_Driver(PCA9685):
    """
    A child class that wraps PCA9685 with PiicoDev initialisation logic
    """    
    def __init__(self, bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, asw=None):
        if type(asw) is list and len(asw) is 2 and all(element in [0,1] for element in asw):
            addr = _I2C_ADDRESS + asw[0] + 2*asw[1]
        else:   
            addr = address # default address used if asw not provided OR invalid
#        i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        PCA9685.__init__(self, bus, address=addr)

class PiicoDev_Servo:
    def __init__(self, controller, channel, freq=50, min_us=600, max_us=2400, degrees=180, midpoint_us=None, range_us=None):
        self.period = 1_000_000/freq # microseconds
        if midpoint_us is not None and range_us is not None: # option to define the servo timing with a midpoint and a range
            min_us = midpoint_us - range_us/2
            max_us = midpoint_us + range_us/2
        self.min_duty = self._us2duty(min_us) 
        self.max_duty = self._us2duty(max_us)
        self._degrees = degrees
        self.freq = freq
        self.controller = controller
        self.channel = {4:0,3:1,2:2,1:3}[channel] # map {silk label:PCA9685 channel}
        
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
        self.controller.duty(self.channel, duty)

    def release(self):
        self.controller.duty(self.channel, 0)
'''''
# Test script
from machine import SoftI2C, Pin
from time import sleep_ms

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)
servo_1 = PiicoDev_Servo(controller, 1)
servo_4 = PiicoDev_Servo(controller, 4)
# Step the servos
servo_1.angle = 0
servo_4.angle = 0
sleep_ms(1000)
servo_1.angle = 90
servo_4.angle = 90
sleep_ms(1000)
servo_1.angle = 180
servo_4.angle = 180
sleep_ms(1000)
servo_4.angle = 0
servo_1.angle = 0
sleep_ms(1000)

# Sweep the servo slowly 0->180°
for x in range(0,180,5):
    servo_1.angle = x
    servo_4.angle = x
    sleep_ms(40)
    '''
