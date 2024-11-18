# File name: logger.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 26 Jun 2019
# Date last modified: 25 June 2020
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
# Module to set up and update a datalogging file
# Multiple instances of a datalogging file can exist 
# Usage:
    #    import logger
    #    logger.Dlog(file, interval, heading) # initialises the file and logging interval inerrupt
    #    logger.kill()		# stops the interrupt process
    #    logger.update(string)    # updates the string to be written to file
    #    logger.start()    # commence logging every interval
    #    logger.stop()    # stops logging
    #    logger.control()    # checks timing, control flag, and battery status to control datalogging - called by a timer interrupt - do not call
    #    logger.write()    # required every loop - appends the update string to the file
    
# Begin code
import machine, micropython
micropython.alloc_emergency_exception_buf(100)
class Dlog:
    def __init__(self, file, interval, heading):
        self.log_interval = int(interval)    # logging interval
        self.log_counter = self.log_interval    # Used to count down the logging interval
        self.log_flag = False    # indicates whether logging is active (True)
        self.log_write = False    # flag to initiate a logging write
        self.log_file = file	# the name of the logging file
        self.log_heading = heading    # logging file header string
        self.log_record = ' '*100    # the record that gets written to the file
        f = open(self.log_file,'w+')         # open a text file for writing
        f.write('%s\n' % self.log_heading)   # write the heading line
        f.close()
        self.timer = machine.Timer(-1, freq=1, callback=self.control)    # Set timer to 1 Hz
    
    def kill(self):
        self.timer.deinit()		# disables the timer and callback interrupt

    def update(self,record):
        self.log_record = record
    
    def start(self):
        self.log_flag = True
        self.log_counter = self.log_interval    # reset the interval counter
    
    def stop(self):
        self.log_flag = False
        self.log_counter = self.log_interval    # reset the interval counter

    def control(self,timer):
        if self.log_flag:
        	if self.log_counter > 0:
           		self.log_counter -= 1    # Count down the interval
		else:
           		self.log_write = True
           		self.log_counter = self.log_interval    # reset the interval counter
        else: pass
    
    def write(self):
        if self.log_write:
            f = open(self.log_file,'a+')         # open a text file for writing
            f.write('%s\n' % self.log_record)    # write the latest record
            f.close()
            self.log_write = False    # reset the write control flag
        else: pass



