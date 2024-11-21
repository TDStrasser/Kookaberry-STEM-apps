# File name: 
__name__ = 'SenseAcc'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 12 November 2019
# Date last modified: 3 November 2020
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
# Measure overall acceleration using the Kookaberry's inbuilt accelerometer
# Logs average and peak acceleration into a file at an interval specified in Kappconfig.txt
# Broadcasts the average and maximum accelerationss over the packet radio in the format [SHK,AccAvg,AccMax]
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: No ports nor peripherals are used
# /lib files: Kapputils.py, kcpu.py, logger.py, doomsday.py
# /root files: Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx.py receives data and transmits time updates
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json, math
from micropython import const
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # converts date to day of week

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
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
sndmsg = [id,'SHK','AA','MA']
acc_interval = 100    # milliseconds between acceleration samples

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,Avg-Acc,Max-Acc')    # Create the datalogger instance
dlog.start()    # Start the datalogger

samples = const(20)
sarray = [0] * samples
parray = [0] * samples
plotx = const(0)
ploty = const(12)
ploth = const(28)
plotw = const(80)
plotxinc = int(plotw/samples)
plotymid = int(ploty + ploth/2)
plotzero = 10
plotrange = const(15)

last_avg = 9.8    # used for checking on sudden changes
last_max = 9.8
last_delta = 1.0

tx_interval = samples - 1    # number of samples between radio transmissions

while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d-%02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]

    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s %s' % (__name__,id), 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('Log in %d' % dlog.log_counter, 60, 60)
    disp.text('%s' % timestr, 0, 50)
# Get the acceleration and compute a single value from the three vectors
    x, y, z = kooka.accel.get_xyz()
    accel = math.sqrt( x * x + y * y + z * z )
#    print(x,y,x,accel)    # uncomment to get diagnostic printout

# Shift the data arrays left and get a fresh sample and scale it
    for i in range(0,samples-1):  
        parray[i]=parray[i+1]    # shift samples left
        sarray[i]=sarray[i+1]
    sarray[samples-1] = accel
    plotzero = int(sum(sarray)/samples)    # zero line is the average of samples
    sample = accel-plotzero
    sample = max(sample,-plotrange/2)
    sample = min(sample,plotrange/2)
    parray[samples-1] = int(sample)
    disp.setfont(fonts.mono8x13)
    disp.text('%0.2f' % accel, 85, 25)
    disp.setfont(fonts.mono6x7)
    disp.text('m/s^2', 85, 35)
    tx_interval -= 1    # count down to radio transmission
    if not tx_interval:    # time for a radio transmission
        accelmax = 0
        accelavg = 0
        for i in range(0, samples):
            accelmax = max(accelmax, sarray[i])    # find the maximum
            accelavg += sarray[i]
        sndmsg[3] = '%0.2f' % accelmax
        accelavg = accelavg / samples
        sndmsg[2] = '%0.2f' % accelavg
        kooka.radio.send(json.dumps(sndmsg))
        tx_interval = samples - 1
# Display the acceleration chart
    disp.rect(plotx,ploty,plotw,ploth+1,1)    # outline rectangle
    for i in range(0,samples-1):
        p1x = i*plotxinc+plotx
        p1y = plotymid-int(parray[i]/plotrange*ploth)
        p2x = (i+1)*plotxinc+plotx
        p2y = plotymid-int(parray[i+1]/plotrange*ploth)
        disp.line(p1x, p1y, p2x , p2y, 1)

    disp.show()
# Update the datalogger with the maximum acceleration
    accelmax = 0
    accelavg = 0
    for i in range(0, samples):
        accelmax = max(accelmax, sarray[i])    # find the maximum
        accelavg += sarray[i]
    accelavg = accelavg / samples
    dlog.update('%s,%0.2f,%0.2f' % (timestr,accelavg,accelmax))    # update the string to be logged
    if abs(last_max - accelmax) >= last_delta or abs(last_avg - accelavg) >= last_delta: dlog.log_write = True    # force logging if significant change
    last_max = accelmax
    last_avg = accelavg
    dlog.write()    # writes the datalogger string when next due

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

    time.sleep_ms(acc_interval)    # Wait for the DHT sensor read interval
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


