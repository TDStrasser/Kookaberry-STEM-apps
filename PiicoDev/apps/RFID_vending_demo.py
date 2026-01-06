# FILENAME: RFID_Vending_demo.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 22 July 2025
# DATE-MODIFIED: 
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
# Vending machine demonstrator using writeable RFID tags.
# Caution - do not use your important RFID tags with this script!
# Enhanced from basic code provided on
# https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/blob/main/examples/Expansion/vending_machine.py
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: P3 configured as I2C for the PiicoDev RFID tag reader
# P3 is connected to SCL (P3A) and SDA (P3B)
# /lib files: PiicoDev_RFID_Kookaberry.mpy
# /root files: none
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS: rfid, i2c
# BEGIN-CODE:

import kooka, fonts

from PiicoDev_RFID_Kookaberry import PiicoDev_RFID
from machine import Pin, SoftI2C
from time import sleep_ms

disp = kooka.display # The Kookaberry display object

def set_led(colour = 'off'): # Manipulates the LEDs more simply
    if colour == 'off':
        kooka.led_red.off()
        kooka.led_green.off()
        kooka.led_orange.off()
    elif colour == 'red':
        set_led('off')
        kooka.led_red.on()
    elif colour == 'green':
        set_led('off')
        kooka.led_green.on()
    elif colour == 'orange':
        set_led('off')
        kooka.led_orange.on()

set_led('off')

# Set up the I2C bus and RFID reader
i2c = SoftI2C(sda = Pin("P3B"), scl=Pin("P3A"))
rfid = PiicoDev_RFID(i2c)   # Initialise the RFID module at the default address (0x2c)

# Initialisations
price = 3 # dollars (whole dollars only)
item = 0 # pointer to item array - button C Prev / button D Next
credit_add = 20 # dollars
balance = 0
mode = 0 # Buy mode / 1 = Recharge credit - controlled by button B
modes = ["Add", "Buy"]
items = ["Show Balance","Apple","Banana","Sandwich","Juice","Water","Chips","Chocolate"]
prices = [0,2,2,4,3,1,2,4]

while not kooka.button_a.was_pressed():
    # Set up the static display elements
    disp.fill(0) # Clear the display
    disp.setfont(fonts.mono8x8)
    disp.text('RFID Vending', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-x  C<-  D->  B-%s' % modes[mode], 0, 63)
    # Control modes
    if kooka.button_b.was_pressed():
        mode = not mode
    if kooka.button_c.was_pressed():
        item -= 1
        if item < 0: item = len(items)-1
    if kooka.button_d.was_pressed():
        item += 1
        if item > len(items)-1: item = 0

    # Set up the dynamic display elements
    if mode == 0:
        if item == 0:
            disp.text('%s' % items[item], 0, 20)
        else:
            disp.text('Buy:',0,20)
            disp.text('%s - $%d' % (items[item],prices[item]), 6, 30)

    else:
        disp.text('Add credit: $%d' % credit_add, 0, 20)
        
    if rfid.tagPresent(): # if a tag is present
        balance = rfid.readNumber() # read the tag value
        
        if mode == 1: # Add credit mode
            new_balance = balance + credit_add
            rfid.writeNumber(new_balance) # Give credit to tag
            balance = new_balance
            set_led('orange')
            
        elif item > 0: # Buy mode
            price = prices[item] # The price of the selected item
            if balance < price: # Tag balance insufficient
                disp.text('                  ', 0, 50)
                disp.text('Insufficient funds', 0, 50)
                set_led('red')
            else: # Buy the item and reduce balance on the tag
                new_balance = balance - price
                rfid.writeNumber(new_balance) # Update balance on tag
                balance = new_balance
                set_led('green')
                disp.text('Success!', 0, 50)
        # Show the balance regardless of outcome
        disp.text('Balance = $%d' % balance, 0, 40)
                
        disp.show()
        # Wait for the user to remove the tag
        while rfid.tagPresent():
            sleep_ms(10)
        set_led('off')
    else:
        disp.text('Place tag on reader', 0, 50)
    
    disp.show()

# Exiting - clears the display
disp.fill(0)
disp.show()
