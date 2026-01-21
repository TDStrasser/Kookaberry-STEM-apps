from PiicoDev_RFID_Kookaberry import PiicoDev_RFID
import machine, kooka
from machine import Pin, SoftI2C
from time import sleep_ms

# First set up the I2C bus
i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))
# Then instantiate the RFID reader using the I2C bus
rfid=PiicoDev_RFID(bus=i2c)
# Test data
tag_slot = 1
number_to_write = 99
text_to_write = 'Kookaberry!'
URI_to_write = 'https://auststem.com.au'
write_mode = 3 # Change this to switch what will be attempted: 0=read only, 1=write number, 2=write text, 3=write URI

print('Place tag near PiicoDev RFID module\n')

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
        
        