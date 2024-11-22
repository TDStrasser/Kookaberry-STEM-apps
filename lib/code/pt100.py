# File name: pt100.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 8 May 2021
# Date last modified: 4 December 2023 - update to adc.read_u16() function
# MicroPython Version: 1.12 for the Kookaberry V4-06
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
# Module to measure temperature using a PT100 resistance temperature detector (RTD) probe
# which is interfaced via a wheatstone bridge and analogue amplifier module
# The sensor is a DFRobot SEN0198 High Temperature Sensor
# The equation given by DFRobot to convert the module analogue voltage to sensor resistance is
# res =  (1800 * voltage + 220.9 * 18) / (2.209 * 18 - voltage) 
# The resistance is then converted to temperature by this equation inferred from curve fitting of RTD resistance vs temperature data:
# temp = 0.0012 * res^2 + 2.3024 * res - 242.89 in deg C
# On the Kookaberry the sensor plugs into P4 or P5. Results may be unpredictable if plugged in elsewhere
# Usage:
    #    import pt100
    #    rtd = pt100.PT100('P4')    # create the RTD object on P4
    #    resistance = rtd.resistance    # reads the RTD resistance
    #    temperature = rtd.temperature    # computes the RTD temperature
    #    theoretical_rtd_resistance = pt100.rtd_resistance(temperature)
    #    The last function is provided to compute the theoretical RTD resistance for a given temperature
    
# Begin code

# Initial conditions
import machine
# Constants - at present no means given to change these via arguments
k_vref = 3.3    # Reference voltage supplied by the Kookaberry
s_vref = 2.495    # Reference voltage for the wheatstone bridge
adc_res = 65536 # A to D converter resolution (65536 for 16 bit)

class PT100:
    def __init__(self, pin):
        self.pin = pin
        self.adc = machine.ADC(machine.Pin(pin))  # create the analogue input for the sensor
        
# Read and process the RTD sensor resistance
    @property
    def resistance(self):
        voltage = self.adc.read_u16() * k_vref / adc_res    # Read input voltage
        res = (1800 * (voltage + s_vref)) / (s_vref * 18 - voltage) #Convert rvoltage to thermocouple resistance
        return res
        
# Convert RTD reistance to temperature
    @property
    def temperature(self):
        res = self.resistance
        temp = 0.0012 * res * res + 2.3024 * res - 242.89 # Convert to temperature
        return temp
    
# Function to calculate standard PT100 resistance for a given temperature
def rtd_resistance(temp):
    A = 3.9083e-3
    B = -5.775e-7
    C = -4.183e-12
    R0 = 100
    
    rs = R0 * (1 + A * temp + B * temp * temp)
    if temp < 0:
        rs += C * temp * temp * temp * (temp - 100)
    return rs

'''
# Test code obtains and compares PT100 RTD to DS18B20 Temperatures and logs them
import time, kooka
disp = kooka.display
rtd = PT100('P4')
# Function to read a DS18B20 for reference
def ds18_read_temp(p):
    import onewire, ds18x20
    
    ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(p, machine.Pin.PULL_UP)))
    roms = ds.scan()
    if not roms: return -100
    ds.convert_temp()
    time.sleep(0.75)
    return ds.read_temp(roms[0])

f = open('PT100-Cal.csv','w+')
f.write('RTD_Temp,DS18_Temp\n')
f.close()
while True:
    rtd_temp = rtd.temperature
    ds18_temp = ds18_read_temp("P1")
    print("RTD:",rtd_temp, " DS18:",ds18_temp, " Err:",rtd_temp - ds18_temp)
    rtd_ohms = rtd_resistance(rtd_temp)
    ds18_ohms = rtd_resistance(ds18_temp)
    print(rtd.resistance,"actual ",rtd_ohms,"theor ohms RTD ", ds18_ohms,"ohms DS18, Err=",(rtd_ohms-ds18_ohms),"\n")
    f = open('PT100-Cal.csv','a+')
    f.write('%6.3f,%6.3f\n' % (rtd_temp,ds18_temp))
    f.close()
    disp.fill(0)
    disp.print('PT100')
    disp.print('')
    disp.print(' RTD:%6.3fC' % rtd_temp)
    disp.print('DS18:%6.3fC' % ds18_temp)
    disp.print('Diff:%6.3fC' % (rtd_temp - ds18_temp))
    time.sleep(10)
'''