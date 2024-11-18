## File name: Kapputils.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 26 July 2018
# Date last modified: 21 June 2020
# MicroPython Version: 1.9.4 for the Kookaberry
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
# Reads a Kookaberry configuration file and parses it into its elements
# Major update - now preference the new configuration format if present
# Otherwise uses the old format
# Begin code
import re, os, ujson

# Function to check whether a file exists
def fileExists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

# Function loads the Kookaberry apps configuration parameters
def config(filename):

#    filename = 'Kappconfig.txt'   # file contains configuration parameters for Kookaberry apps
#
# The parameters that are recognised are listed below. 
# Syntax is of the form "PARAM = Value", where:
#   PARAM   Value                   Format
#   NAME    First name of the user  Any character string
#   SURNAME Surname of the user     Any character string
#   LESSON  Lesson identifier       Any character string
#   DUR     Duration of datalogging Integer in seconds (must be bigger than INTV)
#   INTV    Datalogging interval    Integer in seconds
#   VAR1    Name of logged item 1   Any character string
#   VAR2    Name of logged item 2   Any character string
#   MAX1    Full scale of VAR1      Integer
#   MAX2    Full scale of VAR2      Integer
#   FILE    Log file name           Single word filename - will have .CSV appended
#   CHANNEL Integer 0 to 83         Radio channel used
#   BAUD    Integer 0 to 2          Speed of radio transmission 250kbps, 1Mbps, 2Mbps
#   POWER   Integer 0 to 7          Radio transmission power [-30, -20, -16, -12, -8, -4, 0, 4] dbmW       
#   Valid ranges are NOT checked so invalid values could crash the program using them
#   Anything else is ignored.
    params ={
        'NAME':'',
        'SURNAME':'',
        'LESSON':'',
        'DUR':'10',
        'INTV':'1',
        'VAR1':'Variable 1',
        'VAR2':'Variable 2',
        'FILE':'Kooklog',
        'MAX1':'100',
        'MAX2':'100',
        'CHANNEL':'7',
        'BAUD':'0',
        'POWER':'6'}
#   Set up the regular expression
    p = re.compile(r'\W+') # will split a string into substrings of words - non alphanumerics are ignored

# Function to check whether a file exists
    fname = 'Kookapp.cfg'
    if fileExists(fname):    # Test for the new JSON configuration file
        f = open(fname,'rt')
        fl =f.readline()    # Reads the first line
        params = ujson.loads(fl)    # Decode the JSON dictionary
        f.close()
        return params

#   Open the file for reading and read the contents
    else:
        f = open(filename,'rt')
        fl =f.readlines()
        for x in fl:
            s = p.split(x,2)        # splits off the parameter and the first word of the value
            s[0] = s[0].upper()
            if (s[0] in params):
                params[s[0].upper()]=s[1]   # update the parameter dictionary
#   Clean up the dictionary
            s = p.split(params['FILE']) # split filename into words
            params['FILE']=s[0]+'.CSV'  # append the .CSV file extension to the first word
    
        f.close()   # Close the configuration file
        return params