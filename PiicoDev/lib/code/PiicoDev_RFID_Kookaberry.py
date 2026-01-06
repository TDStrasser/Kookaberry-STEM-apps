# FILENAME: PiicoDev_RFID_Kookaberry.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 15 July 2025
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE:
'''
Copyright 2020 Core Electronics Pty Ltd and 2025 The AustSTEM Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
#
# DESCRIPTION:
# Library module to use the PiicoDev RFID Reader/Writer
# Based on the PiicoDev libraries from Core Electronics which in turn were based on:
# https://github.com/semaf/MFRC522_I2C_Library
# https://github.com/wendlers/micropython-mfrc522
# https://github.com/mxgxw/MFRC522-python
#
# Usage: https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/blob/main/README.md
# Differences: No dependency on the PiicoDev Unified Library - uses Kookaberry MicroPython firmware
'''
# Example of basic tag read
from PiicoDev_RFID_Kookaberry import PiicoDev_RFID
from machine import Pin, SoftI2C
from time import sleep_ms

i2c = softI2C(sda = Pin("P3B"), scl=Pin("P3A"))
rfid = PiicoDev_RFID(i2c)   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print('')

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readId()   # get the id
        print(id)            # print the id

    sleep_ms(100)
'''
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: PiicoDev RFID module connected to any I2C capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

from time import sleep_ms

_I2C_ADDRESS        = 0x2C

_REG_COMMAND        = 0x01
_REG_COM_I_EN       = 0x02
_REG_DIV_I_EN       = 0x03
_REG_COM_IRQ        = 0x04
_REG_DIV_IRQ        = 0x05
_REG_ERROR          = 0x06
_REG_STATUS_1       = 0x07
_REG_STATUS_2       = 0x08
_REG_FIFO_DATA      = 0x09
_REG_FIFO_LEVEL     = 0x0A
_REG_CONTROL        = 0x0C
_REG_BIT_FRAMING    = 0x0D
_REG_MODE           = 0x11
_REG_TX_CONTROL     = 0x14
_REG_TX_ASK         = 0x15
_REG_CRC_RESULT_MSB = 0x21
_REG_CRC_RESULT_LSB = 0x22
_REG_T_MODE         = 0x2A
_REG_T_PRESCALER    = 0x2B
_REG_T_RELOAD_HI    = 0x2C
_REG_T_RELOAD_LO    = 0x2D
_REG_AUTO_TEST      = 0x36
_REG_VERSION        = 0x37
_CMD_IDLE           = 0x00
_CMD_CALC_CRC       = 0x03
_CMD_TRANCEIVE      = 0x0C
_CMD_MF_AUTHENT     = 0x0E
_CMD_SOFT_RESET     = 0x0F

# RFID Tag (Proximity Integrated Circuit Card)
_TAG_CMD_REQIDL  = 0x26
_TAG_CMD_REQALL  = 0x52
_TAG_CMD_ANTCOL1 = 0x93
_TAG_CMD_ANTCOL2 = 0x95
_TAG_CMD_ANTCOL3 = 0x97

# Classic
_TAG_AUTH_KEY_A = 0x60
_CLASSIC_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

#-----Used for Write Functionality------------
    
import struct
from time import ticks_ms as now

_REG_STATUS_2   = 0x08
_CMD_TRANCEIVE  = 0x0C
_CMD_MF_AUTHENT = 0x0E


# RFID Tag (Proximity Integrated Circuit Card)
_TAG_CMD_REQIDL  = 0x26

# NTAG
_NTAG_NO_BYTES_PER_PAGE = 4
_NTAG_PAGE_ADR_MIN = 4 # user memory is 4 to 39 for NTAG213 so that allows for 144 characters.  So that's 36 pages
_NTAG_PAGE_ADR_MAX = 39

# Classic
_TAG_AUTH_KEY_A = 0x60
_CLASSIC_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
_CLASSIC_NO_BYTES_PER_REG = 16
_CLASSIC_ADR = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42, 44, 45, 46, 48]

# PiicoDev Merge NTAG & Classic
_SLOT_NO_MIN = 0
_SLOT_NO_MAX = 35

#----------------------------------------------

class PiicoDev_RFID(object):
    OK = 1
    NOTAGERR = 2
    ERR = 3

    def __init__(self, bus=None, address=_I2C_ADDRESS, asw=None): # I2C is instantiated by the caller and passed as an argument

        self.i2c = bus
        
        if type(asw) is list: # determine address from ASW switch positions (if provided)
            assert max(asw) <= 1 and min(asw) >= 0 and len(asw) is 2, "asw must be a list of 1/0, length=2"
            self.address=_I2C_ADDRESS+asw[0]+2*asw[1]
        else:
            self.address = address # fall back on using address argument
            
        self._tag_present = False
        self._read_tag_id_success = False
        self.reset()
        sleep_ms(50)
        self._wreg(_REG_T_MODE, 0x80)
        self._wreg(_REG_T_PRESCALER, 0xA9)
        self._wreg(_REG_T_RELOAD_HI, 0x03)
        self._wreg(_REG_T_RELOAD_LO, 0xE8)
        self._wreg(_REG_TX_ASK, 0x40)
        self._wreg(_REG_MODE, 0x3D)
        self._wreg(_REG_DIV_I_EN, 0x80) # CMOS Logic for IRQ pin
        self._wreg(_REG_COM_I_EN, 0x20) # allows the receiver interrupt request (RxIRq bit) to be propagated to pin IRQ
        self.antennaOn()
    
    # I2C write to register
    def _wreg(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    # I2C write to FIFO buffer
    def _wfifo(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes(val))

    # I2C read from register
    def _rreg(self, reg):
        val = self.i2c.readfrom_mem(self.address, reg, 1)
        return val[0]
    
    # Set register flags
    def _sflags(self, reg, mask):
        current_value = self._rreg(reg)
        self._wreg(reg, current_value | mask)

    # Clear register flags
    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    # Communicates with the tag
    def _tocard(self, cmd, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        if cmd == _CMD_MF_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == _CMD_TRANCEIVE:
            irq_en = 0x77
            wait_irq = 0x30
        self._wreg(_REG_COMMAND, _CMD_IDLE)      # Stop any active command.
        self._wreg(_REG_COM_IRQ, 0x7F)           # Clear all seven interrupt request bits
        self._sflags(_REG_FIFO_LEVEL, 0x80)      # FlushBuffer = 1, FIFO initialization
        self._wfifo(_REG_FIFO_DATA, send)        # Write to the FIFO
        if cmd == _CMD_TRANCEIVE:
            self._sflags(_REG_BIT_FRAMING, 0x00) # This starts the transceive operation
        self._wreg(_REG_COMMAND, cmd)
        if cmd == _CMD_TRANCEIVE:
            self._sflags(_REG_BIT_FRAMING, 0x80) # This starts the transceive operation

        i = 20000  #2000
        while True:
            n = self._rreg(_REG_COM_IRQ)
            i -= 1
            if n & wait_irq:
                break
            if n & 0x01:
                break
            if i == 0:
                break
        self._cflags(_REG_BIT_FRAMING, 0x80)
        
        if i:
            if (self._rreg(_REG_ERROR) & 0x1B) == 0x00:
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == _CMD_TRANCEIVE:
                    n = self._rreg(_REG_FIFO_LEVEL)
                    lbits = self._rreg(_REG_CONTROL) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(_REG_FIFO_DATA))
            else:
                stat = self.ERR
        return stat, recv, bits

    # Use the co-processor on the RFID module to obtain CRC
    def _crc(self, data):
        self._wreg(_REG_COMMAND, _CMD_IDLE)
        self._cflags(_REG_DIV_IRQ, 0x04)
        self._sflags(_REG_FIFO_LEVEL, 0x80)

        for c in data:
            self._wreg(_REG_FIFO_DATA, c)
        self._wreg(_REG_COMMAND, _CMD_CALC_CRC)

        i = 0xFF
        while True:
            n = self._rreg(_REG_DIV_IRQ)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        self._wreg(_REG_COMMAND, _CMD_IDLE)
        return [self._rreg(_REG_CRC_RESULT_LSB), self._rreg(_REG_CRC_RESULT_MSB)]
    
    # Invites tag in state IDLE to go to READY
    def _request(self, mode):
        self._wreg(_REG_BIT_FRAMING, 0x07)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, [mode])
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR
        return stat, bits

    # Perform anticollision check
    def _anticoll(self, anticolN=_TAG_CMD_ANTCOL1):
        ser_chk = 0
        ser = [anticolN, 0x20]

        self._wreg(_REG_BIT_FRAMING, 0x00)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, ser)
        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR
        return stat, recv
    
    # Select the desired tag
    def _selectTag(self, serNum,anticolN):
        backData = []
        buf = []
        buf.append(anticolN)
        buf.append(0x70)
        for i in serNum:
            buf.append(i)
        pOut = self._crc(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self._tocard( 0x0C, buf)
        if (status == self.OK) and (backLen == 0x18):
            return  1
        else:
            return 0
    
    # Returns detailed information about the tag 
    def _readTagID(self):
        result = {'success':False, 'id_integers':[], 'id_formatted':'', 'type':''}
        valid_uid=[]
        (status,uid)= self._anticoll(_TAG_CMD_ANTCOL1)
        if status != self.OK:
            return result
        
        if self._selectTag(uid,_TAG_CMD_ANTCOL1) == 0:
            return result
        
        if uid[0] == 0x88 : # NTAG
            valid_uid.extend(uid[1:4])
            (status,uid)=self._anticoll(_TAG_CMD_ANTCOL2)
            if status != self.OK:
                return result
            rtn =  self._selectTag(uid,_TAG_CMD_ANTCOL2)
            if rtn == 0:
                return result
            #now check again if uid[0] is 0x88
            if uid[0] == 0x88 :
                valid_uid.extend(uid[1:4])
                (status , uid) = self._anticoll(_TAG_CMD_ANTCOL3)
                if status != self.OK:
                    return result
        valid_uid.extend(uid[0:5])
        id_formatted = ''
        id = valid_uid[:len(valid_uid)-1]
        for i in range(0,len(id)):
            if i > 0:
                id_formatted = id_formatted + ':'
            if id[i] < 16:
                id_formatted = id_formatted + '0'
            id_formatted = id_formatted + hex(id[i])[2:]
        type = 'ntag'
        if len(id) == 4:
            type = 'classic'
        return {'success':True, 'id_integers':id, 'id_formatted':id_formatted.upper(), 'type':type}
    
    # Detect the presence of a tag
    def _detectTag(self):
        (stat, ATQA) = self._request(_TAG_CMD_REQIDL)
        _present = False
        if stat is self.OK:
            _present = True
        self._tag_present = _present
        return {'present':_present, 'ATQA':ATQA}
    
    # Resets the RFID module
    def reset(self):
        self._wreg(_REG_COMMAND, _CMD_SOFT_RESET)

    # Turns the antenna on
    def antennaOn(self):
        if ~(self._rreg(_REG_TX_CONTROL) & 0x03):
            self._sflags(_REG_TX_CONTROL, 0x83)
    
    # Turns the antenna off
    def antennaOff(self):
        if not (~(self._rreg(_REG_TX_CONTROL) & 0x03)):
            self._cflags(_REG_TX_CONTROL, b'\x03')

    # Stand-alone function that puts the tag into the correct state
    # Returns detailed information about the tag
    def readTagID(self):
        detect_tag_result = self._detectTag()
        if detect_tag_result['present'] is False: #Try again, the card may not be in the correct state
            detect_tag_result = self._detectTag()
        if detect_tag_result['present']:
            read_tag_id_result = self._readTagID()
            if read_tag_id_result['success']:
                self._read_tag_id_success = True
                return {'success':read_tag_id_result['success'], 'id_integers':read_tag_id_result['id_integers'], 'id_formatted':read_tag_id_result['id_formatted'], 'type':read_tag_id_result['type']}
        self._read_tag_id_success = False
        return {'success':False, 'id_integers':[0], 'id_formatted':'', 'type':''}

    # Wrapper for readTagID
    def readID(self, detail=False):
        if detail is False:
            tagId = self.readTagID()
            return tagId['id_formatted']
        else: return self.readTagID()

    # Wrapper for readTagID
    def tagPresent(self):
        id = self.readTagID()
        return id['success']

#---Write Functions--------------

# Required for Classic Tag only - Select a specific tag for reading & writing
    def _classicSelectTag(self, ser):
        buf = [0x93, 0x70] + ser[:5]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

# Required for Classic Tag only - Authenticate the address in memory
    def _classicAuth(self, mode, addr, sect, ser):
        return self._tocard(_CMD_MF_AUTHENT, [mode, addr] + sect + ser[:4])[0]

# Required for Classic Tag only - Turn off crypto
    def _classicStopCrypto(self):
        self._cflags(_REG_STATUS_2, 0x08)

# ----------------------------- Write -------------------------------------------------

# Write to an NTAG page
    def _writePageNtag(self, page, data):
        buf = [0xA2, page]
        buf += data
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        return stat

# Write to a Classic register
    def _classicWrite(self, addr, data):
        buf = [0xA0, addr]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
        if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
            stat = self.ERR
        else:
            buf = []
            for i in range(_CLASSIC_NO_BYTES_PER_REG):
                buf.append(data[i])
            buf += self._crc(buf)
            (stat, recv, bits) = self._tocard(_CMD_TRANCEIVE, buf)
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR
        return stat

# Prepare a Classic to write to a register
    def _writeClassicRegister(self, register, data_byte_array):
        while True:
            auth_result = 0
            (stat, tag_type) = self._request(_TAG_CMD_REQIDL)

            if stat == self.OK:
                (stat, raw_uid) = self._anticoll()

                if stat == self.OK:
                    if self._classicSelectTag(raw_uid) == self.OK:
                        auth_result = self._classicAuth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                        if (auth_result == self.OK):
                            stat = self._classicWrite(register, data_byte_array)
                            self._classicStopCrypto()
                            if stat == self.OK:
                                return True
                            else:
                                print("Failed to write data to tag")
                                return False
                        else:
                            print("Authentication error")
                            return False
                    else:
                        print("Failed to select tag")
                        return False   

# ------------------------------ Read ----------------------------------------------------

# Read a register from NTAG or Classic
    def _read(self, addr):
        data = [0x30, addr]
        data += self._crc(data)
        (stat, recv, _) = self._tocard(_CMD_TRANCEIVE, data)
        return recv if stat == self.OK else None

# Prepare a classic to read a register
    def _readClassicData(self, register):
        tag_data = None
        auth_result = 0
        while tag_data is None:
            (stat, tag_type) = self._request(_TAG_CMD_REQIDL)
            if stat == self.OK:
                (stat, raw_uid) = self._anticoll()
                if stat == self.OK:
                    if self._classicSelectTag(raw_uid) == self.OK:
                        auth_result = self._classicAuth(_TAG_AUTH_KEY_A, register, _CLASSIC_KEY, raw_uid)
                        if (auth_result == self.OK):
                            tag_data = self._read(register)
                            self._classicStopCrypto()
                            return tag_data
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")
            sleep_ms(10)

# ----------------------------- Write Number --------------------------------------------

# Writes a number to NTAG
    def _writeNumberToNtag(self, bytes_number, slot=0):
        tag_write_success = False
        assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
        page_adr_min = 4
        stat = self._writePageNtag(page_adr_min+slot, bytes_number)
        tag_write_success = False
        if stat == self.OK:
            tag_write_success = True
        return tag_write_success

# Writes a number to Classic
    def _writeNumberToClassic(self, bytes_number, slot=0):
        assert slot >= _SLOT_NO_MIN and slot <=_SLOT_NO_MAX, 'Slot must be between 0 and 35'
        while len(bytes_number) < _CLASSIC_NO_BYTES_PER_REG:
            bytes_number.append(0)
        tag_write_success = self._writeClassicRegister(_CLASSIC_ADR[slot], bytes_number)
        return tag_write_success

# Writes a number to the tag
    def writeNumber(self, number, slot=35):
        success = False
        bytearray_number = bytearray(struct.pack('l', number))
        read_tag_id_result = self.readTagID()
        while read_tag_id_result['success'] is False:
            read_tag_id_result = self.readTagID()
        if read_tag_id_result['success']:
            if read_tag_id_result['type'] == 'ntag':
                success = self._writeNumberToNtag(bytearray_number, slot)
                while success is False:
                    success = self._writeNumberToNtag(bytearray_number, slot)
            if read_tag_id_result['type'] == 'classic':
                success = self._writeNumberToClassic(bytearray_number, slot)
                while success is False:
                    success = self._writeNumberToClassic(bytearray_number, slot)
        return success

# ----------------------------- Read Number --------------------------------------------

# Reads a number from the tag
    def readNumber(self, slot=35):
        bytearray_number = None
        read_tag_id_result = self.readTagID()
        while read_tag_id_result['success'] is False:
            read_tag_id_result = self.readTagID()
        if read_tag_id_result['type'] == 'ntag':
            page_address = 4
            bytearray_number = self._read(page_address+slot)

        if read_tag_id_result['type'] == 'classic':
            bytearray_number = self._readClassicData(_CLASSIC_ADR[slot])
    
        try:
            number = struct.unpack('l', bytes(bytearray_number[:4]))
            number = number[0]
            return number
        except:
            print('Error reading card')
            return 0

# ----------------------------- Write Text --------------------------------------------

# Writes text to NTAG.
    def _writeTextToNtag(self, text, ignore_null=False): # NTAG213
        buffer_start = 0
        for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX+1):
            data_chunk = text[buffer_start:buffer_start+_NTAG_NO_BYTES_PER_PAGE]
            buffer_start = buffer_start + _NTAG_NO_BYTES_PER_PAGE
            data_byte_array = [ord(x) for x in list(data_chunk)]
            while len(data_byte_array) < _NTAG_NO_BYTES_PER_PAGE:
                data_byte_array.append(0)
            tag_write_success = self._writePageNtag(page_adr, data_byte_array)
            if ignore_null is False:
                if 0 in data_byte_array: # Null found.  Job complete.
                    return tag_write_success
        return tag_write_success

# Writes text to Classic.
    def _writeTextToClassic(self, text, ignore_null=False):
        buffer_start = 0
        x = 0
        for slot in range(9):
            data_chunk = text[buffer_start:buffer_start+_CLASSIC_NO_BYTES_PER_REG]
            buffer_start = buffer_start + _CLASSIC_NO_BYTES_PER_REG
            data_byte_array = [ord(x) for x in list(data_chunk)]
            while len(data_byte_array) < _CLASSIC_NO_BYTES_PER_REG:
                data_byte_array.append(0)
            tag_write_success = self._writeClassicRegister(_CLASSIC_ADR[slot], data_byte_array)
            if ignore_null is False:
                if 0 in data_byte_array: # Null found.  Job complete.
                    return tag_write_success
        return tag_write_success

# Writes text to the tag.
    def writeText(self, text, ignore_null=False):
        success = False
        maximum_characters = 144
        text = text + '\0'
        read_tag_id_result = self.readTagID()
        if read_tag_id_result['type'] == 'ntag':
            success = self._writeTextToNtag(text, ignore_null=ignore_null)
        if read_tag_id_result['type'] == 'classic':
            success = self._writeTextToClassic(text, ignore_null=ignore_null)
        return success

# ----------------------------- Read Text --------------------------------------------

# Reads text from NTAG.
    def _readTextFromNtag(self):
        total_string = ''
        try:
            for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX+1):
                page_data = self._read(page_adr)[:4]
                page_text = "".join(chr(x) for x in page_data)
                total_string = total_string + page_text
                if 0 in page_data: # Null found.  Job complete.
                    substring = total_string.split('\0')
                    return substring[0]
                page_adr = page_adr + _NTAG_NO_BYTES_PER_PAGE
        except:
            pass
        return total_string

# Reads text from Classic.
    def _readTextFromClassic(self):
        x = 0
        total_string = ''
        try:
            for slot in range(9):
                reg_data = self._readClassicData(_CLASSIC_ADR[slot])
                reg_text = "".join(chr(x) for x in reg_data)
                total_string = total_string + reg_text
                if 0 in reg_data: # Null found.  Job complete.
                    substring = total_string.split('\0')
                    return substring[0]
        except: pass
        return total_string

# Reads text from the tag.
    def readText(self, timeout=0):
        text = ''
        read_tag_id_result = self.readTagID()
        start = now()
        while read_tag_id_result['success'] is False:
            read_tag_id_result = self.readTagID()
            if timeout > 0 and now() - start > timeout: break # trigger a timeout
        if read_tag_id_result['type'] == 'ntag':
            text = self._readTextFromNtag()
        if read_tag_id_result['type'] == 'classic':
            text = self._readTextFromClassic()
        return text

# ----------------------------- Write Link --------------------------------------------

# Writes a URI to the tag
    def writeURI(self, uri): # Currently only supported by NTAG213
        is_ndef_message = chr(3)
        ndef_length = chr(len(uri) + 5)
        ndef_record_header = chr(209)
        ndef_type_length = chr(1)
        ndef_payload_length = chr(len(uri) + 1)
        is_uri_record = chr(85)
        record_type_indicator = chr(0)
        tlv_terminator = chr(254)
        ndef = is_ndef_message + ndef_length + ndef_record_header + ndef_type_length + ndef_payload_length + is_uri_record + record_type_indicator + uri + tlv_terminator
        success = self.writeText(ndef, ignore_null=True)
        return success
