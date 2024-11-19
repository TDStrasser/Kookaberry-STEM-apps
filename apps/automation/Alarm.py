# File name: 
__name__ = 'Alarm'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 28 February 2020
# Version 1.4
# Date last modified: 1 December 2020
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
# Description
# A simple alarm system that arms and disarms, with a single trigger input on a timer
# The trigger timer is adjustable, the alarm reset timer is fixed
# An alarm.CSV log file is written whenever the alarm changes state
# Broadcasts the alarm signal on change over the packet radio in the format [ID, Dig,alarm state]
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Alarm trigger (PIR etc) on P1, alarm output on P2
# /lib files: Kapputils.py, doomsday.py
# /root files: Kookapp.cfg or Kappconfig.txt
# Other dependencies: Nil
# Complementary apps: SenseRx.py receives data and transmits time updates
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time, json, framebuf
from micropython import const
from Kapputils import config    # module to read the configuration file
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
sndmsg = [id,'Dig','0']

# Alarm parameters
sensitivity = [20,50,100,200,500,750,1000,2000,5000]    # milliseconds to trigger
sens_len = len(sensitivity)
sens_ptr = int(sens_len/2)
trigger_t = sensitivity[sens_ptr]    # alarm trigger time
alarm_t = 5000    # alarm output duration time
_t_trigger = time.ticks_ms()
_t_alarm = time.ticks_ms()
# Set up the input and output
pir_pin = 'P1'
pir_last = False
pir = machine.Pin(pir_pin, machine.Pin.IN, machine.Pin.PULL_UP)    # create digital input for PIR
relay_pin = 'P2'
relay = machine.Pin(relay_pin, machine.Pin.OUT)    # create the digital output for the alarm buzzer or logic output
alarm = False
armed = False
trigbar_w = 80    # Trigger timing display dimensions
trigbar_h = 10

# set up the datalogging file
fname = __name__+'.csv'
f = open(fname, 'w+')
f.write('Date-Time,ID,Alarm\n')
f.close()

update = False    # Flag used to trigger a file and radio update

# Create a movement icon
motion = bytearray([0xE0, 0x10, 0x88, 0x60, 0x10, 0x00, 0xC0, 0x20, 0xF0, 
0xF6, 0x26, 0x40, 0x80, 0x00, 0x10, 0x60, 0x88, 0x10, 
0xE0, 0x07, 0x08, 0x11, 0x06, 0x08, 0x00, 0x61, 0x58, 
0x0F, 0x07, 0x04, 0x3C, 0x20, 0x00, 0x08, 0x06, 0x11, 0x08, 0x07])
m_icon = framebuf.FrameBuffer(motion, 19, 16, framebuf.MONO_VLSB)
# Create an alert icon
alert = bytearray([0x38, 0x1E, 0x02, 0x3B, 0x09, 0xCC, 0xE0, 0xF0, 
0xF0, 0xE0, 0xCC, 0x09, 0x3B, 0x02, 0x1E, 0x38,
0x00, 0x00, 0x00, 0x08, 0x1C, 0x1F, 0x1F, 0x5F, 
0x5F, 0x1F, 0x1F, 0x1C, 0x08, 0x00, 0x00, 0x00])
a_icon = framebuf.FrameBuffer(alert, 16, 16, framebuf.MONO_VLSB)


while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
# Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('Ch%2d ID%s' % (params['CHANNEL'],id), 70, 6)
    disp.text('A-x  C+trig-D  B-arm', 0, 63)
    disp.setfont(fonts.mono5x5)
    disp.text('%s' % timestr, 0, 54)
    disp.text('I:%s' % pir_pin, 110, 45)
    disp.text('O:%s' % relay_pin, 110, 54)
# Increment the trigger delay via button C
    if kooka.button_c.was_pressed():
        sens_ptr = min(sens_len-1, sens_ptr + 1)    # increment
        trigger_t = sensitivity[sens_ptr]
# Decrement the trigger delay via button D
    if kooka.button_d.was_pressed():
        sens_ptr = max(0, sens_ptr - 1)    # increment
        trigger_t = sensitivity[sens_ptr]
# Arm/disarm the alarm delay via button B
    if kooka.button_b.was_pressed():
        armed = not armed
        _t_trigger = time.ticks_ms()
        _t_alarm = time.ticks_ms()

# Get the digital inputs
    if pir.value():    # Motion detected
        if not pir_last:
            _t_trigger = time.ticks_ms() + trigger_t    # Start the trigger timer
            pir_last = True    # Remember the last PIR value
    else:
        pir_last = False    # Remember the last PIR value
# Process the alarm triggering and reset
    if time.ticks_diff(time.ticks_ms(), _t_trigger) >= 0 and armed and pir_last:    # Trigger delay expired
        if not alarm: update = True    # Update on initiation of alarm
        alarm = True
        _t_alarm = time.ticks_ms() + alarm_t    # Start the alarm reset timer
            
    if alarm and time.ticks_diff(time.ticks_ms(), _t_alarm) >= 0:    # Alarm reset expired
        update = True    # Update on change of alarm state
        alarm = False
        
    relay.value(alarm)    # Set the output to the alarm state
    
# Update the Kookaberry front panel LEDs
    if pir_last: kooka.led_orange.on()
    else: kooka.led_orange.off()
    if armed and not alarm: kooka.led_green.on()
    else: kooka.led_green.off()
    if alarm: 
        kooka.led_red.on()
        kooka.led_green.off()
    else: kooka.led_red.off()
    
# Update the log file and send radio
    if update:
        f = open(fname,'a+')
        last_alarm = not alarm
        f.write('%s,%s,%d\n' % (timestr, id, last_alarm))    # Log end of last alarm
        f.write('%s,%s,%d\n' % (timestr, id, alarm))    # Log beginning of new alarm
        f.close()
#        print('%s,%s,%d\n' % (timestr, id, alarm))
        kooka.radio.send(json.dumps(sndmsg))    # Send prior alarm state to mark the end
        sndmsg[2] = '%d' % alarm
        print(sndmsg)
        kooka.radio.send(json.dumps(sndmsg))    # Send new alarm state
        update = False

# Prepare the dynamic displays
    if pir_last: disp.blit(m_icon, 6, 10)
    if alarm: disp.blit(a_icon, 80, 10)
    if armed: 
        disp.setfont(fonts.mono8x8)
        disp.text('Armed', 30, 24)
    if alarm:
        disp.text('%d' % int(abs(time.ticks_diff(time.ticks_ms(), _t_alarm))/1000+0.5), 100, 24)
    disp.setfont(fonts.mono6x7)
    disp.text('%0.3f' % float(trigger_t/1000), 90, 36)
    kooka.display.rect(4, 30, trigbar_w, trigbar_h, 1)
    if pir_last:
        trig_elapsed = time.ticks_diff(_t_trigger,time.ticks_ms())
        trig_elapsed = trigbar_w - max(0,min(trigbar_w,int(trig_elapsed / trigger_t * trigbar_w)))
        kooka.display.fill_rect(4, 30, trig_elapsed, trigbar_h, 1)

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
kooka.radio.disable()    # turn off the radio


