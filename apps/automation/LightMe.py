# File name: 
__name__ = 'LightMe'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 25 July 2018
# Date last modified: 4 December 2023 - update to adc.read_u16() function
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
# Ambient light meter using the Gravity Analogue Ambient Light Sensor which gives an analogue reading 
# from 0 dark to 4095 bright - allegedly 600 Lux
# together with a LED Module or MOSFET that switches a separately supplied light on and off.
# The algorithm switches the relay on when the measured light is below the dark threshhold, and
# the relay off again when the ambient light reaches the bright threshhold. 
# Care needs to be taken that any light controlled by the relay doesn't bleed into the sensor or the light output will chatter.
# A datalogging function has been added which is configured by the file Kookapp.cfg
# The display now shows a histogram of the measured light with threhhold bars that can be adjusted down and up by the C and D keys respectively.  The dark threshhold is set at 50% of the bright threshhold.
# A lightbulbicon was added to show when the light output is activated.
# December 2020 - updated to more efficient and smoother timing

# Initial conditions
import machine, kooka, fonts, time, framebuf
from Kapputils import config    # utility to read the configuration file
import logger

s_plug = 'P4' # input port to use for the light sensor - change this to suit
r_plug = 'P2'    # output port for the relay module - change this to suit
sc_reading = 100 # set to 100 initially then reading with pins shorted - depends on the sensor supply voltage
gain = 100 / sc_reading
t_light = 50 # bright threshhold - change this to suit
t_dark = int(t_light / 2)  # dark threshhold
condition = ['Dark', 'Dim', 'Bright']
r_status = ['Off', 'On']
sens_interval = 100    # milliseconds between samples
_timer_sens = time.ticks_ms()    # initialise sample timer

adc = machine.ADC(machine.Pin(s_plug))  # create the analogue input for the sensor
relay = machine.Pin(r_plug, machine.Pin.OUT)    # create the digital output for the relay
kooka.radio.disable()         # turn off bluetooth to save battery power
# Create a light bulb icon
bitmap = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x38, 0x70, 0x00, 0x00, 0x80, 0x80, 0x8E, 0x9E, 0x8E,
0x80, 0x80, 0x00, 0x00, 0x70, 0x38, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x06,
0x0E, 0x0C, 0x0C, 0x00, 0xF8, 0xFC, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
0xFE, 0xFC, 0xF8, 0x00, 0x0C, 0x0C, 0x0E, 0x06, 0x04, 0x00, 0x00, 0x00, 0x06, 0x06, 0x03, 0x02,
0x80, 0xC1, 0xE7, 0x4F, 0x3F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x1F, 0x4F, 0xE7, 0xC1,
0x80, 0x02, 0x03, 0x06, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00,
0x00, 0x00, 0x25, 0x2D, 0x6D, 0xED, 0x6D, 0x2D, 0x05, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

bulb = framebuf.FrameBuffer(bitmap, 29, 32, framebuf.MONO_VLSB)

disp = kooka.display
params = config('Kookapp.cfg')   # read the configuration file
interval = int(params['INTV'])      # use interval from the configuration file
fname = __name__ + '.csv'        # The name of the log file
# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Timer,Light %,Threshhold %,Switch %' )    # Create the datalogger instance
dlog.start()    # Start the datalogger

_time_zero = time.ticks_ms()   # initialise the logging duration timer

relay.low() # switch the relay off to begin

while not kooka.button_a.was_pressed():
    timer_run = int(time.ticks_diff(time.ticks_ms(), _time_zero) / 1000) # seconds since beginning
    timestr = '%0.2d:%0.2d:%0.2d'% (int(timer_run/3600),int((timer_run/60)%60), int(timer_run%60))
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 10)
    disp.setfont(fonts.mono5x5)
    disp.text('In:%s Out:%s' % (s_plug, r_plug), 74, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 63)
    disp.text('C-Dn  D-Up', 50, 63)
    disp.text('Run:%s' % timestr, 0, 54)
    disp.text('Log:%d' % dlog.log_counter, 80, 54)
    if relay.value(): disp.blit(bulb, 6, 14)
# Adjust the lighting threshhold using the C and D keys
    if kooka.button_c.was_pressed():
        if t_light >= 15: t_light -= 5    # decrement bright threshhold
        t_dark = int(t_light / 2)
    if kooka.button_d.was_pressed():
        if t_light <= 85: t_light += 5    # increment bright threshhold
        t_dark = int(t_light / 2)
        
# Read and process the ambient light sensor
    disp.setfont(fonts.mono8x13)
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        light = adc.read_u16() / 65535 * 100 * gain #Convert raw ADC to percentage scale
# Categorise the light reading
        category = 0
        if light >= t_dark: category = 1
        if light >= t_light: category = 2
# Control the relay
        if category == 0: relay.high()
        if category == 2: relay.low()
# Update the datalogger
        dlog.update('%s,%d,%d,%d' % (timestr, light, t_light,relay.value()*100))    # update the string to be logged
        dlog.write()    # writes the datalogger string when next due

# Display the reading as a percentage and the category
    disp.text('%.0f %%' % light, 45, 24)
    disp.text('%s' % condition[category], 45, 38)
# Display a bar chart with the treshholds marked
    r_width = 10
    r_height = 30
    r_x = 100
    r_y = 10
    disp.rect(r_x,r_y,r_width,r_height,1)    # outline rectangle
    # Display the dark threshhold line
    t_y = int(r_y + r_height - t_dark * r_height / 100)
    t_x1 = r_x - 5
    t_x2 = r_x + r_width + 5
    disp.line(t_x1 , t_y, t_x2 , t_y, 1)
    # Display the light threshhold line
    t_y = int(r_y + r_height - t_light * r_height / 100)
    t_x1 = r_x - 5
    t_x2 = r_x + r_width + 5
    disp.line(t_x1 , t_y, t_x2 , t_y, 1)
    # Display the light measurement histogram line
    t_y = int(r_y + r_height - light * r_height / 100)
    t_h = int(light * r_height / 100)
    disp.fill_rect(r_x , t_y, r_width , t_h, 1)
    disp.show()

# Clean up and exit
dlog.kill()    # disables the datalogger
relay.low()