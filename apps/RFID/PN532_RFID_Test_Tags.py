# FILENAME: PN532_RFID_Test_Tags.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 22 July 2025
# DATE-MODIFIED: 26 February 2026 - adapted for PN532 RFID Reader
# Version 1.0
# SCRIPT: MicroPython Version: 1.24 for the Kookaberry with Pico RP2040 / RP2350
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
# Test script for writeable RFID tags.
# Caution - do not use your important RFID tags with this script!
# Interface is only on the REPL console.
# Modify the Operating Mode variable below to modify the scripts behaviour:
#   0=read only, 1=write number, 2=write text, 3=write URI
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: P3 configured as I2C for the RFID tag reader
# P3 is connected to SCL (P3A) and SDA (P3B)
# /lib files: PN532.mpy
# /root files: none
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS: rfid, i2c
# BEGIN-CODE:
from pn532 import PN532
import machine, kooka
from machine import Pin, SoftI2C
from time import sleep_ms

# First set up the I2C bus
i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))

# Then instantiate the RFID reader using the I2C bus
rfid=PN532(bus=i2c)

# Test data
tag_slot = 2
number_to_write = 99
text_to_write = 'Kookaberry!'
URI_to_write = 'https://auststem.com.au'

#### Operating Mode ####
write_mode = 3 # Change this to switch what will be attempted: 0=read only, 1=write number, 2=write text, 3=write URI
########################

print('Place tag near RFID module\n')

while True: # Runs forever
    if rfid.tagPresent():    # if an RFID tag is present
        # In the following the parameter detail is False by default and True if selected
        # if detail is False then only the tag's identification number is returned formatted as a hex string
        # if detail is True then the tag type, success flag, and id numbers (formatted and unformatted) are returned in a structured array
        id=rfid.readID(detail=True)     # get the detailed tag information
        print(id) # print the id information on the REPL console
        
        # If a classic tag, read the data contained in the write slots as long as the tag is next to the reader
        if id['type'] == 'classic' and write_mode == 1: # only write if correct mode is selected
            print('Classic tag present - writing', number_to_write,'in slot',tag_slot)
            rfid.writeNumber(number_to_write, tag_slot)
        
        if id['type'] == 'classic': # Read the classic tag regardless of mode
            print('Reading all slots while Classic tag is present')
            slot = 0
            while rfid.tagPresent() and slot <= 35:
                print('Slot',slot,'contains',hex(rfid.readNumber(slot)))
                slot += 1
            
    # For any tag type, read the text on it
    if rfid.tagPresent():
        print('Read tag text:',rfid.readText())
            
    # Attempt to write text to tag
    if rfid.tagPresent() and write_mode == 2:
        print('Writing tag text:',text_to_write,rfid.writeText(text_to_write))

    # Attempt to write URI to tag
    if rfid.tagPresent() and write_mode == 3:
        print('Writing URI:',URI_to_write,rfid.writeURI(URI_to_write))
            
    sleep_ms(100)
        
        