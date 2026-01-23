# FILENAME: PiicoDev_RGB_Kookaberry.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 23 Januarz 2026
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE:
'''
Copyright 2020 Core Electronics Pty Ltd and 2025 The AustSTEM Foundation

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
# Library module to use the PiicoDev RGB LED module
# Based on the PiicoDev libraries from Core Electronics 
#
# Usage: https://github.com/CoreElectronics/CE-PiicoDev-RGB-LED-MicroPython-Module/blob/main/README.md
# Differences: No dependency on the PiicoDev Unified Library - uses Kookaberry MicroPython firmware
'''
# Example script setting the RGB LEDs to successive hues around the colour wheel
from machine import Pin, SoftI2C
from time import sleep_ms
from PiicoDev_RGB_Kookaberry import PiicoDev_RGB, wheel

# First set up the I2C bus
i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))

# Then instantiate the PiicoDev RGB module using the I2C bus
leds = PiicoDev_RGB(bus=i2c)

while True:
    for x in range(0,360,10): # glow on
        hue = x / 360
        for y in range(10):
            brightness = y/10
            rgb = wheel(h=hue,v=brightness)
            leds.fill( rgb ) # fill() will automatically show()
            sleep_ms(100)

'''
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: PiicoDev RGB module connected to any I2C capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:
from time import sleep_ms
_baseAddr=0x08
_DevID=0x84
_regDevID=0x00
_regFirmVer=0x01
_regCtrl=0x03
_regClear=0x04
_regI2cAddr=0x05
_regBright=0x06
_regLedVals=0x07

# This function is doing an HSV→RGB conversion (with hue normalized to 0–1, not degrees) and returning 8‑bit RGB values (0–255) for a given hue h,
# saturation s, and value/brightness v.
# Inputs:
# h: hue in the range 0–1 (not degrees; to use degrees, you must convert h = degrees/360.0).
# s: saturation (0–1).
# v: value/brightness (0–1).
# Output:
# A tuple/list [R, G, B] (or (v, v, v) in the special case), each in 0–255.
# So it maps a point in HSV color space to an RGB color suitable for typical 8‑bit displays.

def wheel(h, s=1, v=1):
    # Handle special case of desaturation (no colour)
    # If saturation is zero, the color is on the gray axis (no hue), so R=G=B.
    # It scales v from 0–1 to 0–255 and returns that same value for all channels.
    if s == 0.0: v*=255; return (v, v, v)
    
    # The hue circle 0–1 is divided into 6 segments (red→yellow, yellow→green, etc.).
    # i (0–5) selects which of the 6 hue sectors the color lies in.
    # f (0–1) is the fractional position inside that sector, used for interpolation between the two end colors of the sector.
    # After later i %= 6, i is forced into 0–5 even if h slightly exceeds 1 due to rounding/float error.
    i = int(h*6.) # assume int() truncates
    f = (h*6.)-i;
    
    # Precompute intermediate values p, q, t
    # These are standard intermediates in HSV-to-RGB formulas:
    # p is the value of the “low” channel when saturation is applied.
    # q and t are the two intermediate values as you move across the hue sector; one channel ramps down from v to p, the other ramps up from p to v.
    # Each is then scaled by 255 and truncated to an int. v itself is also scaled to 0–255.
    # So at this point:
    # v, p, q, and t are all integers 0–255.
    p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    v = int(v+0.5)
    
    # Choose RGB ordering by hue sector. The last part switches on i to assign v, p, q, t to the appropriate channels:
    # This is the usual HSV→RGB mapping:
    # Sector 0 (red→yellow): R = v, G = t, B = p
    # Sector 1 (yellow→green): R = q, G = v, B = p
    # Sector 2 (green→cyan): R = p, G = v, B = t
    # Sector 3 (cyan→blue): R = p, G = q, B = v
    # Sector 4 (blue→magenta): R = t, G = p, B = v
    # Sector 5 (magenta→red): R = v, G = p, B = q
    # So as h increases from 0 to 1, the function walks around the color wheel once.
    if i == 0: return [v, t, p]
    if i == 1: return [q, v, p]
    if i == 2: return [p, v, t]
    if i == 3: return [p, q, v]
    if i == 4: return [t, p, v]
    if i == 5: return [v, p, q]

class PiicoDev_RGB(object):
    def setPixel(self,n,c):
        self.led[n]=[round(c[0]),round(c[1]),round(c[2])]

    def show(self):
        buffer = bytes(self.led[0]) + bytes(self.led[1]) + bytes(self.led[2])
        self.i2c.writeto_mem(self.addr, _regLedVals, buffer)

    def setBrightness(self,x):
        self.bright= round(x) if 0 <= x <= 255 else 255
        self.i2c.writeto_mem(self.addr, _regBright, bytes([self.bright]))
        sleep_ms(1)

    def clear(self):
        self.i2c.writeto_mem(self.addr,_regClear,b'\x01')
        self.led=[[0,0,0],[0,0,0],[0,0,0]]
        sleep_ms(1)

    def setI2Caddr(self, newAddr):
        x=int(newAddr)
        assert 8 <= x <= 0x77, 'address must be >=0x08 and <=0x77'
        self.i2c.writeto_mem(self.addr, _regI2cAddr, bytes([x]))
        self.addr = x
        sleep_ms(5)

    def readFirmware(self):
        v=self.i2c.readfrom_mem(self.addr, _regFirmVer, 2)
        return (v[1],v[0])

    def readID(self):
        return self.i2c.readfrom_mem(self.addr, _regDevID, 1)[0]

    # Control the 'Power' LED. Defaults ON if anything else but False is passed in
    def pwrLED(self, state):
        assert state == True or state == False, 'argument must be True/1 or False/0'
        self.i2c.writeto_mem(self.addr,_regCtrl,bytes([state]))
        sleep_ms(1)
        
    def fill(self,c):
        for i in range(len(self.led)):
            self.led[i]=c
        self.show()
        
    def __init__(self, bus=None, addr=_baseAddr, id=None, bright=50):
        self.i2c = bus
        if type(id) is list: # preference using the ID argument
            assert max(id) <= 1 and min(id) >= 0 and len(id) is 4, "id must be a list of 1/0, length=4"
            self.addr=_baseAddr+id[0]+2*id[1]+4*id[2]+8*id[3]
        else:
            self.addr = addr # accept an integer
        self.led = [[0,0,0],[0,0,0],[0,0,0]]
        self.bright=bright
        try:
            self.setBrightness(bright)
            self.show()
        except Exception as e:
            print("* Couldn't find a device - check switches and wiring")
            raise e
        