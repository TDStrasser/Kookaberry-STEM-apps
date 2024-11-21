# FILENAME: _Config.py
__name__ = '_Config'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 21 June 2020
# DATE-MODIFIED: 5 November 2022 - alternate upython sys.implementation.mpy (_mpy) attributes)
# VERSION: 3.0
# SCRIPT-TYPE: 1.18 for the Kookaberry V4-05
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
# DESCRIPTION:
# Sets / edits and stores the configuration parameters for the Kookaberry apps.
# Replaces the former Kookapp.cfg configuration file regime 
# Splash screen shows the operating system version information 
# Default radio channel changed from 7 to 83 to avoid WiFi interference.
# Creates a kdetils.cfg file for the KookaManager
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Kookapp.cfg if it exists
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------
# TAGS: #utility #config #radio #log #id
# BEGIN-CODE:
import machine, time, kooka, fonts, os, ujson, ubinascii, sys
disp = kooka.display
# The configuration parameters dictionary
params ={
    'ID':1,    # Kookaberry's ID 1 to 99
    'INTV':10,    # Data logging interval in seconds
    'CHANNEL':83,    # Integer 0 to 83 Radio channel used - higher channels avoid WiFi interference
    'BAUD':0,    # Integer 0 to 2 Speed of radio transmission 250kbps, 1Mbps, 2Mbps
    'POWER':6,    # Integer 0 to 7 Radio transmission power [-30, -20, -16, -12, -8, -4, 0, 4] dbmW
    'NAME':'01',    # Kept for compatibility with prior configurations
    'SURNAME':''    # Kept for compatibility with prior configurations
    }
    
# Parameter selections or constraints
id_min = 1
id_max = 99
intervals =[2,5,10,20,30,45,60,120,300,600,15*60,30*60,40*60,60*60,2*60*60,5*60*60,8*60*60,12*60*60,24*60*60]
channel_min = 0
channel_max = 83

# Function to check whether a file exists
def fileExists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

# Function formats seconds into hh:mm:ss string format
def timefmt(seconds):
    hh = int(seconds / 3600)
    ss = seconds % 3600
    mm = int(ss / 60)
    ss = ss % 60
    return '%0.2d:%0.2d:%0.2d' % (hh,mm,ss)


fname = 'Kookapp.cfg'    # Name of the configuration parameters file
# Test to see if the configuration file already exists and loads it
# No check is performed to verify the parameters' structure
if fileExists(fname):    # Test for the JSON configuration file
    f = open(fname,'rt')
    fl =f.readline()    # Reads the first line
    params = ujson.loads(fl)    # Decode the JSON dictionary
    f.close()
# print(params)    # for debugging
# Set up an array of parameter keys
p_ptr = 0    # pointer to current parameter
p_keys = ['ID','INTV','CHANNEL']    # The parameters that are accessible to edit
# Display system information as a splash screen - press B to proceed to configuration
import os    # Contains system identifier function
info = os.uname()    # Return a string tuple with version information

# Create or update the kdetails.cfg file
# Define dictionary of Kookaberry information
kdetails = {
    'RELEASE': info[2],    # MicroPython release
    'VERSION': info[3].split()[0],    # Firmware version descriptor
    'DATE': info[3].split()[2],    # Date of release
    'MACHINE': info[4],    # Processor details
    'UNIQUE_ID': ubinascii.hexlify(machine.unique_id()).decode('utf-8'),    # Unique Kookaberry identifier
    'MPY_VER': '%d' % (sys.implementation._mpy & 0xff if info[3].split('.')[1] >= '19' else sys.implementation.mpy & 0xff)
    }
#print(kdetails)
f = open('kdetails.cfg','w+')
f.write('%s\n' % ujson.dumps(kdetails))
f.close()

# Splash the Kookaberry details on the display
release = info[2]
version = info[3].split(' ')
mc = info[4].split(' ')
disp.fill(0)
disp.setfont(fonts.mono8x8)
disp.text('%s' % __name__, 0, 6)
disp.setfont(fonts.mono6x7)
disp.text('A-continue', 0, 60)
# Version information
disp.text(mc[0], 0, 20)
disp.setfont(fonts.mono5x5)
disp.text(mc[2], 74, 20)
disp.setfont(fonts.mono6x7)
disp.text('MicroPython %s' % release, 0, 30)
disp.text(version[0], 0, 40)
disp.text('%s %s' % (version[1],version[2]), 0, 50)
disp.show()
while not kooka.button_a.was_pressed(): pass    # Wait here for button B 

# Main loop
p_ptr = 0    # index to the pins names array
intv_ptr = intervals.index(params['INTV'])    # initialise the intervals pointer
#print(intv_ptr,intervals[intv_ptr])

while not kooka.button_a.was_pressed(): # quit if button A pressed
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.text('%s: ' % p_keys[p_ptr], 0, 27)
    if p_keys[p_ptr] == 'INTV': 
        disp.text('%s' % timefmt(params[p_keys[p_ptr]]), 64, 27)
    else: 
        disp.text('%d' % params[p_keys[p_ptr]], 64, 27)
       
    disp.setfont(fonts.mono6x7)
    disp.text('CH:%s ID:%0.2d' % (params['CHANNEL'],params['ID']), 64, 6)
    disp.text('A-ex C-up D-dn B-nxt', 0, 60)
    disp.text('Edit configuration', 0, 16)
    disp.text('C / D: change param', 0, 40)
    disp.text('B: next parameter', 0, 50)
    disp.show()
    if kooka.button_b.was_pressed():    # advance to the next parameter
        p_ptr += 1
        if p_ptr >= len(p_keys): p_ptr = 0
        
    if kooka.button_c.was_pressed():    # index the parameter
        if p_keys[p_ptr] == 'ID':
            params[p_keys[p_ptr]] += 1
            if params[p_keys[p_ptr]] > id_max: params[p_keys[p_ptr]] = id_min
        if p_keys[p_ptr] == 'INTV':
            intv_ptr += 1
            if intv_ptr >= len(intervals): intv_ptr= 0
            params[p_keys[p_ptr]] = intervals[intv_ptr]
        if p_keys[p_ptr] == 'CHANNEL':
            params[p_keys[p_ptr]] += 1
            if params[p_keys[p_ptr]] > channel_max: params[p_keys[p_ptr]] = channel_min

    if kooka.button_d.was_pressed():    # decrement the parameter
        if p_keys[p_ptr] == 'ID':
            params[p_keys[p_ptr]] -= 1
            if params[p_keys[p_ptr]] < id_min: params[p_keys[p_ptr]] = id_max
        if p_keys[p_ptr] == 'INTV':
            intv_ptr -= 1
            if intv_ptr < 0: intv_ptr= len(intervals)-1
            params[p_keys[p_ptr]] = intervals[intv_ptr]
        if p_keys[p_ptr] == 'CHANNEL':
            params[p_keys[p_ptr]] -= 1
            if params[p_keys[p_ptr]] < channel_min: params[p_keys[p_ptr]] = channel_max

# Write the parameters to file and exit
params['NAME'] = '%0.2d' % params['ID']    # for backwards compatibility
f = open(fname,'w+')
f.write('%s\n' % ujson.dumps(params))
f.close()