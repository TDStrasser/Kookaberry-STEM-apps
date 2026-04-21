# FILENAME: PN532_Kookaberry.py

# COPYRIGHT: The AustSTEM Foundation Limited

# AUTHOR: Tony Strasser (adapted for PN532 by AI assistant)

# DATE-CREATED: 24 February 2026

# DATE-MODIFIED:

# VERSION: 1.0

# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350

# LICENCE:

'''
Copyright 2025 The AustSTEM Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# DESCRIPTION:
# Library module to use a PN532-based NFC/RFID Reader/Writer as a drop-in replacement
# for the PiicoDev RFID Reader/Writer (MFRC522-based).
# The PN532 communicates via I2C using its normal information frame protocol.
# This module provides the same public API as PiicoDev_RFID_Kookaberry.py so that
# existing application scripts require minimal changes.
#
# Based on:
# - PN532 User Manual (NXP UM0701-02)
# - Adafruit CircuitPython PN532 library (Tony DiCola / ladyada / Carter Nelson)
# - Carglglz MicroPython PN532 SPI port
# - Original PiicoDev RFID Kookaberry library (Tony Strasser / Core Electronics)

#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: PN532 NFC module connected to any I2C capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies: None
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

from time import sleep_ms, ticks_ms as now
import struct

_I2C_ADDRESS = 0x24  # Default I2C address of the PN532

# PN532 frame constants
_PREAMBLE     = 0x00
_STARTCODE1   = 0x00
_STARTCODE2   = 0xFF
_POSTAMBLE    = 0x00
_HOSTTOPN532  = 0xD4
_PN532TOHOST  = 0xD5

# PN532 Commands
_CMD_GETFIRMWAREVERSION  = 0x02
_CMD_SAMCONFIGURATION    = 0x14
_CMD_POWERDOWN           = 0x16
_CMD_INLISTPASSIVETARGET = 0x4A
_CMD_INDATAEXCHANGE      = 0x40
_CMD_INRELEASE           = 0x52

# Baud rate / card type selection for InListPassiveTarget
_MIFARE_ISO14443A = 0x00

# Mifare tag commands (sent via InDataExchange)
_MIFARE_CMD_AUTH_A  = 0x60
_MIFARE_CMD_AUTH_B  = 0x61
_MIFARE_CMD_READ    = 0x30
_MIFARE_CMD_WRITE   = 0xA0
_MIFARE_CMD_WRITE_ULTRALIGHT = 0xA2

# Default MIFARE Classic key
_CLASSIC_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# ACK frame expected from PN532
_ACK = bytes([0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00])

# I2C ready status byte
_I2C_READY = 0x01

# NTAG constants (NTAG213 user memory: pages 4-39, 4 bytes/page, 144 bytes total)
_NTAG_NO_BYTES_PER_PAGE = 4
_NTAG_PAGE_ADR_MIN = 4
_NTAG_PAGE_ADR_MAX = 39

# Classic constants
_CLASSIC_NO_BYTES_PER_REG = 16
_CLASSIC_ADR = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22,
                24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42,
                44, 45, 46, 48]

# Slot limits (shared between NTAG and Classic)
_SLOT_NO_MIN = 0
_SLOT_NO_MAX = 35

# ---------------------------------------------------------------------------
# PiicoDev_RFID class — PN532 based, API-compatible with MFRC522 version
# ---------------------------------------------------------------------------

class PN532(object):
    OK = 1
    NOTAGERR = 2
    ERR = 3

    def __init__(self, bus=None, address=_I2C_ADDRESS, asw=None, debug=False):
        """Initialise the PN532 RFID reader over I2C.

        Args:
            bus:     A pre-initialised MicroPython I2C or SoftI2C object.
            address: I2C address of the PN532 (default 0x24).
            asw:     Retained for API compatibility with PiicoDev RFID reader - not used
            debug:   If True, print diagnostic frame data.
        """
        self.i2c = bus
        self.debug = debug
        self.address = address

        self._tag_present = False
        self._read_tag_id_success = False
        self._uid = None          # Cached UID from last successful read
        self._tag_type = ''       # 'ntag' or 'classic'

        # Wake up and initialise the PN532
        self._wakeup()
        sleep_ms(50)
        fw = self._get_firmware_version()
        if fw is None:
            # Retry once
            self._wakeup()
            sleep_ms(100)
            fw = self._get_firmware_version()
        if fw is not None and self.debug:
            print('PN532 firmware: IC=0x{:02X} Ver={}.{} Support=0x{:02X}'.format(*fw))
        self._sam_configuration()

    # ======================== LOW-LEVEL I2C TRANSPORT ========================

    def _wakeup(self):
        """Send a dummy write to wake the PN532 from low-power / sleep."""
        try:
            self.i2c.writeto(self.address, b"0x00")  # bytes([0x00]))
        except OSError:
            pass
        sleep_ms(50)

    def _wait_ready(self, timeout=500):
        """Poll the PN532 status byte until it indicates ready, or timeout (ms)."""
        start = now()
        while (now() - start) < timeout:
            try:
                status = self.i2c.readfrom(self.address, 1)
                if status[0] == _I2C_READY:
                    return True
            except OSError:
                pass
            sleep_ms(10)
        if self.debug:
            print('_wait_ready() timeout')
        return False

    def _write_data(self, data):
        """Write raw bytes to the PN532 over I2C."""
        if self.debug:
            print('TX:', [hex(b) for b in data])
        self.i2c.writeto(self.address, data)

    def _read_data(self, count):
        """Read count bytes from the PN532 (skipping the leading status byte)."""
        buf = self.i2c.readfrom(self.address, count + 1)
        if buf[0] != _I2C_READY:
            return None
        if self.debug:
            print('RX:', [hex(b) for b in buf[1:]])
        return buf[1:]

    # ======================== PN532 FRAME LAYER =============================

    def _write_frame(self, data):
        """Build and send a normal information frame containing *data*."""
        length = len(data)
        assert 0 < length < 255, 'Frame data must be 1-254 bytes'
        frame = bytearray(length + 8)
        frame[0] = _PREAMBLE
        frame[1] = _STARTCODE1
        frame[2] = _STARTCODE2
        frame[3] = length & 0xFF
        frame[4] = (0xFF - length + 1) & 0xFF #(~length + 1) & 0xFF           # LCS - two's complement
        frame[5:5 + length] = data
        checksum = sum(data)
        frame[5 + length] = (0xFF - sum(data) + 1) & 0xFF  # (~checksum) & 0xFF      # DCS
        frame[6 + length] = _POSTAMBLE
        self._write_data(bytes(frame))
        if self.debug: print(f" frame sent :{frame.hex(" ")}")

    def _read_frame(self, length):
        """Read a normal information frame; return the payload (TFI + PD0..PDn)."""
        response = self._read_data(length + 8)
        if response is None:
            raise RuntimeError('PN532 not ready')
        if self.debug:
            print('Frame:', [hex(b) for b in response])

        # Scan past preamble 0x00 bytes to the 0xFF start code byte
        offset = 0
        while offset < len(response) and response[offset] == 0x00:
            offset += 1
        if offset >= len(response) or response[offset] != 0xFF:
            raise RuntimeError('Invalid frame preamble')
        offset += 1

        frame_len = response[offset]
        # Verify length checksum
        if (frame_len + response[offset + 1]) & 0xFF != 0:
            raise RuntimeError('Frame length checksum error')
        # Verify data checksum
        checksum = sum(response[offset + 2: offset + 2 + frame_len + 1]) & 0xFF
        if checksum != 0:
            raise RuntimeError('Frame data checksum error')
        return response[offset + 2: offset + 2 + frame_len]

    def _read_ack(self):
        """Read and verify the ACK frame from the PN532."""
        ack = self._read_data(len(_ACK))
        if ack is None:
            return False
        if self.debug:
            print('Frame:', [hex(b) for b in ack])
        return bytes(ack) == _ACK

    # ======================== PN532 COMMAND LAYER ===========================

    def call_function(self, command, params=b'', response_length=0, timeout=1000):
        """Send a command to the PN532 and return the response payload.

        Returns a bytearray of response data (after TFI and command+1 byte),
        or None on timeout / error.
        """
        # Build frame data: TFI + command + params
        data = bytearray(2 + len(params))
        data[0] = _HOSTTOPN532
        data[1] = command & 0xFF
        for i, val in enumerate(params):
            data[2 + i] = val

        # Send the command frame
        try:
            self._write_frame(data)
        except OSError:
            self._wakeup()
            return None

        # Wait for and verify ACK
        if not self._wait_ready(timeout):
            return None
        if not self._read_ack():
            raise RuntimeError('Did not receive ACK from PN532')

        # Wait for response
        if not self._wait_ready(timeout):
            return None

        # Read the response frame
        try:
            response = self._read_frame(response_length + 2)
        except RuntimeError:
            return None

        # Validate response is for our command
        if len(response) < 2:
            return None
        if response[0] != _PN532TOHOST or response[1] != (command + 1):
            raise RuntimeError('Unexpected command response')
        return response[2:]

    # ======================== PN532 SETUP COMMANDS ==========================

    def _get_firmware_version(self):
        """Return (IC, Ver, Rev, Support) or None."""
        resp = self.call_function(_CMD_GETFIRMWAREVERSION, response_length=4, timeout=500)
        if resp is None or len(resp) < 4:
            return None
        return (resp[0], resp[1], resp[2], resp[3])

    def _sam_configuration(self):
        """Configure the PN532 SAM (Security Access Module) for normal operation."""
        self.call_function(_CMD_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])

    # ======================== TAG DETECTION / UID ===========================

    def _read_passive_target(self, timeout=1000):
        """Attempt to detect a single ISO14443A tag.

        Returns the UID as a bytearray, or None if no tag found.
        """
        try:
            resp = self.call_function(
                _CMD_INLISTPASSIVETARGET,
                params=[0x01, _MIFARE_ISO14443A],
                response_length=20,
                timeout=timeout
            )
        except RuntimeError:
            return None
        if resp is None or len(resp) < 6:
            return None
        if resp[0] != 0x01:  # number of targets
            return None
        uid_length = resp[5]
        if uid_length > 10 or len(resp) < 6 + uid_length:
            return None
        return bytearray(resp[6:6 + uid_length])

    def _classify_tag(self, uid):
        """Return 'ntag' for 7-byte UIDs, 'classic' for 4-byte UIDs."""
        if uid is None:
            return ''
        if len(uid) == 7:
            return 'ntag'
        return 'classic'

    def _readTagID(self):
        """Internal: detect a tag and read its UID.  Returns a result dict."""
        result = {'success': False, 'id_integers': [], 'id_formatted': '', 'type': ''}
        uid = self._read_passive_target(timeout=500)
        if uid is None:
            return result

        id_list = list(uid)
        id_formatted = ':'.join('{:02X}'.format(b) for b in uid)
        tag_type = self._classify_tag(uid)

        self._uid = uid
        self._tag_type = tag_type
        return {
            'success': True,
            'id_integers': id_list,
            'id_formatted': id_formatted,
            'type': tag_type
        }

    def _detectTag(self):
        """Detect tag presence and cache UID."""
        result = self._readTagID()
        self._tag_present = result['success']
        return {'present': result['success'], 'ATQA': 0}

    # ======================== PUBLIC API — Tag ID ===========================

    def readTagID(self):
        """Read the tag UID — matches original PiicoDev_RFID API.

        Returns dict with keys: success, id_integers, id_formatted, type
        """
        result = self._readTagID()
        if not result['success']:
            # Retry once — the tag may need a second attempt
            result = self._readTagID()
        self._read_tag_id_success = result['success']
        if not result['success']:
            return {'success': False, 'id_integers': [0], 'id_formatted': '', 'type': ''}
        return result

    def readId(self, detail=False):
        """Wrapper for readTagID — returns formatted string or full dict."""
        if not detail:
            tagId = self.readTagID()
            return tagId['id_formatted']
        return self.readTagID()

    def tagPresent(self):
        """Return True if a tag is currently present."""
        id_result = self.readTagID()
        return id_result['success']

    # ======================== LOW-LEVEL TAG I/O =============================

    def _release_target(self):
        """Release the current target so a new InListPassiveTarget can succeed."""
        try:
            self.call_function(_CMD_INRELEASE, params=[0x00], response_length=1, timeout=200)
        except RuntimeError:
            pass

    def _mifare_authenticate(self, block_number, uid, key=_CLASSIC_KEY, key_cmd=_MIFARE_CMD_AUTH_A):
        """Authenticate a MIFARE Classic block using key A (default)."""
        uid_bytes = bytes(uid) if not isinstance(uid, (bytes, bytearray)) else uid
        key_bytes = bytes(key)
        params = bytearray(3 + len(key_bytes) + len(uid_bytes))
        params[0] = 0x01                # target number
        params[1] = key_cmd & 0xFF
        params[2] = block_number & 0xFF
        params[3:3 + len(key_bytes)] = key_bytes
        params[3 + len(key_bytes):] = uid_bytes[:4]  # only first 4 bytes of UID used
        resp = self.call_function(_CMD_INDATAEXCHANGE, params=params, response_length=1)
        if resp is None:
            return False
        return resp[0] == 0x00

    def _mifare_read_block(self, block_number):
        """Read 16 bytes from a MIFARE Classic or NTAG block/page address.

        The PN532 InDataExchange with READ command always returns 16 bytes.
        For NTAG, only the first 4 are from the requested page.
        """
        resp = self.call_function(
            _CMD_INDATAEXCHANGE,
            params=[0x01, _MIFARE_CMD_READ, block_number & 0xFF],
            response_length=17
        )
        if resp is None or len(resp) < 1:
            return None
        if resp[0] != 0x00:
            return None
        return list(resp[1:])

    def _mifare_write_classic_block(self, block_number, data):
        """Write 16 bytes to a MIFARE Classic block."""
        params = bytearray(3 + _CLASSIC_NO_BYTES_PER_REG)
        params[0] = 0x01
        params[1] = _MIFARE_CMD_WRITE
        params[2] = block_number & 0xFF
        for i in range(_CLASSIC_NO_BYTES_PER_REG):
            params[3 + i] = data[i] if i < len(data) else 0
        resp = self.call_function(_CMD_INDATAEXCHANGE, params=params, response_length=1)
        if resp is None:
            return self.ERR
        return self.OK if resp[0] == 0x00 else self.ERR

    def _ntag_write_page(self, page, data):
        """Write 4 bytes to an NTAG page."""
        params = bytearray(3 + _NTAG_NO_BYTES_PER_PAGE)
        params[0] = 0x01
        params[1] = _MIFARE_CMD_WRITE_ULTRALIGHT
        params[2] = page & 0xFF
        for i in range(_NTAG_NO_BYTES_PER_PAGE):
            params[3 + i] = data[i] if i < len(data) else 0
        resp = self.call_function(_CMD_INDATAEXCHANGE, params=params, response_length=1)
        if resp is None:
            return self.ERR
        return self.OK if resp[0] == 0x00 else self.ERR

    # ======================== NTAG READ / WRITE HELPERS =====================

    def _read_ntag_page(self, page):
        """Read 4 bytes from an NTAG page (wrapper around _mifare_read_block)."""
        data = self._mifare_read_block(page)
        if data is None:
            return None
        return data[:4]  # NTAG pages are 4 bytes; READ returns 16

    # ======================== CLASSIC READ / WRITE WITH AUTH ================

    def _readClassicData(self, register):
        """Read 16 bytes from a Classic block, handling authentication.

        Requires a tag to already be selected via InListPassiveTarget.
        """
        if self._uid is None:
            return None
        if not self._mifare_authenticate(register, self._uid):
            if self.debug:
                print('Authentication error on block', register)
            return None
        return self._mifare_read_block(register)

    def _writeClassicRegister(self, register, data_byte_array):
        """Write 16 bytes to a Classic block, handling authentication."""
        if self._uid is None:
            return False
        if not self._mifare_authenticate(register, self._uid):
            if self.debug:
                print('Authentication error on block', register)
            return False
        stat = self._mifare_write_classic_block(register, data_byte_array)
        return stat == self.OK

    # ======================== PUBLIC API — Write Number =====================

    def _writeNumberToNtag(self, bytes_number, slot=0):
        assert _SLOT_NO_MIN <= slot <= _SLOT_NO_MAX, 'Slot must be between 0 and 35'
        page_adr = _NTAG_PAGE_ADR_MIN + slot
        stat = self._ntag_write_page(page_adr, bytes_number)
        return stat == self.OK

    def _writeNumberToClassic(self, bytes_number, slot=0):
        assert _SLOT_NO_MIN <= slot <= _SLOT_NO_MAX, 'Slot must be between 0 and 35'
        while len(bytes_number) < _CLASSIC_NO_BYTES_PER_REG:
            bytes_number.append(0)
        return self._writeClassicRegister(_CLASSIC_ADR[slot], bytes_number)

    def writeNumber(self, number, slot=35):
        """Write an integer to a tag at the specified slot.

        Blocks until a tag is present and the write succeeds.
        """
        success = False
        bytearray_number = bytearray(struct.pack('l', number))
        read_tag_id_result = self.readTagID()
        while not read_tag_id_result['success']:
            read_tag_id_result = self.readTagID()

        if read_tag_id_result['type'] == 'ntag':
            success = self._writeNumberToNtag(bytearray_number, slot)
            while not success:
                success = self._writeNumberToNtag(bytearray_number, slot)
        if read_tag_id_result['type'] == 'classic':
            success = self._writeNumberToClassic(list(bytearray_number), slot)
            while not success:
                success = self._writeNumberToClassic(list(bytearray_number), slot)
        return success

    # ======================== PUBLIC API — Read Number ======================

    def readNumber(self, slot=35):
        """Read an integer from the tag at the specified slot."""
        read_tag_id_result = self.readTagID()
        while not read_tag_id_result['success']:
            read_tag_id_result = self.readTagID()

        bytearray_number = None
        if read_tag_id_result['type'] == 'ntag':
            bytearray_number = self._read_ntag_page(_NTAG_PAGE_ADR_MIN + slot)
        if read_tag_id_result['type'] == 'classic':
            bytearray_number = self._readClassicData(_CLASSIC_ADR[slot])
        try:
            number = struct.unpack('l', bytes(bytearray_number[:4]))
            return number[0]
        except:
            print('Error reading card')
            return 0

    # ======================== PUBLIC API — Write Text =======================

    def _writeTextToNtag(self, text, ignore_null=False):
        buffer_start = 0
        for page_adr in range(_NTAG_PAGE_ADR_MIN, _NTAG_PAGE_ADR_MAX + 1):
            data_chunk = text[buffer_start:buffer_start + _NTAG_NO_BYTES_PER_PAGE]
            buffer_start += _NTAG_NO_BYTES_PER_PAGE
            data_byte_array = [ord(x) for x in list(data_chunk)]
            while len(data_byte_array) < _NTAG_NO_BYTES_PER_PAGE:
                data_byte_array.append(0)
            stat = self._ntag_write_page(page_adr, data_byte_array)
            tag_write_success = (stat == self.OK)
            if not ignore_null:
                if 0 in data_byte_array:
                    return tag_write_success
        return tag_write_success

    def _writeTextToClassic(self, text, ignore_null=False):
        buffer_start = 0
        for slot in range(9):
            data_chunk = text[buffer_start:buffer_start + _CLASSIC_NO_BYTES_PER_REG]
            buffer_start += _CLASSIC_NO_BYTES_PER_REG
            data_byte_array = [ord(x) for x in list(data_chunk)]
            while len(data_byte_array) < _CLASSIC_NO_BYTES_PER_REG:
                data_byte_array.append(0)
            tag_write_success = self._writeClassicRegister(_CLASSIC_ADR[slot], data_byte_array)
            if not ignore_null:
                if 0 in data_byte_array:
                    return tag_write_success
        return tag_write_success

    def writeText(self, text, ignore_null=False):
        """Write a text string to the tag."""
        success = False
        text = text + '\0'
        read_tag_id_result = self.readTagID()
        if read_tag_id_result['type'] == 'ntag':
            success = self._writeTextToNtag(text, ignore_null=ignore_null)
        if read_tag_id_result['type'] == 'classic':
            success = self._writeTextToClassic(text, ignore_null=ignore_null)
        return success

    # ======================== PUBLIC API — Read Text ========================

    def _readTextFromNtag(self):
        total_string = ''
        try:
            for page_adr in range(_NTAG_PAGE_ADR_MIN, _NTAG_PAGE_ADR_MAX + 1):
                page_data = self._read_ntag_page(page_adr)
                if page_data is None:
                    break
                page_text = "".join(chr(x) for x in page_data)
                total_string += page_text
                if 0 in page_data:
                    return total_string.split('\0')[0]
        except:
            pass
        return total_string

    def _readTextFromClassic(self):
        total_string = ''
        try:
            for slot in range(9):
                reg_data = self._readClassicData(_CLASSIC_ADR[slot])
                if reg_data is None:
                    break
                reg_text = "".join(chr(x) for x in reg_data)
                total_string += reg_text
                if 0 in reg_data:
                    return total_string.split('\0')[0]
        except:
            pass
        return total_string

    def readText(self, timeout=0):
        """Read text from the tag."""
        text = ''
        read_tag_id_result = self.readTagID()
        start = now()
        while not read_tag_id_result['success']:
            read_tag_id_result = self.readTagID()
            if timeout > 0 and now() - start > timeout:
                break
        if read_tag_id_result['type'] == 'ntag':
            text = self._readTextFromNtag()
        if read_tag_id_result['type'] == 'classic':
            text = self._readTextFromClassic()
        return text

    # ======================== PUBLIC API — Write URI ========================

    def writeURI(self, uri):
        """Write an NDEF URI record to the tag (NTAG213 primarily)."""
        is_ndef_message = chr(3)
        ndef_length = chr(len(uri) + 5)
        ndef_record_header = chr(209)
        ndef_type_length = chr(1)
        ndef_payload_length = chr(len(uri) + 1)
        is_uri_record = chr(85)
        record_type_indicator = chr(0)
        tlv_terminator = chr(254)
        ndef = (is_ndef_message + ndef_length + ndef_record_header + ndef_type_length +
                ndef_payload_length + is_uri_record + record_type_indicator + uri + tlv_terminator)
        success = self.writeText(ndef, ignore_null=True)
        return success

    # ======================== UTILITY =======================================

    def antennaOn(self):
        """No-op for PN532 — the RF field is managed by the PN532 firmware."""
        pass

    def antennaOff(self):
        """No-op for PN532 — the RF field is managed by the PN532 firmware."""
        pass

    def reset(self):
        """Soft-reset the PN532 via SAM reconfiguration."""
        self._wakeup()
        sleep_ms(50)
        self._sam_configuration()

'''
# Example of basic tag read
# from PN532_Kookaberry import PN532
from machine import Pin, SoftI2C
from time import sleep_ms
i2c = SoftI2C(sda=Pin("P3B"), scl=Pin("P3A"))
rfid = PN532(i2c, debug=False)   # Initialise the RFID module

print('Place tag near the NFC reader')
print('')
while True:
    if rfid.tagPresent():        # if an RFID tag is present
        id = rfid.readId()       # get the id
        print(id)                # print the id
    sleep_ms(100)
'''