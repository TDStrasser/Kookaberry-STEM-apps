# File name: veml_i2c.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: dd mmm 2020
# Date last modified: dd mmm 2020
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
# Based on the driver at https://github.com/cmur2/python-veml6070 with pure I2C bus for the Kookaberry adaptation
# Redundant SMBbus code lines have been commented out and replaced by I2C code
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Seeed VEML6070 I2C sensor breakout board
# /lib files: this file should be placed in /lib
# /root files: nil
# Other dependencies: nil
# Complementary apps: I2C_ID to debug the I2C interface
#------------------------------------------


import time

ADDR_L = 0x38 # 7bit address of the VEML6070 (write, read) - control and lsb of reading
ADDR_H = 0x39 # 7bit address of the VEML6070 (read) - msb of reading

RSET_240K = 240000
RSET_270K = 270000
RSET_300K = 300000
RSET_600K = 600000

SHUTDOWN_DISABLE = 0x00
SHUTDOWN_ENABLE = 0x01

INTEGRATIONTIME_1_2T = 0x00
INTEGRATIONTIME_1T = 0x01
INTEGRATIONTIME_2T = 0x02
INTEGRATIONTIME_4T = 0x03

# Scale factor in seconds / Ohm to determine refresh time for any RSET
# Note: 0.1 seconds (100 ms) are applicable for RSET_240K and INTEGRATIONTIME_1T
RSET_TO_REFRESHTIME_SCALE = 0.1 / RSET_240K

# The refresh time in seconds for which NORMALIZED_UVA_SENSITIVITY
# is applicable to a step count
NORMALIZED_REFRESHTIME = 0.1

# The UVA sensitivity in W/(m*m)/step which is applicable to a step count
# normalized to the NORMALIZED_REFRESHTIME, for RSET_240K and INTEGRATIONTIME_1T
NORMALIZED_UVA_SENSITIVITY = 0.05

class Veml6070:

    def __init__(self, i2c, sensor_address=ADDR_L, rset=RSET_270K, integration_time=INTEGRATIONTIME_1T):
        self.i2c = i2c
        self.buf = bytearray(1)
        self.sender_address = sensor_address
        self.rset = rset
        self.shutdown = SHUTDOWN_DISABLE # before set_integration_time()
        self.set_integration_time(integration_time)
        self.disable()

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time
        # self.bus.write_byte(self.sendor_address, self.get_command_byte())
        self.buf[0] = self.get_command_byte()
        self.i2c.writeto(self.sender_address, self.buf)
        # constant offset determined experimentally to allow sensor to readjust
        time.sleep(0.2)

    def get_integration_time(self):
        return self.integration_time

    def enable(self):
        self.shutdown = SHUTDOWN_DISABLE
        self.buf[0] = self.get_command_byte()
        self.i2c.writeto(self.sender_address, self.buf)
        # self.bus.write_byte(self.sendor_address, self.get_command_byte())

    def disable(self):
        self.shutdown = SHUTDOWN_ENABLE
        self.buf[0] = self.get_command_byte()
        self.i2c.writeto(self.sender_address, self.buf)
        # self.bus.write_byte(self.sendor_address, self.get_command_byte())

    def get_uva_light_intensity_raw(self):
        self.enable()
        # wait two times the refresh time to allow completion of a previous cycle with old settings (worst case)
        time.sleep(self.get_refresh_time()*2)
        msb = self.i2c.readfrom(ADDR_H, 1)
        # msb = self.bus.read_byte(self.sendor_address+(ADDR_H-ADDR_L))
        lsb = self.i2c.readfrom(ADDR_L, 1)
        #lsb = self.bus.read_byte(self.sendor_address)
        self.disable()
        return int.from_bytes(msb,'big') * 256 + int.from_bytes(lsb,'big')

    def get_uva_light_intensity(self):
        """
        returns the UVA light intensity in Watt per square meter (W/(m*m))
        """
        raw_data = self.get_uva_light_intensity_raw()

        # normalize raw data (step count sampled in get_refresh_time()) into the
        # linearly scaled normalized data (step count sampled in 0.1s) for which
        # we know the UVA sensitivity
        normalized_data = raw_data * NORMALIZED_REFRESHTIME / self.get_refresh_time()

        # now we can calculate the absolute UVA power detected combining
        # normalized  data with known UVA sensitivity for this data
        return normalized_data * NORMALIZED_UVA_SENSITIVITY # in W/(m*m)

    def get_command_byte(self):
        """
        assembles the command byte for the current state
        """
        cmd = (self.shutdown & 0x01) << 0 # SD
        cmd = cmd | (self.integration_time & 0x03) << 2 # IT
        cmd = ((cmd | 0x02) & 0x3F) # reserved bits
        return cmd

    def get_refresh_time(self):
        """
        returns time needed to perform a complete measurement using current settings (in s)
        """
        case_refresh_it = {
            INTEGRATIONTIME_1_2T: 0.5,
            INTEGRATIONTIME_1T: 1,
            INTEGRATIONTIME_2T: 2,
            INTEGRATIONTIME_4T: 4
        }
        return self.rset * RSET_TO_REFRESHTIME_SCALE * case_refresh_it[self.integration_time]

    @staticmethod
    def get_estimated_risk_level(intensity):
        """
        returns estimated risk level from comparing UVA light intensity value
        in W/(m*m) as parameter, thresholds calculated from application notes
        """
        if intensity < 24.888:
            return "low"
        elif intensity < 49.800:
            return "mod"
        elif intensity < 66.400:
            return "high"
        elif intensity < 91.288:
            return "v-hi"
        else:
            return "extr"
