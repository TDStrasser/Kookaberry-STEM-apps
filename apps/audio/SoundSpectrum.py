# File name: 
__name__ = 'SoundSpectrum'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 9 May 2020
# Date last modified: 11 June 2020
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
# Measures the speech audio spectrum using an analogue microphone plugged into P5
# It continuously samples and accumulates the power spectrum whenever sufficient audio signal is detected
# It finishes sampling when the A button is pressed and finalises the spectrum
# It logs the spectrum into SoundSpectrum.csv when complete
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: analogue microphone sensor plugged into P5
# /lib files: goertzel.mpy
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: GraphCSV.py produces a html graph from the csv file
#------------------------------------------
# Begin code

import math, machine, time, kooka, fonts, array
import goertzel    # simplified spectrum analysis
    
# Main code starts here

# set up for collecting samples
audio_pin = 'P5'
freq_min = 40    # starting frequency
freq_max = 4000    # ending frequency
freq_res = 40    # spectrum resolution
freq_bins = int(math.ceil((freq_max - freq_min) / freq_res))
sample_rate = int(freq_max * 2)    # Nyquist criterion
samples = int(sample_rate / freq_res)    # required length of sample buffer
sample_buf = array.array('H', 0 for _ in range(samples)) # unsigned 16 bit integers
adc = machine.ADC(audio_pin)
#
sample_ctr = 0    # The number of samples taken
silence_timeout = 60000
spectrum = [0]*freq_bins    # array for the accumulated spectral power
disp_spectrum = [0]*freq_bins    # used for displaying the spectrum
# Spectrum display parameters
plot_x = 10
plot_y = 20
plot_w = 100
plot_h = 25

disp = kooka.display    # initialise the OLED display

_timer_silence = time.ticks_ms()    # timer used for delays
silence_threshhold = 0.1    # threshhold above which sound is captured

while not kooka.button_a.was_pressed() and not time.ticks_diff(time.ticks_ms(), _timer_silence) >= silence_timeout:
# Sample the audio every sampling period
    disp.fill(0)
    disp.setfont(fonts.mono5x5)
    disp.text('%d' % freq_min, (plot_x-6), (plot_y+plot_h+6))
    disp.text('%d' % freq_max, (plot_x+plot_w-12), (plot_y+plot_h+6))
    disp.setfont(fonts.mono6x7)
    disp.text('%s I:%s' % (__name__,audio_pin), 0, 6)
    disp.text('A-exit', 0, 60)
    disp.text('Samples: %d' % sample_ctr, 0, 16)
    kooka.read_timed(adc, sample_buf, sample_rate)
    sil_t = sum(sample_buf)/len(sample_buf) * (1 + silence_threshhold)    #adaptive threshhold as bias on analogue input may vary
    if max(sample_buf) > sil_t:    # Sound detected
# Calculate the spectrum
        sample_ctr += 1    #Count the samples taken
        disp.text('Sample', 80,16)
        freqs, powers = goertzel.goertzel(sample_buf, sample_rate, (freq_min, freq_max))
        for i in range(0, len(powers)):    # totalise the power spectrum
            spectrum[i] = powers[i]
        _timer_silence = time.ticks_ms()  # reset the silence waiting period
    else: # No sound detected
        disp.text('W %d/%d' % (time.ticks_diff(time.ticks_ms(), _timer_silence)/1000,silence_timeout/1000), 80,16)
# Display the spectrum progressively
    disp.rect(plot_x,plot_y,plot_w,plot_h+1,1)    # outline rectangle
    if sample_ctr > 0:    #only if samples exist
        spectrum_scale = max(spectrum) / 100    # factor used to normalise the spectr
        for i in range(0,freq_bins):
            disp_spectrum[i] = spectrum[i] / spectrum_scale
            x = int(freqs[i]/freq_res) + plot_x
            h = int(disp_spectrum[i]/4)
            y = plot_y + plot_h - h
            disp.vline(x,y,h, 1)
        disp.text('Max:%.0fHz' % freqs[disp_spectrum.index(max(disp_spectrum))], 50, 60)
    disp.show()

# Program exit and cleanup
if sample_ctr > 0:    # Only if samples taken
    spectrum_scale = max(spectrum) / 100    # factor used to normalise the spectrum in range 0 to 100
# Write out the file and draw the spectrum on screen
# Bubble sort the frequency and spectrumarrays in synch
    n = len(freqs)
    for i in range(n-1): 
    # range(n) also work but outer loop will repeat one time more than needed. 
    # Last i elements are already in place 
        for j in range(0, n-i-1): 
        # traverse the array from 0 to n-i-1 
        # Swap if the element found is greater than the next element 
            if freqs[j] > freqs[j+1] : 
                freqs[j], freqs[j+1] = freqs[j+1], freqs[j] 
                spectrum[j], spectrum[j+1] = spectrum[j+1], spectrum[j] 
    f = open(__name__+'.csv','w+')
    f.write('Frequency,Power\n')
    for i in range(0,len(freqs)):
        spectrum[i] = spectrum[i] / spectrum_scale
        f.write('%.1f,%.2f\n' % (freqs[i],spectrum[i]))
    f.close()
#time.sleep(10)    # leave the display on for this time before exiting.
# End





