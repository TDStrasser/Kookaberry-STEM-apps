# File name: 
__name__ = 'SenseRx'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 17 October 2019
# Date last modified: 8 May 2021 - added SensePT100 to table
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
# This program listens to the packet radio, and displays messages received.
# The program records what it receives to file in SenseRxLog.csv in the root directory
# It is intended to be used with the SenseXXX apps that measure and log various sensors
# Extended to accommodate the STELR sustainable housing kit apps
# Extended to relay data via UART1 for tethered applications
"""
Update to record a sparse CSV file catering for all the SenseXX sensors
and keeping the columns for their data consistent.
The CSV file column layout is as follows:
Column    Item
1    Date and time string
2    Kookaberry ID
3    Sensor Identification
# Atmospheric measurements
4    Ambient Temperature degC
5    Probe Temperature degC
6    Humidity %
7    Pressure hPa
8    Windspeed kph
9    Precipitation mm
10    CO2 ppm
11    VOC ppb
12    PM2.5 particulates ug/m3
13    PM10 particulates ug/m3
# Light measurements
14    Light level Lux
15    UV Index
# Fluid measurements
16    Moisture level %
17    Total dissolved solids ppm
18    Fluid turbidity JTU (Jackson Turbidity Units)
19    Alkalinity pH
# Physical measurements
20    Velocity m/sec
21    Acceleration m/sec2
22    Angle degrees
23    Distance metres
24    Weight kgs
# Electrical measurements
25    Voltage Volts
26    Current Amps
27    Resistance ohms
28    Power Watts
29    Energy Watt-hours
30    Frequency Hz
# Other
31    Generic Analogue 1 %
32    Generic Analogue 2 %
33    Generic Numeric decimal
34    T1 probe temperature degC (additional for STELR app)
35    T2 probe temperature degC (additional for STELR app)
36    T3 probe temperature degC (additional for STELR app)
37    Time in seconds
"""
# Update relays data via UART1 to feed to an outboard server such as Node-Red
# The UART will also receive and process correctly formatted time updates from the UART.
# The UART receive time format is {[YYYY,MM,DD,HH,MM,SS]}
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Kapputils.py, kcpu.py, TimeConfig.py
# /root files: Kookapp.cfg
# Other dependencies: DS3231 battery clock on P1 [optional]
# Complementary apps: SenseXXX.py sensor apps
#------------------------------------------
# Begin code
import TimeConfig
# Clean up RAM
from sys import modules
from gc import collect
for fn in modules: 
    if fn != 'kooka' and fn != 'sh1106':
        modules.pop(fn)    # free up the RAM used by other modules
    collect()
from machine import RTC, UART
import kooka, time, json, fonts
import doomsday    # module converts date to day of week
from Kapputils import config    # utility to read the configuration file
disp_lines = ['']*5
disp_length = len(disp_lines) - 1
disp_locs = [17,26,35,44,53]
# Set up the sparse CSV headings and index
column_h = ['Time','ID','Sensor','Ta-degC','To-degC','H-%','P-hPa','Wind-kph','Rain-mm','CO2-ppm','VOC-ppb','PM2.5-ug/m3','PM10-ug/m3','L-Lux','UV-I','Moist-%','TDS-ppm','Turb-JTU','pH','V-m/s','a-m/s2','Ang-deg','d-m','Wt-kgs','Volts','Amps','Ohms','Watts','E-Wh','F-Hz','A1-%','A2-%','N','T1-degC','T2-degC','T3-degC','t-secs']
sensors = {    # Dictionary of sensor and column mapping, -1 means ignore
    'SHK': [20,-1],    # SenseAcc - acceleration
    'Anlg': [30,31],    # SenseAnlg- dual generic analogue
    'BME': [3,5,6],    #SenseBME- BME280 T,H,P
    'BMP280': [3,6],    #SenseBMP - BMP280 T,P
    'CCS': [9,10],    # SenseCO2 - CCS811 CO2,VOC
    'DHT11': [3,5],    # SenseDHT - DHT11 T,H
    'DHT22': [3,5],    # SenseDHT - DHT22 T,H
    'DS18': [4,-1],    # SenseDS18 - DS18B20 probe - T
    'IRT': [3,4],    # SenseIRT - IR Temp probe - Ta,To
    'PT100': [4,26],    # SensePT100 - High temperature RTD probe - T, R
    'Ill': [-1,13],    # SenseLight - Analogue Light Sensor
    'Lux': [13,-1],    # SenseLux - VEML7700 Luxmeter
    'NTCT': [4,-1],    # SenseNTCT - NTCT temperature probe
    'SDS011': [11,12],    # SenseSDS - SDS011 particulates PM2.5, PM10
    'UVI': [14,-1],    # SenseUVI - Analogue UV Index sensor
    'To3': [33,34,35],    # STELR-Temp 3 x DS18B20 sensors
    'LxUV': [13,14],    # STELR_LxUV VEML7700 and analogue UVI sensor
    'Spd': [36,19],    # SpeedTrap - time in secs and velocity in m/s
    'ReT': [36,-1],    # ReTimer - reaction time in seconds
    'Dig': [32]    # Digital app such as Alarm
    }
    
