# File name: Compass.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 28 July 2018
# Date last modified: 5 December 2020
# Version 1.2
# MicroPython Version: 1.12 for the Kookaberry V4-06
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
# Description
# Compass using the Kookaberry's inbuilt magnetometer.
# The compass needle points to magnetic North 
# The accelerometer drives a set of cross hairs that should be kept over the compass axis.
# The GREEN LED will show when the compass is level.
# A "Level!" warning and RED LED is shown if the Kookaberry is not level 
# The Kookaberry's heading is shown in degrees as is the general heading
# The B button moves the Kookaberry to a calibration mode. The ORANGE LED shows.
# To calibrate rotate the Kookaberry through 360 degrees while level
# When calibration is complete (shown by a full circle) the app returns to compass mode
# Pre-requisites: None - standalone app

# Begin code
import time, kooka, math, fonts
hstr = ['N','NE','NE','E','E','SE','SE','S','S','SW','SW','W','W','NW','NW','N']
compass_radius = 22    # radius of compass dial
compass_points = 8    # number of points on the compass dial
compass_ticks = 18    # radius of the points on the dial
mag_cal = [0,0,0]    # magnetometer calibration values
mag_mins = [0,0,0]
mag_maxs = [0,0,0]
cal_points = [False]*5
calibrated = False    # status of calibration
modes = ['Calib','Comp']
mode_ptr = 0
level = False

disp = kooka.display
# Routine to draw an arc specified in degrees
def drawarc(x,y,r,arcstart,arcstop): 
    arcinc = 5    # increment of arc to be draw in degrees
    arclen = abs(arcstop-arcstart)
    lines = int(arclen/arcinc)
    for i in range(0,lines):
        angle1 = (arcstart + i*arcinc)/180 * math.pi
        angle2 = (arcstart + (i+1)*arcinc)/180 * math.pi
        x1 = x + int(r * math.sin(angle1))
        y1 = y - int(r * math.cos(angle1))
        x2 = x + int(r * math.sin(angle2))
        y2 = y - int(r * math.cos(angle2))
        disp.line(x1, y1, x2 , y2, 1)
#        print(x1, y1, x2 , y2, 1)
    return
while not kooka.button_a.was_pressed():
    headingxyz = kooka.compass.get_xyz()
    heading = math.atan2(headingxyz[1]-mag_cal[1], headingxyz[0]-mag_cal[0])
    degrees = heading*180/math.pi+180
    if degrees >= 360: degrees = 0
    hcase = int(degrees / 22.5)
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text("Compass", 0, 6)
    disp.text('X', 0, 60)
    disp.text('%s' % modes[mode_ptr], 88, 60)
    disp.text("%d" % degrees, 0, 30)
    disp.text("deg", 0, 40)
    if level: 
        kooka.led_green.on()
        kooka.led_red.off()
    if not level: 
        disp.text('Level!', 80, 6)
        kooka.led_green.off()
        kooka.led_red.on()
        
    if mode_ptr == 0:    # normal compass mode
# Display the compass needle and heading
        kooka.led_orange.off()
        disp.text("%s" % hstr[hcase], 100, 35)
        tipx = int(compass_radius * math.sin(-heading))
        tipy = int(compass_radius * math.cos(-heading))
        disp.line(64, 32, 64 - tipx, 32 + tipy, 1)
    elif mode_ptr == 1:    # compass calibration mode
        kooka.led_orange.on()
        disp.setfont(fonts.mono5x5)
        disp.text('Rotate', 90,20)
        disp.text('compass', 90,30)
        disp.text('level', 90,40)
        # check we are covering the rotation while level
        if level:
            if degrees < 15: cal_points[0] = True
            elif degrees > 80 and degrees < 100: cal_points[1] = True
            elif degrees > 170 and degrees < 190: cal_points[2] = True
            elif degrees > 215 and degrees < 235: cal_points[3] = True
            elif degrees > 350: cal_points[4] = True
            finished = True
            for i in range(0,len(headingxyz)):
                mag_mins[i] = min(mag_mins[i],headingxyz[i])
                mag_maxs[i] = max(mag_maxs[i],headingxyz[i])
                finished = finished and cal_points[i]
            calibrated = finished
        if calibrated:
            for i in range(0,len(mag_cal)): mag_cal[i] = (mag_maxs[i] + mag_mins[i])/2
            mode_ptr = 0
        if cal_points[0]: drawarc(64,32,compass_radius,0,45)
        if cal_points[1]: drawarc(64,32,compass_radius,45,135)
        if cal_points[2]: drawarc(64,32,compass_radius,135,225)
        if cal_points[3]: drawarc(64,32,compass_radius,225,315)
        if cal_points[4]: drawarc(64,32,compass_radius,315,360)
# Draw the compass points
    for b in range(0, compass_points):
        a = math.pi / 4 * b
        a1x = int(compass_radius * math.sin(a)) +64
        a1y = int(compass_radius * math.cos(a)) +32
        a2x = int(compass_ticks * math.sin(a)) +64
        a2y = int(compass_ticks * math.cos(a)) +32
        disp.line(a1x,a1y,a2x,a2y,1)
# Obtain and display Kookaberry orientation to get level
    x, y, z = kooka.accel.get_xyz()
    x = min(1, max(-1, x / 9.8))
    y = min(1, max(-1, y / 9.8))
    u = 64 - int(y * 64)
    v = 32 - int(x * 32)
    level = abs(x) <= 0.1 and abs(y) <= 0.1
    disp.line(u - 5, v, u + 5, v, 1)
    disp.line(u, v - 5, u, v + 5, 1)
    disp.show()
# Control the mode of the compass
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        if mode_ptr > len(modes)-1: mode_ptr = 0
        if mode_ptr == 1: 
            cal_points = [False]*5
            calibrated = False    # status of calibration
            mag_mins = [0,0,0]
            mag_maxs = [0,0,0]
    time.sleep_ms(20)
# Exit cleanly
kooka.led_green.off()
kooka.led_orange.off()
kooka.led_red.off()
disp.fill(0)
disp.show()



