# FILENAME: WhatChances.py
__name__ = 'Chances'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 19 July 2022
# DATE-MODIFIED: 19 July 2022
# VERSION: 1.0
# SCRIPT: MicroPython Version: 1.12 for the Kookaberry V4-05
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
# An exercise in probability.  A circle is defined with 2 to 6 segments, each but the last segment with an adjustable angle.  
# Once defined, a randomised spinner can be spun multiple times and the frequency of landing on each segment recorded.
# A graph is shown of the frequency histogram contrasted with the theoretical probability distribution.
# The results can be saved to the 'Chances.csv' file on the Kookaberry.
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: None
# /lib files: shapes_lib.mpy is embedded in Kookaberry firmware
# /root files: None
# Other dependencies: None
# Complementary apps: GraphCSV
#------------------------------------------
# TAGS: #maths #probability #statistics
# BEGIN-CODE:
import kooka, math, fonts, random, machine, json
import shapes_lib

# Initial conditions
disp = kooka.display

# Mode display data
menus = ['C- Segs D+', 'C- Angl D+', '10 Spn 100 B-sav', '']
modes = ['Segs','Angl ','Spins ','']

# Control data
stage = 0
stage_max = len(modes)
min_segments = 2
max_segments = 10
circle_origin = [24,32]
circle_radius = 20
segments = min_segments
seg_angles = [360/segments] * segments
seg_ptr = 0
seg_res = 5    # resolution of segment angle
seg_chances = [100/segments] * segments
seg_counts = [0] * segments
chart_origin = [2*circle_origin[0]+15, circle_origin[1]-circle_radius]
chart_size = [123-chart_origin[0], 2*circle_radius]
spin_total = 0
spins = 0
v_scale = 1

