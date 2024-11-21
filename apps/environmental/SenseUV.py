# File name: 
__name__ = 'SenseUV'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 12 Aug 2020
# Date last modified: 17 September 2020
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
# Measures UV light level in milliwatts/sqcm using a VEML6070 digital UV sensor
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [UV,watts]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: VEML6070 sensor plugged into P3
# /lib files: Kapputils.mpy, kcpu.mpy, logger.mpy, doomsday.mpy, veml6070_i2c.mpy
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json, math
import veml6070_i2c
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
#import doomsday    # works out the day of the week from the date (supressed temporarily)

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # RTC time
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
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
sndmsg = [id,'UVc','W']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,UV-mW/sqcm')    # Create the datalogger instance
dlog.start()    # Start the datalogger

dspin = 'P3'
i2c = machine.I2C(sda=machine.Pin('PA9'), scl=machine.Pin('PA10'), freq=50000)
s_flag = False
uv = veml6070_i2c.Veml6070(i2c)

uv_light = 0

dsinterval = 2000
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Read and process the sensor, send the radio message, update the logger
    if time.ticks_diff(time.ticks_ms(), _timer_ds) >= 0:
        _timer_ds += dsinterval    # only take a sample every period
        t_read = False
        try:
            uv_light = uv.get_uva_light_intensity() / 10 # Scale from W/sqm to mw/sqcm
            t_read = True
#            uv_risk = uv.get_estimated_risk_level(uv_light)    # not consistent with BOM risk which is 1 point per 25mW/sqm
            uv_index = int(uv_light / 2.5)
#            print(uv.get_uva_light_intensity_raw())
            sndmsg[2] = '%.1f' % uv_light
#            print(t_read, timestr, sndmsg)    # Diagnostic use (uncomment)
            logstr = '%s,%.1f' % (timestr,uv_light)
            dlog.update(logstr)    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due
            kooka.radio.send(json.dumps(sndmsg))    # Log via radio
            print(sndmsg)
        except:
            print(logstr)
            pass
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
        disp.text('UV:%4.1f mW/sqcm' % uv_light, 10, 15)
        # Prepare the UV index and risk display
        if uv_index <= 2: uv_risk = "low"
        elif uv_index <= 5: uv_risk = "moderate"
        elif uv_index <= 7: uv_risk = "high"
        elif uv_index <=10: uv_risk = "very high"
        else: uv_risk = "extreme"
        disp.text('UVindex :%d %s' % (uv_index, uv_risk), 10, 25)
        disp.rect(10, 30, 110, 10, 1)
        disp.fill_rect(10, 30, int(math.log10(max(uv_light,1))/math.log10(328)*110), 10, 1)

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
#            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            ftime[3]=1    #workaround to prevent memory allocation problems
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


