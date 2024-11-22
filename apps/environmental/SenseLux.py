# File name: 
__name__ = 'SenseLux'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 2 May 2020
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
# Measures light level in Lux using a VEML7700 digital light sensor
# Logs the measurements into a file at an interval specified in Kookapp.cfg
# Broadcasts the sensor readings over the packet radio in the format [Lux,Light]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: VEML7700 sensor plugged into P3
# /lib files: Kapputils.mpy, logger.mpy, (doomsday.mpy, veml7700.mpy are embedded in Kookaberry firmware)
# /root files: Kookapp.cfg or Kappconfig.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json, math
from veml7700 import VEML7700
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
sndmsg = [id,'Lux','L']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,Light-lux')    # Create the datalogger instance
dlog.start()    # Start the datalogger

# Function to initialise the VEML sensor
def sensor_init(i2c, adx):
    sensors = i2c.scan()    # scan the I2C bus for addresses
    for x in sensors:
        if x == adx: 
            veml = VEML7700(address=adx, i2c=i2c, it=100, gain=1/8)
            return veml
        
i2c = machine.SoftI2C(scl='PA9',sda='PA10', freq=50000)
veml = sensor_init(i2c, 0x10)
if not veml: # Couldn't find sensor, swap pins on I2c and try again
    i2c = machine.SoftI2C(scl='PA10',sda='PA9', freq=50000)
    veml = sensor_init(i2c, 0x10)
light = 0
dspin = 'P3'

dsinterval = 2000
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples
txinterval = params['INTV'] * 1000    # radio transmitting interval
_timer_tx = time.ticks_ms() + txinterval

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        _timer_ds += dsinterval    # only take a sample every period
        t_read = False
        try:
            light = veml.read_lux()
            t_read = True
            sndmsg[2] = '%.1f' % light
#            print(t_read, timestr, sndmsg)    # Diagnostic use (uncomment)
            logstr = '%s,%.1f' % (timestr,light)
            dlog.update(logstr)    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due
        except:    # Couldn't take a reading from the sensor
            light = 0
            i2c = machine.SoftI2C(scl='PA9',sda='PA10', freq=50000)
            veml = sensor_init(i2c, 0x10)
            if not veml: # Couldn't find sensor, swap pins on I2c and try again
                i2c = machine.SoftI2C(scl='PA10',sda='PA9', freq=50000)
                veml = sensor_init(i2c, 0x10)

# Transmit data over the radio
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += txinterval    # update the timer for the next interval
        if t_read: kooka.radio.send(json.dumps(sndmsg))    # send the data if available
        print(sndmsg)
        
# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,dspin), 90, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono6x7)
    if t_read: 
        disp.text('Light: %6.1f lux' % light, 12, 17)
        disp.rect(10, 27, 110, 10, 1)
        disp.fill_rect(10, 27, int(math.log10(max(light,1))/math.log10(120000)*110), 10, 1)

    else: disp.text('Plug sensor into %s' % dspin, 0, 20)
    disp.show()

# Check for time updates
    msg = kooka.radio.receive()    #listen for a message
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
#            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


