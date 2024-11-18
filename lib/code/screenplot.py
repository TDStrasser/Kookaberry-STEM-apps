# File name: screenplot.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 25 September 2020
# Date last modified: 30 July 2023 - added autoscaling option
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
# Module that providesa set of plotting functions for drawing line trends on a Kookaberry display
# Multiple instances of plots and trends can exist 
# Usage:
    #    import screenplot
    #    screenplot.area(disp, x0, y0, width, height) # initialises the plot area in pixels. disp = framebuffer object
    #    screenplot.draw_area()    # clears the plot area and draws a border
    #    screenplot.trend()    # initialises a new trendline
    #    screenplot.scale(area, xmax, ymin, ymax)		# initialises the scale dimensions for the trend within the plot area given
    #    screenplot.value(value)    # appends the value to the trend data  
    #    screenplot.draw_trend(area, autoscale=False)    # draws the trend on the given area and optionally autoscales the y scale

#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: display framebuffer
# Complementary apps: Nil
#------------------------------------------

# Begin code

from gc import collect
class area:
    def __init__(self, disp, x0=0, y0=10, width=128, height=40):    # Initialises the display framebuffer area to be used
        self.disp = disp    # pointer to the framebuffer contining the display
        self.x0 = x0    # top left hand corner in pixels
        self.y0 = y0    
        self.width = width    # width in pixels
        self.height = height    # height in pixels
        self.xscale = 1    # default scale in pixels/unit
        self.yscale = 1
        self.xmax = width

        
    def draw_area(self):
        self.disp.fill_rect(self.x0, self.y0, self.width, self.height, 0)    # Erase the plot area
        self.disp.rect(self.x0, self.y0, self.width, self.height, 1)    # Draw a border
        
class trend():
    def __init__(self, area, xmax, ymin, ymax):
        self.xmax = xmax    # the number of data points to be kept
        self.ymin = ymin
        self.ymax = ymax
        self.xscale = area.width / xmax   # scale  of x in pixels / unit
        self.yscale = area.height / (ymax - ymin)    # scale of y in pixels/unit
        self.data = []    # initialise an empty trend array within the display

    def value(self, val):
        if len(self.data) > self.xmax: self.data.pop(0)    # Scroll data if exceeds width of plot area
        collect()
        self.data.append(val)
        collect()
        
    def draw_trend(self, area, autoscale = False):
        if autoscale: # Recalculate y scale based on minimum and maximum values collected
            data_max = max(self.data)
            data_min = min(self.data)
            scale_interval = 50
            new_ymax = (int(data_max / scale_interval) + 1) * scale_interval
            if data_min >= 0: new_ymin = int(data_min / scale_interval) * scale_interval
            else: new_ymin = (int(data_min / scale_interval) - 1) * scale_interval
            self.ymin = new_ymin
            self.ymax = new_ymax
            self.yscale = area.height / (new_ymax - new_ymin)    # scale of y in pixels/unit

        for i in range(1, len(self.data)):
            x1 = area.x0 + int((i-1)*self.xscale)
            y1 = min(max(self.data[i-1], self.ymin), self.ymax) - self.ymin
            y1 = area.y0 + area.height - int(y1*self.yscale)- 1
            x2 = area.x0 + int(i*self.xscale)
            y2 = min(max(self.data[i], self.ymin), self.ymax) - self.ymin
            y2 = area.y0 + area.height - int(y2*self.yscale) - 1
            area.disp.line(x1, y1, x2, y2, 1)
'''
# Test the code
from kooka import display
import gc, fonts
y = 0
ymax = 600
plot = area(display)
t1 = trend(plot,50,-10,ymax)
t2 = trend(plot,50,0,ymax+10)
last_mem = gc.mem_free()
print(gc.mem_free())
while True:
    display.fill(0)
    t1.value(y)
    t2.value(ymax-y)
    plot.draw_area()
    t1.draw_trend(plot, True)
    t2.draw_trend(plot, True)
    display.setfont(fonts.mono6x7)
    display.text('Y%d ymn%d ymx%d' % (y, min(t1.data), max(t1.data)), 0,63)
    display.show()
    y += 10
    if y > ymax: y= -100
    if gc.mem_free() != last_mem:
        last_mem = gc.mem_free()
        print(last_mem)
'''
