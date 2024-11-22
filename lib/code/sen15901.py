# FILENAME: sen15901.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 4 June 2022
# DATE-MODIFIED: 4 December 2023 - update to ADC.read_u16() function
# VERSION: 1.0
# SCRIPT: MicroPython Version: 1.12 for the Kookaberry V4-05
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
# Class and functions module for the Shenzen Fine Offset SEN15901 weather sensor comprising:
# an anemometer, a windvane, and a tipping bucket raingauge.
# Usage -
# Create the sensor object:
#  weather = sen15901.SEN15901(anem_pin,rgauge_pin,wvane_pin,vcc=3.3,pullup=4700)
# Gather the sensor readings:
#  windspeed = weather.windspeed # Wind speed in kilometres / hour
#  wind_azimuth = weather.azimuth # Wind direction in degrees from North or -1
#  wind_direction = weather.direction # String sub-cardinal eg. 'NNE' or 'None'
#  rainfall = weather.rainfall # Total rainfall in mm since startup
#  weather.reset_rainfall() # zeroes the rainfall accumulator
# Utility constants and functions:
#  weather.anem_calib # constant containing the windspeed per anemometer pulse per sec
#  weather.rgauge_calib # constant containing the rainfall per pulse of the rain gauge
# weather.vcc # the Vcc voltage applied to the windvane
# weather.pullup # the pullup resistor value in ohms for the windvane
# weather.wvane_calib()  # recalculates the windvane direction voltage array
#   use this whenever any windvane constant is changed
# weather.windvane_read() # reads the windvane voltage and returns an index to the direction array if successful, or -1 is the read fails
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: digital inputs for anemometer and rain gauge
#                            analogue input for the windvane
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: WeatherStation.py
#------------------------------------------
# TAGS: #weather #wind #rainfall
# BEGIN-CODE:

# Resistances of the windvane circuit starting at North (0 degrees)
wvane_ohms = [33000,6570,8200,891,1000,688,2200,1410,3900,3140,16000,14120,120000,42120,64900,21880]
wvane_hdg = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
anem_calib = 2.4 # one pulse/sec in kph
rgauge_calib = 0.2794 # one pulse in mm of rainfall
import machine, time

# The Fine Offset sensor array class
class SEN15901:
    
    def __init__(self, anem_pin, rgauge_pin, wvane_pin, vcc=3.3, pullup=10000):
        self.wvane_pin = wvane_pin
        self.vcc = vcc
        self.pullup = pullup
        self.rain = 0
        self.rain_timer = time.ticks_ms()
        self.wind = 0
        self.wvane_volts = [0] * len(wvane_ohms)
        self.wvane_calib()
        # Set up the anemometer digital input
        self.anem_pin = machine.Pin(anem_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.an_pulses = [time.ticks_ms(), 0, time.ticks_ms()]    # the last pulse time, the pulse counter,the time windspeed was last read - used to debounce and derive the average speed between reads
        self.anem_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=self.anem_pulsecount)
        self.anem_calib = anem_calib # speed in m/sec at one pulse/sec
        
        # Set up the tipping bucket rain gauge input
        self.rgauge_pin = machine.Pin(rgauge_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.rgauge_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.rgauge_accumulate)
        self.rgauge_calib = rgauge_calib

    # Handler for timing the anemometer pulses
    def anem_pulsecount(self, anem_pin):
        if time.ticks_diff(time.ticks_ms(), self.an_pulses[0]) > 10: # debounce
            self.an_pulses[1] += 1    # update the pulse counter
            self.an_pulses[0] = time.ticks_ms() # record the last update
        
    # Handler for the tipping bucket raingauge
    def rgauge_accumulate(self, rgauge_pin):
        # Rain gauge switch debouncing - only process the first interrupt
        if time.ticks_diff(time.ticks_ms(), self.rain_timer) > 1000: # debounce
            self.rain += self.rgauge_calib
            self.rain_timer = time.ticks_ms()
        
    # Resets the rainfall accumulator
    def reset_rainfall(self):
        self.rain = 0

    # Populates the windvane voltage array given Vcc and the pullup resistor
    def wvane_calib(self):
        for i in range(len(wvane_ohms)):
            self.wvane_volts[i] = self.vcc * wvane_ohms[i]/(wvane_ohms[i] + self.pullup)
        
    # Function reads the windvane sensor and returns the wind heading
    def windvane_read(self):
        try:
            voltage = machine.ADC(self.wvane_pin).read_u16() / 65535 * 3.3
        except:
            return -1
        # Find the closest heading
        error = self.vcc
        index = 0
        for i in range(len(self.wvane_volts)):
            cur_error = abs(voltage - self.wvane_volts[i])
            if  cur_error < error:
                error = cur_error
                index = i
        return index
                
    # Properties to retrieve the sensor data
    @property
    def rainfall(self):
        return self.rain
        
    @property
    def windspeed(self):
#        print(self.an_pulses[1], time.ticks_diff(time.ticks_ms(), self.an_pulses[0]))
        speed = 1000 * self.an_pulses[1] / time.ticks_diff(time.ticks_ms(), self.an_pulses[2]) * self.anem_calib # speed = pulses / period * calibration value
        self.an_pulses[2] = time.ticks_ms() # reset last read time
        self.an_pulses[1] = 0 # reset the pulse count
        return speed
        
    @property
    def direction(self):
        index = self.windvane_read()
        if index < 0: return 'None'
        else: return wvane_hdg[index]
        
    @property
    def azimuth(self):
        index = self.windvane_read()
        if index < 0: return index
        else: return index * 360 / 16

# Test code
'''
sensor = SEN15901('P1','P2','P4')
while True:
    print('Wind:',sensor.windspeed, sensor.direction, sensor.azimuth)
    print('Rain:',sensor.rainfall)
    time.sleep(2)
'''