# File name: 
__name__ = 'SenseCO2'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 19 May 2020
# Date last modified: 4 November 2020
# MicroPython Version: 1.12 for the Kookaberry V4-05
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
# Measures total eCO2 in ppm and VOCsin ppb using a CCS811 digital gas sensor
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [CO2,VOC]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: CCS811 sensor plugged into P3
# /lib files: Kapputils.mpy, kcpu.mpy, logger.mpy, doomsday.mpy, CCS811.mpy
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json, math
import CCS811
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # works out the day of the week from the date (supressed temporarily)

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
disp.print(__name__)
disp.print('Initialising...')

params = config('Kappconfig.txt')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file
kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=40) # set up the radio
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'CCS','CO2','VOC']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,eCO2-ppm,tVOC-ppb')    # Create the datalogger instance
dlog.start()    # Start the datalogger

s_pin = 'P3'
i2c = machine.I2C(scl='PA9',sda='PA10', freq=100000)
s_flag = False
s = CCS811.CCS811(i2c)
time.sleep(1)    #let the sensor start up and stabilise
eCO2 = 0
tVOC = 0
# Tables of Air Quality Indicators
eCO2_levels = [500,1000,2500,5000,40000,100000]
eCO2_status = ['Good','OK','Poor','Bad','Evac','Tox']
tVOC_levels = [50,750,6000,40000]
tVOC_status = ['Good','Poor','Bad','Tox']

s_interval = 2000
_timer_s = time.ticks_ms()    # timer used for delays and timing samples
tx_interval = params['INTV'] * 1000    # interval between radio update in milliseconds
_timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer


while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_s) >= 0:
        _timer_s += s_interval    # only take a sample every period
        s_read = False
        logstr = '%s,%d,%d' % (timestr,eCO2,tVOC)
        try:
            if s.data_ready():
                eCO2 = s.eCO2
                tVOC= s.tVOC
#                print('eCO2: %d ppm, TVOC: %d ppb' % (s.eCO2, s.tVOC))
                s_read = True
                sndmsg[2] = '%d' % eCO2
                sndmsg[3] = '%d' % tVOC
#                print(s_read, timestr, sndmsg)    # Diagnostic use (uncomment)
                logstr = '%s,%d,%d' % (timestr,eCO2,tVOC)
                dlog.update(logstr)    # update the string to be logged
                dlog.write()    # writes the datalogger string when next due
                
        except:
            print(logstr)
            pass
# send the radio update
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += tx_interval    # transmit every period
        if s_read: kooka.radio.send(json.dumps(sndmsg))    # send the radio message

# Evaluate air quality
    eCO2_q = ''
    for i in range(0,len(eCO2_levels)):
        if eCO2 <= eCO2_levels[i]:
            eCO2_q = eCO2_status[i]
            break
        else: pass
    tVOC_q = ''
    for i in range(0,len(tVOC_levels)):
        if tVOC <= tVOC_levels[i]:
            tVOC_q = tVOC_status[i]
            break
        else: pass
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,s_pin), 90, 6)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono6x7)
    if s_read: 
        disp.text('eCO2: %d ppm' % eCO2, 6, 20)
        disp.text('tVOC: %d ppb' % tVOC, 6, 30)
        disp.text('%s' % eCO2_q, 100, 20)
        disp.text('%s' % tVOC_q, 100, 30)

    else: disp.text('Sensor fault', 0, 20)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


