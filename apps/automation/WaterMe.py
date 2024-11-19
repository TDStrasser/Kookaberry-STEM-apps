# File name: 
__name__ = 'WaterMe'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 27 July 2018
# Date last modified: 11 June 2023 Implemented 16 bit ADC reads
# Version 1.6
# MicroPython Version: 1.20 for the Kookaberry V4-06
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
# Moisture meter using the Gravity Soil Moisture Sensor which gives an analogue reading from 0 dry to 65535 wet
# or the Gravity Capacitive Moisture Sensor which gives an analogue reading which needs to be calibrated.
# The dry reading is 78% and the wet reading is 37% of full scale from the A/D converter
# together with a Gravity Switch Module that switches a separately supplied water pump on and off.
# The algorithm turns the pump on when the measured moisture is below the moist threshhold, and
# the relay off again when the moisture reaches the wet threshhold.
# A datalogging function has been added which is configured by the file Kappconfig.txt
# Logging is enabled/disabled by pressing the B button.
# The pump function is enabled/disabled by pressing the C button
# The sensor type is changed by pressing the D button subject to the signal being consistent with sensor type. The defult is a resistive sensor.
# A bar graph display with threshholds replaces the analogue needle display

# Begin code
# Initial conditions
import machine, kooka, fonts, time, math
from Kapputils import config    # utility to read the configuration file

s_plug = 'P4' # input port to use for the moisture sensor - change this to suit
r_plug = 'P2'    # output port for the relay module - change this to suit
sc_reading = 80 # set to 100 initially then reading with pins shorted - depends on the sensor supply voltage
s_gain = 100 / sc_reading
c_dry = 3177/4095*65535    # capacitive sensor dry reading (air)
c_wet = 1532/4095*65535    # capacitive sensor wet reading (water)
c_margin = 500  # margin for error (noise, cailbration etc)
c_gain = 1
t_moist = 25 # moist threshhold - change this to suit
t_wet = 50 # wet threshhold - change this to suit
condition = ['Dry', 'Moist', 'Wet']
r_status = ['Off', 'On']
s_type = ['Res','Cap']  # Sensor descriptors
p_type = 0  # Sensor pointer
sample_interval = 1    # interval at which the sensor is sampled

adc = machine.ADC(machine.Pin(s_plug))  # create the analogue input for the sensor
relay = machine.Pin(r_plug, machine.Pin.OUT)    # create the digital output for the relay
kooka.radio.disable()         # turn off bluetooth to save battery power

disp = kooka.display
relay.low() # switch the relay off to begin

# First select probe type - resistive or capacitive


# Prepare for datalogging
params = config('Kappconfig.txt')   # read the configuration file
interval = int(params['INTV'])      # use interval from the configuration file
fname = __name__ + '.csv'
f = open(fname,'w+')         # open a text file for writing
#f.write('Kookaberry Log for %s\n' % params['ID'])
f.write('Time,Moisture,Category,Sensor,Pump\n')   # write the heading line
f.close()
dur_timer = 0   # initialise the logging timer
sample_timer = 0    # the sample interval timer per configuration
intv_timer = 0  # initialise the interval timer
log_flag = 0    # used to switch logging on and off
relay_flag = 0    # used to enable the output switch


while not kooka.button_a.was_pressed():
    t0 = time.ticks_ms() # mark the time in ticks at the beginning of the loop
    if kooka.button_c.was_pressed(): relay_flag = not(relay_flag)
    if kooka.button_d.was_pressed(): p_type = not(p_type)
    if kooka.button_b.was_pressed(): log_flag = not(log_flag)
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Water Me', 0, 10)
    disp.setfont(fonts.mono6x7)
    if log_flag :  disp.text('Log @ %ds' % interval, 70, 10)
    else: disp.text('Log off', 70, 10)
    disp.text('X    Enbl  Sens  Log', 0, 63)
    disp.text('Sensor %s Pump %s' % (s_plug, r_plug), 0, 53)
    disp.text('S-%s' % s_type[p_type], 95, 26)
    if relay_flag: disp.text('P-%s' % r_status[relay.value()], 95, 40)
    else: disp.text('P-Dis', 95, 40)
    disp.setfont(fonts.mono8x13)
    if (sample_timer == 0):
        raw = adc.read_u16()    # read the analogue signal (0 to 4095 scale)
        if (raw < (c_wet-c_margin)) : p_type = 0   # improbable capacitive reading change to resistive
        if (raw > (c_dry+c_margin)) : p_type = 0   # improbable capacitive reading change to resistive
        if p_type == 0:
            moisture = raw / 65535 * 100 * s_gain # Convert raw to percentage scale
        if p_type == 1:
            moisture = (c_dry - raw) / (c_dry - c_wet) * 100 * c_gain   # Convert raw to percentage scale
        moisture = max(0, min(100, moisture))    # Limit the scale

# Categorise the moisture reading
        category = 0
        if moisture >= t_moist: category = 1
        if moisture >= t_wet: category = 2
# Display the reading as a percentage and the category
    disp.text('%.0f %%' % moisture, 50, 26)
    disp.text('%s' % condition[category], 50, 40)
# Display a bar chart with the treshholds marked
    r_width = 20
    r_height = 30
    r_x = 10
    r_y = 13
    disp.rect(r_x,r_y,r_width,r_height,1)    # outline rectangle
    # Display the lower threshhold line
    t_y = int(r_y + r_height - t_moist * r_height / 100)
    t_x1 = r_x - 5
    t_x2 = r_x + r_width + 5
    disp.line(t_x1 , t_y, t_x2 , t_y, 1)
    # Display the upper threshhold line
    t_y = int(r_y + r_height - t_wet * r_height / 100)
    t_x1 = r_x - 5
    t_x2 = r_x + r_width + 5
    disp.line(t_x1 , t_y, t_x2 , t_y, 1)
    # Display the measurement histogram line
    t_y = int(r_y + r_height - moisture * r_height / 100)
    t_h = int(moisture * r_height / 100)
    disp.fill_rect(r_x , t_y, r_width , t_h, 1)
    disp.show()
# Control the relay
    if (relay_flag and category == 0): relay.high()
    if (not(relay_flag) or category == 2): relay.low()
    if (category == 2): relay_flag = 0    # Disable the pump when wet is reached
# Control the sampling interval
    if (intv_timer == 0 and log_flag):   # write to file every interval if logging is on
        f = open(fname,'a+')         # open a text file for writing
        f.write('%d,%d,%s,%s,%s\n' % (dur_timer, moisture, condition[category],s_type[p_type],r_status[relay.value()]))
        f.close()   # Close to save from corruption by power interruptions
    t1 = time.ticks_ms() # mark the time in ticks after the loop work is done
    t_sleep = sample_interval * 1000 - time.ticks_diff(t1, t0)    #calculate how long before 1 second is up
    time.sleep_ms(t_sleep)
    dur_timer += sample_interval  # keep the timers ticking over
    intv_timer += sample_interval
    sample_timer += sample_interval
    if (sample_timer >= sample_interval):
        sample_timer = 0
    if (intv_timer >= interval):    # reset interval timer every interval
        intv_timer = 0

# Clean up and exit
f.close()
# Switch the relay off when exiting
relay.low()