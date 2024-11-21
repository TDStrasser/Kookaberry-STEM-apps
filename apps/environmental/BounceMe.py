# FILENAME: BounceMe.py
__name__ = 'BounceMe'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 13 November 2019
# DATE-MODIFIED: 5 July 2022 - improved multiple csv files for recordings
# VERSION: 1.3
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
#
# DESCRIPTION:
# Measures instantaneous acceleration using the Kookaberry's inbuilt accelerometer
# Captures data for a short period selectable on the screen and when Start is pressed.
# Buttons C and D adjust the logging period
# Long press on button B starts logging at the end of which the graph on the display is frozen to enable viewing.
# A short press on button B unfreezes the chart on the display.
# Logs instantaneous acceleration into a file at the full sample rate.
# Successive captures generate separate logging files
#------------------------------------------
# TAGS: #log #accelerometer #graph #sensor
# DEPENDENCIES:
# I/O ports and peripherals: No ports nor peripherals are used
# /lib files: kbtimer.mpy, Kapputils.mpy
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------
# BEGIN-CODE:
# Initial conditions

import machine, kooka, fonts, time, math, re, os
from Kapputils import config    # module to read the configuration file
import kbtimer    # long button press utility

b_timer = kbtimer.KBTimer(kooka.button_b, 1000) # instantiate a buttom B timer object

disp = kooka.display    # initialise the OLED display
params = config('Kookapp.cfg')   # read the configuration file
# turn off the radio to save power
kooka.radio.disable()
# Generate the Kookaberry's ID for the log file
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]

capture_no = 0    # used to track recording sessions
samples = 40
sarray = [0] * samples    # array of accelerometer data
parray = [0] * samples    # array for live plotting
carray = [0] * samples    # array for captured data plotting
plotx = 0
ploty = 12
ploth = 28
plotw = 80
plotxinc = int(plotw/samples)
plotymid = int(ploty + ploth/2)
plotrange = 15

bounce_time = 4    # duration of datalogging
bounce_min = 2
bounce_max = 20
bouncing = False    # Flag to indicate bounce in progress
freezeplot = False    # flag control freezing of plot display

acc_interval = 50    # milliseconds between acceleration samples

# Function to fetch a cleaned up list of files in the named directory
file_types = ['csv'] # Defines what ypes of files are listed
p = re.compile(r'\W+')     # regular expression to split strings into alphanumeric words

def listdir(dir):
    olist = []
    flist = os.listdir(dir)    # fetch the full list
    for i in range(0,len(flist)):    # examine each entry
        entry = p.split(flist[i],3)    # split the entry
        if len(entry) == 2 and len(entry[0]) > 0 and len(entry[1]) > 0:
            if entry[1].lower() in file_types:
                olist.append(flist[i])     # add to valid file list
    olist.sort()       
    return olist

# Search the Kookaberry for existing recordings and initialise session
csv_files = listdir('/') # find all csv files
#print(csv_files)
for file in csv_files:
    if __name__ in file:
        entry = p.split(file,3)    # split the entry
        capt_str = entry[0][len(__name__): ] #
        if capt_str.lstrip(' '):  # Decode the number from characters
            capt = int(capt_str)
            capture_no = max(capture_no, capt)
#            print(capture_no, capt)

# Set up the sampling timer
t_accel = time.ticks_ms()

while not kooka.button_a.was_pressed():
# write static screen parts
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('BounceMe %s' % (id), 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A(x) C(-) D(+) B+(Go)', 0, 60)
    if not freezeplot: disp.text('Live', 90, 50)
    else: disp.text('Frozen', 85, 50)
    if bouncing: disp.text('Rec#%d %d ms' % (capture_no,bounce_countdown), 0, 50)
    else: disp.text('Rec#%d %d secs' % (capture_no,bounce_time), 0, 50)
    
# Adjust the bounce parameters
    if kooka.button_c.was_pressed():    # decrease the bounce capture period
        bounce_time = max(bounce_min, bounce_time - 2)
    if kooka.button_d.was_pressed():    # increase the bounce capture period
        bounce_time = min(bounce_max, bounce_time + 2)
    if kooka.button_b.was_pressed() and not bouncing:    # Unfreezes the display
        freezeplot = False    # go back to live plotting
    if b_timer.isexpired() and not bouncing:     # long press on B starts the bounce capture period - disable to prevent false restarts
        bounce_countdown = bounce_time * 1000    # countdown timer in milliseconds
        capture_no += 1
        # set up the datalogging file
        fname = '%s%0.3d.csv' % (__name__, capture_no)
        f = open(fname,'w+')         # open a new text file for writing
        f.write('msecs,Acceleration m/sec^2\n')   # write the data headings line
        bouncing = True    # set flag for bounce capture
        cap_index = 0    # used for the capture array
        freezeplot = False    # go back to live plotting
        b_timer.reset()

    if time.ticks_diff(time.ticks_ms(), t_accel) >= 0:
        t_accel += acc_interval    # Set timer for next interval


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
    # capture bounce data
        if bouncing:
            if not freezeplot: carray[cap_index] = int(sample)
            cap_index += 1
            if cap_index >= samples: freezeplot = True    # freeze the graph
            f.write('%s,%s\n' % (bounce_time*1000 - bounce_countdown, accel))
            bounce_countdown -= acc_interval    # adjust capture countdown
            if bounce_countdown <= 0:    # capture interval elapsed
                bouncing = False    # reset capture flag
                b_timer.reset()    # reset any intervening long B presses
                freezeplot = True    # freeze the graph
                f.close()    # safely close file
    # Display the acceleration chart
        disp.rect(plotx,ploty,plotw,ploth+1,1)    # outline rectangle
        for i in range(0,samples-1):
            p1x = i*plotxinc+plotx
            p2x = (i+1)*plotxinc+plotx
            if not freezeplot:
                p1y = plotymid-int(parray[i]/plotrange*ploth)
                p2y = plotymid-int(parray[i+1]/plotrange*ploth)
            else:
                p1y = plotymid-int(carray[i]/plotrange*ploth)
                p2y = plotymid-int(carray[i+1]/plotrange*ploth)
            disp.line(p1x, p1y, p2x , p2y, 1)

    disp.show()

#    time.sleep_ms(acc_interval)    # Wait for the sensor read interval
# Clean up and exit
if bouncing: f.close()    # if the file is open, close it