# The main loop begins here
while not kooka.button_a.was_pressed():
    # Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text(modes[stage], 64, 6)
    disp.text('A-x %s B-nxt' % menus[stage], 0, 63)
    
    # Process the buttons and modes
    if kooka.button_b.was_pressed(): # Manage the stages
        if stage == 0:    # Set up to define angles
            seg_ptr = 0
            stage += 1
        elif stage == 1 and seg_ptr < segments-2:
            seg_ptr += 1
        else:
            stage += 1
            if stage >= stage_max: # Reset the statistics
                stage = 0
        
    if stage == 0:    # Define the number of segments
        update = False
        if kooka.button_d.was_pressed():    # increase segments
            segments = min(max_segments, segments + 1)
            update = True
        if kooka.button_c.was_pressed():    # decrease segments
            segments = max(min_segments, segments - 1)
            update = True
        if update: # Update the arrays and data
            while len(seg_angles) < segments:
                seg_angles.append(0)
                seg_chances.append(0)
                seg_counts.append(0)
            while len(seg_angles) > segments:
                seg_angles.pop(0)
                seg_chances.pop(0)
                seg_counts.pop(0)
            for i in range(segments):
                seg_angles[i] = round(360/segments,0)
                seg_chances[i] = round(100/segments,0)

        disp.text('%d' % segments, 98, 6)
        
    elif stage == 1:    # Update the segment angles
        update = False
        if kooka.button_d.was_pressed():    # increase segment angle
            update = True
            angle_preceding = 0
            for i in range(seg_ptr):
                angle_preceding += seg_angles[i]    # total angle so far
            angle_remaining = int((360 - angle_preceding) / seg_res)-(segments-seg_ptr)
            angle_quanta = int(seg_angles[seg_ptr] / seg_res)
            angle_quanta = min(angle_quanta+1, angle_remaining)
            seg_angles[seg_ptr] = int(seg_res * angle_quanta)
        if kooka.button_c.was_pressed():    # decrease segment angle
            update = True
            angle_preceding = 0
            for i in range(seg_ptr):
                angle_preceding += seg_angles[i]    # total angle so far
            angle_quanta = int(seg_angles[seg_ptr] / seg_res)
            angle_quanta = max(angle_quanta-1, 1)
            seg_angles[seg_ptr] = int(seg_res * angle_quanta)
            
        if update:    # if angle changed, update the remaining angles
            angle_preceding += seg_angles[seg_ptr]
            angle_distribution = round((360 - angle_preceding) / (segments -1 - seg_ptr), 0)
            for i in range(seg_ptr + 1, segments): # distribute the remaining angle
                seg_angles[i] = angle_distribution
            
            for i in range(segments):    # Calculate the theoretical probabilities
                seg_chances[i] = round(seg_angles[i]/3.6, 0)
                
        disp.text('%d:%d' % (seg_ptr+1, seg_angles[seg_ptr]), 94, 6)
        
    elif stage == 2:
        if spins == 0:    # Do the random spins (after current spins finish)
            if kooka.button_c.was_pressed():    # Do 10 spins
                spins = 10
            if kooka.button_d.was_pressed():    # Do 100 spins
                spins = 100
                
        disp.text('%d' % spin_total, 100, 6)
        
    elif stage == 3:    # Save data to file and reset
        f = open(__name__+'.csv', 'a+')
        f.write('Angles,'+json.dumps(seg_angles).strip('[').strip(']')+'\n')
        f.write('Probabilities,'+json.dumps(seg_chances).strip('[').strip(']')+'\n')
        f.write('Counts,'+json.dumps(seg_counts).strip('[').strip(']')+'\n')
        f.close()
        stage = 0
        spin_total = 0
        for i in range(segments):
            seg_counts[i] = 0

    # Draw the circle and segments
    shapes_lib.circle(disp,circle_origin[0],circle_origin[1],circle_radius,1)
    angle_total = 0
    for angle in seg_angles:
        angle_total += angle
        shapes_lib.line(disp,circle_origin[0],circle_origin[1],circle_radius,angle_total, 1)
    
    # Draw the probability distribution and counts
    disp.rect(chart_origin[0], chart_origin[1], chart_size[0], chart_size[1], 1)
    disp.line(chart_origin[0], chart_origin[1], chart_origin[0]+chart_size[0], chart_origin[1], 0)
    p_scale = 100 / max(seg_chances)    # Scale the probability distribution
    disp.setfont(fonts.mono5x5)
    disp.text('%d' % round(max(seg_chances),0), chart_origin[0]-11, chart_origin[1]+5, 1)
    disp.text('0', chart_origin[0]-6, chart_origin[1]+chart_size[1], 1)
    x_inc = int(chart_size[0] / segments)
    if max(seg_counts)/v_scale >= 100:    # rescale the counts chart
        v_scale += 1
    for i in range(segments): # Draw the theoretical property distribution and counts
        x = chart_origin[0]+ i * x_inc
        yt = int(chart_origin[1] + chart_size[1] - round(chart_size[1]/100*seg_chances[i]*p_scale, 0))
        yc = int(chart_origin[1]+chart_size[1]-round(chart_size[1]/100*(seg_counts[i]/v_scale), 0))
        disp.line(x, yt, x+x_inc, yt, 1) # draw the theoretical distributions
        disp.rect(x+2, yc, x_inc-2, int(chart_size[1]/100*seg_counts[i]/v_scale), 1)
    
    # Animate the spinning process
    if spins:    # Spins currently ordered
        spin_total += 1
        spins = max(0, spins-1)
        random_angle = random.randint(1,360)
        x,y = shapes_lib.line(disp,circle_origin[0],circle_origin[1],circle_radius-10,random_angle, 1)
        shapes_lib.fill_polygon(disp, x, y, 4, 3, random_angle, 1)
        angle_total = 0
        for i in range(segments):    # update the segment counts
            angle_total += seg_angles[i]
            if random_angle <= angle_total:    # if angle in current segment
                seg_counts[i] += 1
                break

    disp.show()
    machine.idle()

