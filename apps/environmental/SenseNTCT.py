# File name: 
__name__ = 'SenseNCT'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 12 November 2019
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
# Measure temperature using a negative temperature coefficient thermistor (NTCT) sensor
# Logs the measurements into a file at an interval specified in Kookapp.cfg
# Broadcasts the sensor readings over the packet radio in the format [NTCT,Temp]

#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Quokka NTCT board and probe plugged into P5
# /lib files: Kapputilspy, logger.py, ntct.py, doomsday.py
# /root files: Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                    _Config.py sets up Kookaberry parameters
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import ntct    # module that interfaces to the NCT sensor
import doomsday    # converts date to day of week

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
params = config('Kookapp.cfg')   # read the configuration file
# set up the radio for later use
kooka.radio.enable()
chan = int(params['CHANNEL'])      # use channel from the configuration file
baud = int(params['BAUD'])      # use data rate from the configuration file
pwr = int(params['POWER'])      # use transmit power from the configuration file
kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=40) # set up the radio
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'NTCT','T']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,T-degC')    # Create the datalogger instance
dlog.start()    # Start the datalogger

ntctpin = 'P5'
sens_interval = 2000    # milliseconds between sensor reads
thermistor = ntct.NTCT(ntctpin)    # create the thermistor object on the input
t_read = False    # True when temperature sensor has a fresh reading
_timer_sens = time.ticks_ms()    # timer used for delays and timing samples
txinterval = params['INTV'] * 1000    # radio transmitting interval
_timer_tx = time.ticks_ms() + txinterval

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        t_read = False
        temp = thermistor.read_temp()    # read the thermistor
        sndmsg[2] = '%0.1f' % temp
        t_read = True
        dlog.update('%s,%0.1f' % (timestr,temp))    # update the string to be logged
        dlog.write()    # writes the datalogger string when next due

# Transmit data over the radio
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += txinterval    # update the timer for the next interval
        if t_read: kooka.radio.send(json.dumps(sndmsg))    # send the data if available
        print(timestr, sndmsg)
    
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 00, 8)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,ntctpin), 90, 8)
    disp.text('A-exit', 0, 63)
    disp.text('Log in %d' % dlog.log_counter, 60, 63)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono8x13)
    disp.text('Temp = %.1f C' % temp, 12, 25)
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
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


