# File name: 
__name__ = 'SenseDS18'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 30 November 2019
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
# Measure temperature using a DS18B20 onewire digital temperature sensor
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [DS18B20,Temp]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: DS18B20 probe plugged into P4
# /lib files: Kapputilspy, logger.py, doomsday.py, onewire.py, ds18x20.py
# /root files: Kappconfig.txt or Kappconfig.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                    _Config sets up Kookaberry parameters
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, ujson
import onewire, ds18x20
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
#import doomsday    # works out the day of the week from the date (supressed temporarily)

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
sndmsg = [id,'DS18','T']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,T-degC')    # Create the datalogger instance
dlog.start()    # Start the datalogger

dspin = 'P4'
ds_interval = 2000    # milliseconds between sensor reads
ds_read_delay = 1000    # milliseconds between temperature read request and data available
ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(dspin)))

_timer_ds = time.ticks_ms()    # timer used for delays and timing samples
readstate = 0    # controls the DS18B20 two stage temperature reading process
temp = 0

radio_interval = params['INTV'] * 1000    # radio transmission interval
_timer_radio = time.ticks_ms() + radio_interval
radio_err = False

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        if readstate == 0:
        # scan for devices on the bus
            roms = ds.scan()
#            print('found devices:', roms)
            if roms:
                ds.convert_temp()    # request temperature
                _timer_ds = time.ticks_ms() + ds_read_delay # timer to come back and read the temperature
                readstate = 1
            
        # get the temperature
        elif readstate == 1:
            try: temp = ds.read_temp(roms[0])    # assume sensor is first one on the onewire
            except:
                roms=''
                temp = 0
            sndmsg[2] = '%0.1f' % temp    # update the radio buffer
            dlog.update('%s,%0.1f' % (timestr,temp))    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due
            # set up for next sample
            _timer_ds = time.ticks_ms() + ds_interval - ds_read_delay 
            readstate = 0
# Send a radio update per the programmed interval
    if time.ticks_diff(time.ticks_ms(), _timer_radio) >= 0:
        _timer_radio += radio_interval
        print(timestr, sndmsg)
        try:
            if temp: kooka.radio.send(ujson.dumps(sndmsg)) # transmit if a reading taken
            radio_err = False
        except:    # radio error
            radio_err = True

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (dspin, id), 90, 6)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    if radio_err: disp.text('Radio error', 0,40)
    disp.setfont(fonts.mono8x13)
    if roms: disp.text('Temp = %.1f C' % temp, 12, 20)
    else: disp.text('No sensor in %s' % dspin, 0, 20)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = ujson.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
#            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


