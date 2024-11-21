# FILENAME: SenseBME.py
__name__ = 'SenseBME'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 9 April 2020
# DATE-MODIFIED: 25 May 2022 - changed startup when no sensor connected
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
# DESCRIPTION:
# Measures temperature, relative humidity and air pressure using a BME280 sensor
# Logs the measurements into a file at an interval specified in Kookapp.cfg
# Broadcasts the sensor readings over the packet radio in the format [BME,AmbTemp,RH,Press]
# If the sensor is not present prompt is displayed. Logging suspends until a sensor is present.
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: BME280 sensor plugged into P3
# /lib files: Kapputils.mpy, (logger.mpy, doomsday.mpy, bme280.mpy are embedded in Kookaberry firmware)
# /root files: Kookapp.cfg
# Other dependencies: Nil
# Complementary apps: SenseRx receives the radio datagrams and updates the time
#                        KookatimeTx can also update the time
#------------------------------------------
# TAGS: #temperature #pressure #humidity #sensor #log #radio #i2c #environment
# BEGIN-CODE:
# Initial conditions

import machine, kooka, fonts, time, json
import bme280
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # works out the day of the week from the date

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
kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=50) # set up the radio
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]
sndmsg = [id,'BME','T','H','P']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,AmbT-degC,Humid-%,Pressure-hPa')    # Create the datalogger instance
dlog.start()    # Start the datalogger

dspin = 'P3'
i2c = machine.I2C(scl=machine.Pin('P3B'), sda=machine.Pin('P3A'), freq=50000)
s_flag = False
try:
    bme = bme280.BME280(i2c=i2c) # Initialise the BME280 sensor
except: # Sensor not detected, swap scl and sda lines and try again
    i2c = machine.I2C(scl=machine.Pin('P3A'), sda=machine.Pin('P3B'), freq=50000)
    try:
        bme = bme280.BME280(i2c=i2c) # Initialise the BME280 sensor
    except: # BME280 still not found
        bme = None
if bme:
    disp.print('BME280 found')
else:
    disp.setfont(fonts.mono6x7)
    disp.print('Connect BME280')
    disp.print(' to P3')
    disp.print('.. and restart app')
    time.sleep(5)
    disp.print('Exiting')
    raise SystemExit
    
temp = 0
press = 0
humid = 0

dsinterval = 2000    # sensor sampling interval
txinterval = params['INTV'] * 1000    # radio transmitting interval
_timer_ds = time.ticks_ms()    # timer used for delays and timing samples
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
#            print(bme.values)
            temp = bme.values[0]
            press = bme.values[1]
            humid = bme.values[2]
            t_read = True
            sndmsg[2] = '%.1f' % temp
            sndmsg[3] = '%.1f' % humid
            sndmsg[4] = '%.1f' % press
#            print(t_read, timestr, sndmsg)    # Diagnostic use (uncomment)
            logstr = '%s,%.1f,%.1f,%.1f' % (timestr,temp,humid,press)
            dlog.update(logstr)    # update the string to be logged
            dlog.write()    # writes the datalogger string when next due

        except:
            print('Exception:',logstr)
            pass
            
# Transmit data over the radio
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += txinterval    # update the timer for the next interval
        if t_read: kooka.radio.send(json.dumps(sndmsg))    # send the data if available
        

# Prepare the display
    disp.fill(0)
    disp.setfont(fonts.mono6x7)
    disp.text(__name__, 0, 6)
    disp.text('%s %s' % (id,dspin), 90, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
    disp.setfont(fonts.mono6x7)
    if t_read: 
        disp.text('Temp: %6.1f C' % temp, 12, 17)
        disp.text('RelH: %6.1f %%' % humid, 12, 26)
        disp.text('Press: %6.1f hPa' % press, 12, 35)
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