# Use the Kookaberry Real Time Clock.
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
rtc = RTC()    # instantiate the Real Time Clock
time_sent = False    # one shot flag for sending time updates

params = config('Kookapp.cfg')   # read the configuration file
# flag to set up the radio for later use
radio_on = False

# Prepare the UART port to relay the sensor data received.
uart = UART(1, 9600,bits=8, parity=None, stop=1)

# Prepare the logging file
fname = __name__+'.csv'
f = open(fname,'w+')    # open file for writing - overwrites any prior file
f.write('%s\n' % ','.join(column_h) )    # write the headings
f.close()
collect()
disp = kooka.display    # initialise the display
msg_count = 0

while not kooka.button_a.was_pressed():
    # Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
    # Set up the radio if not already on
    if not radio_on:
        try:    # Restarting the radio
            print('Radio init ', timestr)
            kooka.radio.enable()
            chan = int(params['CHANNEL'])      # use channel from the configuration file
            baud = int(params['BAUD'])      # use data rate from the configuration file
            pwr = int(params['POWER'])      # use transmit power from the configuration file
            kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=50) # set up the radio
            radio_on = True
        except:
            radio_on = False

    if ktime[6]%10 == 0 and not time_sent and ktime[0] >= 2020: # Send time beacon every 10 seconds if current time has been set ie. years is 2020 or later
        msgstr = '[%4d,%2d,%2d,%2d,%2d,%2d]' % (ktime[0],ktime[1],ktime[2],ktime[4],ktime[5],ktime[6])
        try:
            kooka.radio.send(msgstr)    # send time every 10 seconds
            time_sent = True
            radio_on = True
#        print(msgstr)
        except:
            radio_on = False
            
    elif ktime[6]%10 > 0: time_sent = False    # resets time update flag
    
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    if radio_on: rstr = 'OK' 
    else: rstr=' !'
    disp.text('%s Ch %d' % (rstr,chan), 72, 10)
    disp.text('A-ex', 6, 63)	   # A Key = Exit
    disp.setfont(fonts.mono5x5)
    disp.text('%s' % timestr, 36, 63)	   # A Key = Exit
#    disp.text('Msg: %d' % msg_count, 50, 62)	   # No of messages received
    for i,line in enumerate(disp_lines):
        disp.text('%s' % line, 4, disp_locs[i])    # display last received messages
        
    if radio_on: 
        try:
            msg = kooka.radio.receive()    #listen for a message
        except:
            radio_on = False
        
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  pass  # is a time update so ignore
        else:    # not a time update so process
            msg_count += 1
            disp_lines[0] = disp_lines[1]
            disp_lines[1] = disp_lines[2]
            disp_lines[2] = disp_lines[3]
            disp_lines[3] = disp_lines[4]
            sensordata = json.loads(msg)
            sensorstr = ','.join(sensordata)
            for i in range(0,len(sensordata)): sensordata[i] = str(sensordata[i])# Guard against non-string data
            if sensordata[1] not in sensors:    # Sensor message not known
                sensorstr += '!'
                print('Unknown sensor',sensorstr)
            else:    # Sensor identified - parse and log
                logstr = '%s,%s,' % (timestr, ','.join(sensordata[0:2]))    # Time, ID, Sensor
                sd_item = 2
                sd_len = len(sensordata)
                for i in range(3,len(column_h)):    # range across columns to place sensor data
                    if sd_item < sd_len:
                        ignore = False
                        if sensors[sensordata[1]][sd_item-2] == -1: ignore = True   #ignore sensor item
                        elif i == sensors[sensordata[1]][sd_item-2] and not ignore:    # if this column
                            logstr += sensordata[sd_item]
                            sd_item += 1
                    logstr += ',' 
                f = open(fname, 'a+')
                f.write('%s\n' % logstr)    # update the log file
                f.close()
                print(logstr)
                # Relay sensor data via UART
                for i in range(2, len(sensordata)):
                    index = sensors[sensordata[1]][i-2]
                    if index >= 0:
                        series = column_h[index] + "-" + sensordata[0]
                        value = sensordata[i]
                        uart.write('{%s:%s}' % (series, value))
                    
            disp_lines[disp_length] = '%3d' % msg_count + ' ' + sensorstr
    disp.show()
# Check for time updates from the UART
    if uart.any():
        msg = uart.readline().decode('utf-8').rstrip('\n')
    if msg:    # radio has received a message
        print(msg)
        if len(msg) >= 16 and len(msg) <= 21 and msg[0] == '[' and msg[len(msg)-1] == ']' and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
    
# Clean up and exit
kooka.radio.disable()    # turn packet radio off

