# File name: 
__name__ = 'Dimmer'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 4 December 2020
# Date last modified: 11 June 2023 - changed to ADC 16bit read
# Version 1.1
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
# Read an analogue signals (scale of 0 to 100) attached to P4
# Drives a PWM output (for a LED or a motor via a power stage) 
# in accordance with the input
# thereby emulating a dimmer or variable speed motor control.
# The abalogue value is displayed in a bar chart.
# Thecorresponding PWM waveform is displayed as a line graphic
# An option is provided to slow the PWM to illustrate flicker
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Analogue peripheral on P4
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: 
#------------------------------------------
# Begin code
# Initial conditions

import machine, kooka, fonts, time
from micropython import const

disp = kooka.display    # initialise the OLED display
# Set up the analogue bar chart parameters
bar_x = 6
bar_y = 10
bar_h = 30
bar_w = 10
# Set up the PWM waveform display parameters
pwm_x = 30
pwm_y = 10
pwm_h = 30
pwm_w = 90
# Set up the PWM waveform display
pwmd_x = [pwm_x, pwm_x, pwm_x, pwm_x, pwm_x + pwm_w, pwm_x + pwm_w]
pwmd_y = [pwm_y + pwm_h, pwm_y + pwm_h, pwm_y + pwm_h, pwm_y + pwm_h, pwm_y + pwm_h, pwm_y + pwm_h]

# Set up the inputs and outputs
input = 'P4'    # input ports
adc = machine.ADC(machine.Pin(input))  # create the analogue input for the sensor
signal = 0    # the measured signals
freqs = [16, 20, 30, 50, 100]
freq_ptr = len(freqs) - 1
output = 'P1'
pwmpin = machine.PWM(machine.Pin(output),freq = freqs[freq_ptr])

sens_interval = 50    # milliseconds between samples

_timer_sens = time.ticks_ms()    # initialise sample timer

while not kooka.button_a.was_pressed():
# Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono5x5)
    disp.text('In:%s Out:%s' % (input, output), 70, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 60)
    disp.text('B-freq', 70, 60)
# Adjust the PWM frequency via button B
    if kooka.button_b.was_pressed():
        freq_ptr += 1    # increment the pointer to the frequency array
        if freq_ptr >= len(freqs): freq_ptr = 0
        pwmpin.freq(freqs[freq_ptr])

# Get the analogue input and set the PWM output
    if time.ticks_diff(time.ticks_ms(), _timer_sens) >= 0:
        _timer_sens += sens_interval    # only take a sample every period
        signal = int(adc.read_u16() * 100 / 65535)    # Scale to 0-100
        pwmpin.duty(signal)    # Adjust the PWM duty cycle

# Prepare the analogue signal bar chart
    disp.setfont(fonts.mono6x7)
    disp.text('%2d' % signal, bar_x , 50) 
    disp.rect(bar_x, bar_y, bar_w, bar_h, 1)
    bar_signal = bar_h - int(signal*bar_h/100)
    disp.fill_rect(bar_x, bar_y + bar_signal , bar_w, bar_h - bar_signal, 1)
# Prepare the PWM waveform display
    disp.setfont(fonts.mono6x7)
    disp.text('PWM Freq %3dHz' % freqs[freq_ptr], pwm_x, 50) 
    pwmd_x[2] = pwmd_x[3] = pwm_x + int(signal * pwm_w / 100)
    if signal > 0: pwmd_y[1] = pwmd_y[2] = pwmd_y[5] = pwm_y
    else: pwmd_y[1] = pwmd_y[2] = pwmd_y[5] = pwm_y + pwm_h
    for i in range(0, len(pwmd_x)-1):
        disp.line(pwmd_x[i], pwmd_y[i], pwmd_x[i+1], pwmd_y[i+1], 1)
    disp.show()
# Disable PWM on exit
pwmpin.duty(0)
pwmpin.deinit()

