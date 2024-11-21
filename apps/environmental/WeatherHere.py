# File name: 
__name__ = 'WeatherHere'
# Lesson Plan: KLP004
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 28 July 2018
# Date last modified: 5 December 2020
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
# A local weather station reading temperature, absolute humidity and wind speed.
# Temperature and Humidity using the Gravity DHT11 Sensor 
# Windspeed derived from pulses read by a magnetic or hall sensor attached to an anemometer - limits have been placed to filter out improbable windspeeds
# The apparent temperature is calculated using equations from the Australian Bureau of Meteorology
# A datalogging function has been added which is configured by the file Kookapp.cfg
# Begin code
# Initial conditions
import machine, kooka, dht, fonts, time, math, time
from Kapputils import config    # utility to read the configuration file
fname = __name__ + '.CSV'    # Log file name is derived from the lesson plan number
disp = kooka.display
# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
rtc = machine.RTC()    # instantiate the Real Time Clock
ktime = rtc.datetime()    # read the time

# Set up the DHT11 temperature and humidity sensor
dht_pin = 'P2'
anem_pin = 'P4'
th_pin = machine.Pin(dht_pin)
buf = bytearray(5)
condition = ['Cold', 'Cool', 'Mild', 'Warm','Hot','Torrid']
threshholds = [12, 18, 23, 30, 35, 60]
sample_interval = 2    # minimum interval at which the sensor can be sampled
# Set up the anemometer using an opto-coupler digital sensor
an_pin = machine.Pin(anem_pin, machine.Pin.IN)
an_timer =[0,0,0]    #bytearray time now, time last, time interval
tnow = tlast = time.ticks_ms()    # initialise the time
windspeed = float(0)    # Variable for wind speed in km/h
pulses = 4    # Number of magnetic pulses per revolution
radius = 40    # Radius of the anemometer turbine in millimetres
circumference = 2 * math.pi * radius  # circumference of the anemometer turbine
pulse_distance = circumference / float(pulses) / 1000  # distance between pulse points in metres
wind_limit = 40    # Maximum windspeed - values greater will be ignored (caused by anemometer hub reversing on stop)
wind_calib_gain = 1.7    # Linear approximation for anemometer inefficiency
wind_calib_offset = 0    # Anemometer calibration axis intercept in kph
wind_samples = [0]    # Array of windspeed samples

def pulserate(p):    # handler for interrupt driven pulse rate
    an_timer[0] = time.ticks_ms() # mark the time in ticks at the interrupt
    an_timer[2] = an_timer[0] - an_timer[1]  # interval = time now minus last time
    an_timer[1] = an_timer[0]
    return

an_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulserate)

# Set up the radio
kooka.radio.disable()         # turn off bluetooth to save battery power

params = config('Kookapp.cfg')   # read the configuration file
interval = int(params['INTV'])      # use interval from the configuration file
if interval < sample_interval : interval = sample_interval    # limit minimum interval
f = open(fname,'w+')         # open a text file for writing
f.write('Date-Time,Temperature degC,Rel Humidity %,Apparent  Temp degC,Avg Wind kph, Min Wind kph,Max Wind kph,Condition\n')   # write the heading line
f.close()   # Close the file to guard against power down corruption
dur_timer = 0   # initialise the logging timer
intv_timer = 0  # initialise the interval timer

while not kooka.button_a.was_pressed():
    t0 = time.ticks_ms() # mark the time in ticks at the beginning of the loop
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 63)
    try:
        dht.dht_readinto(th_pin, buf)
    except OSError:
        disp.setfont(fonts.mono6x7)
        disp.text('Connect DHT11 to %s' % dht_pin, 0, 20)
        disp.text(' Anemometer to %s' % anem_pin, 0, 30)
    else:
        disp.setfont(fonts.mono6x7)
        disp.text('Temp: %dC' % buf[2], 8, 28)
        disp.text('Humi: %d%%' % buf[0], 8, 37)
        disp.text('%s' % dht_pin, 110,28)
# Work out the duration timer
        hours = int(dur_timer/3600)
        minutes = int((dur_timer - (hours * 3600))/60)
        seconds = dur_timer - (hours * 3600) - (minutes * 60)
        disp.text('%02d:%02d:%02d @ %d' % (hours, minutes, seconds, interval), 0, 19)
# Work out the apparent temperature
        rh = float(buf[0])
        Ta = float(buf[2])
        e = (rh / 100) * 6.105 * math.exp( 17.27 * Ta / ( 237.7 + Ta ) )
        AT = Ta + 0.33 * e - 4.00 - 0.7 * windspeed * 1000 / 3600
        i = 0
        while (i < len(threshholds)):
            if (AT <= threshholds[i]) : break
            i+=1
        disp.text('AppT: %dC' % AT, 8, 46)
        disp.text('%s' % condition[i], 66, 63)
# Work out the wind speed
        wind_last = windspeed    # remember the previous windspeed
        if an_timer[2] > 0: windspeed = 3600000 / float(an_timer[2]) * pulse_distance * wind_calib_gain / 1000 + wind_calib_offset
        if windspeed > wind_limit: windspeed = wind_last    # ignore improbable windspeed samples
        wind_still = abs(t0 - an_timer[1])/1000    # time since the last interrupt
        if wind_still > 2 * sample_interval: windspeed = 0 # if no interrupts received in successive sampling intervals then set windspeed to zero
        disp.text('Wind: %3.1fkph' % windspeed, 8, 55)
        disp.text('%s' % anem_pin, 110, 55)
        wind_samples.append(windspeed)    # Keep a record between file writes

# Control the sampling interval
        if (intv_timer == 0):   # write to file every interval
# Construct the time string
            ktime = rtc.datetime()  # Refresh the time
            timestr = "%02d/%02d/%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]

# Work out the average, maximum and minimum windspeeds
            if len(wind_samples) : del wind_samples[0]    # if samples taken delete first dummy sample
            wind_mean = sum(wind_samples)/len(wind_samples)
            wind_min = min(wind_samples)
            wind_max = max(wind_samples) 
            for i in range((len(wind_samples)-1),1,-1): del wind_samples[i]  # reinitialse sample list
            wind_samples[0] = 0 
# write data to the log file             
            f = open(fname,'a+')         # open the text file for appending
            f.write('%s,%d,%d,%d,%3.2f,%3.2f,%3.2f,%s\n' % (timestr, buf[2], buf[0], AT, wind_mean, wind_min, wind_max, condition[i]))
            f.close()   # Close again to guard against power down corruption
        t1 = time.ticks_ms() # mark the time in ticks after the loop work is done
        t_sleep = sample_interval * 1000 - time.ticks_diff(t1, t0)    #calculate how long before min_interval is up
        time.sleep_ms(t_sleep)
        dur_timer += sample_interval  # keep the timers ticking over
        intv_timer += sample_interval
        if (intv_timer >= interval):    # reset interval timer every interval
            intv_timer = 0

    disp.show()

# Clean up and exit
f.close()