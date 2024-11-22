# FILENAME: Altimeter.py
__name__ = 'Altimeter'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 5 August 2021
# VERSION: 1.3
# DATE-MODIFIED: 30 March 2022 - added set altitude mode
# SCRIPT-TYPE: MicroPython Version: 1.12 for the Kookaberry V4-05
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# DESCRIPTION:
# Calculates altitude from barometric pressure using a BMP/E280  sensor
# Local reference sea-level barometric pressure (known as QNH) can be adjusted
#  using the C and D buttons. The default QNH is 1013hPa
# A set altitude mode (pilot mode) is provided - toggle modes with the B button
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
# The configuration of the I2C scl and sda pins is also tested and swapped if necessary
#------------------------------------------
# TAGS: #sensor #pressure #altitude #i2c
# DEPENDENCIES:
# I/O ports and peripherals: BME/BMP280 sensor plugged into P3
# /lib files: bme280.mpy is embedded in Kookaberry firmware
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------
# BEGIN-CODE:
# Initial conditions

import machine, kooka, fonts, time, math
from bme280 import BME280

kooka.radio.disable()    # turn off the radio to save battery
disp = kooka.display    # initialise the OLED display
disp.print(__name__)
disp.print('Initialising...')

i2c_swap = False
bme_adx = 0x77

# Mode indications
modes = ['QNH','ALT']
mode = 0

# Function to initialise the BME280 sensor
def sensor_init(i2c, adx):
    sensors = i2c.scan()    # scan the I2C bus for addresses
    for x in sensors:
        if x == adx: 
            dev = BME280(address = x, i2c=i2c, it=100, gain=1/8)
            return dev
        
i2c = machine.SoftI2C(scl='PA9',sda='PA10', freq=50000)
bme = sensor_init(i2c, bme_adx)
if not bme: # Couldn't find sensor, swap pins on I2c and try again
    i2c = machine.SoftI2C(scl='PA10',sda='PA9', freq=50000)
    bme = sensor_init(i2c, bme_adx)
    if bme: i2c_swap = True
temp = 0
press = 0
humid = 0
dspin = 'P3'

dsinterval = 2000
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples

while not kooka.button_a.was_pressed():
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        _timer_ds += dsinterval    # only take a sample every period
        t_read = False
        try:
            temp = bme.values[0]
            press = bme.values[1]
            humid = bme.values[2]
            t_read = True
        except:    # Couldn't take a reading from the sensor
            temp = 0
            press = 0
            humid = 0
            i2c = machine.SoftI2C(scl='PA9',sda='PA10', freq=50000)
            bme = sensor_init(i2c, 0x10)
            if bme: i2c_swap = True
            if not bme: # Couldn't find sensor, swap pins on I2c and try again
                i2c = machine.SoftI2C(scl='PA10',sda='PA9', freq=50000)
                bme = sensor_init(i2c, 0x10)
# Adjust QNH barometric pressure as necessary
    if mode: # If in set altitude mode
        altitude = round(bme.altitude, 0)
        if kooka.button_c.was_pressed(): 
            while bme.altitude > altitude - 1: # adjust QNH until altitude set
                bme.sealevel -= 0.1
        if kooka.button_d.was_pressed(): 
            while bme.altitude < altitude + 1:
                bme.sealevel += 0.1

    else:    # If in QNH adjustment mode
        if kooka.button_c.was_pressed(): # Adjust QNH directly
            bme.sealevel -= 0.2
        if kooka.button_d.was_pressed(): 
            bme.sealevel += 0.2
# Set mode (QNH or ALT)
    if kooka.button_b.was_pressed(): 
        mode = not mode
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-x -C|%s|D+  B-%s' % (modes[mode], modes[not mode]), 0, 63)
    disp.setfont(fonts.mono6x7)
    if t_read: 
        disp.text('Alt: %6.0f m' % bme.altitude, 12, 25)
        disp.text('BaP: %6.1f hPa' % press, 12, 34)
        disp.text('QNH: %6.1f hPa' % bme.sealevel, 12, 43)
        disp.setfont(fonts.mono5x5)
        if mode:
            disp.text('Adjust present altitude', 10, 50)
        else:
            disp.text('Obtain QNH from bom.gov.au', 10, 50)
    else: disp.text('Plug sensor into %s' % dspin, 0, 20)
    disp.show()

# Clean up and exit


