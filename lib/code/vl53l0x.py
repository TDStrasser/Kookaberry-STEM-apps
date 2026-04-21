# ------------------------------------------
# File: vl53l0x.py
# Description: MicroPython class library module for the VL53L0X
#              laser Time-of-Flight (ToF) distance sensor.
#              Adapted from the Pololu VL53L0X Arduino driver and
#              the Adafruit CircuitPython VL53L0X driver by Tony DiCola.
#              Modified for Kookaberry / MicroPython (no bus_device dependency).
# Author: Tony DiCola (original), modified for Kookaberry
# Created: 2017
# Modified: 2026-02-27
# Version: 2.0 - Instance-safe (re-entrant) version
# Platform: Kookaberry / MicroPython 1.12+
# Licence: MIT
# ------------------------------------------
# Description of Changes in v2.0:
#   - Moved class-level I2C communication buffers (BUFFER8, BUFFER16,
#     BUFFER24, BUFFER40) into instance-level attributes (self._buf1,
#     self._buf2, self._buf3, self._buf5) so that each sensor instance
#     has its own private buffers. This makes the driver re-entrant and
#     safe for use with multiple VL53L0X sensors on the same or
#     different I2C buses without data corruption between instances.
#   - Added comprehensive commentary explaining each section of the code.
# ------------------------------------------
# Complementary apps: Used by Kookaberry apps that require laser
#                     distance measurement via the VL53L0X sensor.
# ------------------------------------------
# BEGIN-CODE
# ------------------------------------------

import time
from micropython import const

# ============================================================================
# VL53L0X Register Address Constants
# These are the internal register addresses of the VL53L0X sensor as
# defined in the ST Microelectronics datasheet and the Pololu Arduino
# driver. They control ranging configuration, interrupts, timing,
# calibration, SPAD management, and result readback.
# ============================================================================

# -- Ranging control registers --
SYSRANGE_START                          = const(0x00)

# -- System threshold registers for interrupt triggering --
SYSTEM_THRESH_HIGH                      = const(0x0C)
SYSTEM_THRESH_LOW                       = const(0x0E)

# -- Sequence and range configuration --
SYSTEM_SEQUENCE_CONFIG                  = const(0x01)
SYSTEM_RANGE_CONFIG                     = const(0x09)

# -- Inter-measurement period for continuous timed mode --
SYSTEM_INTERMEASUREMENT_PERIOD          = const(0x04)

# -- GPIO interrupt configuration and control --
SYSTEM_INTERRUPT_CONFIG_GPIO            = const(0x0A)
GPIO_HV_MUX_ACTIVE_HIGH                = const(0x84)
SYSTEM_INTERRUPT_CLEAR                  = const(0x0B)

# -- Result status registers --
RESULT_INTERRUPT_STATUS                 = const(0x13)
RESULT_RANGE_STATUS                     = const(0x14)

# -- Ambient and ranging event count registers (for signal analysis) --
RESULT_CORE_AMBIENT_WINDOW_EVENTS_RTN   = const(0xBC)
RESULT_CORE_RANGING_TOTAL_EVENTS_RTN    = const(0xC0)
RESULT_CORE_AMBIENT_WINDOW_EVENTS_REF   = const(0xD0)
RESULT_CORE_RANGING_TOTAL_EVENTS_REF    = const(0xD4)
RESULT_PEAK_SIGNAL_RATE_REF             = const(0xB6)

# -- Part-to-part range offset calibration --
ALGO_PART_TO_PART_RANGE_OFFSET_MM       = const(0x28)

# -- I2C address register (allows runtime address change) --
I2C_SLAVE_DEVICE_ADDRESS                = const(0x8A)

# -- Minimum Signal Rate Check (MSRC) configuration --
MSRC_CONFIG_CONTROL                     = const(0x60)

# -- Pre-range configuration registers --
PRE_RANGE_CONFIG_MIN_SNR                = const(0x27)
PRE_RANGE_CONFIG_VALID_PHASE_LOW        = const(0x56)
PRE_RANGE_CONFIG_VALID_PHASE_HIGH       = const(0x57)
PRE_RANGE_MIN_COUNT_RATE_RTN_LIMIT      = const(0x64)

# -- Final range configuration registers --
FINAL_RANGE_CONFIG_MIN_SNR              = const(0x67)
FINAL_RANGE_CONFIG_VALID_PHASE_LOW      = const(0x47)
FINAL_RANGE_CONFIG_VALID_PHASE_HIGH     = const(0x48)
FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = const(0x44)

# -- Pre-range sigma threshold registers --
PRE_RANGE_CONFIG_SIGMA_THRESH_HI        = const(0x61)
PRE_RANGE_CONFIG_SIGMA_THRESH_LO        = const(0x62)

# -- VCSEL (Vertical Cavity Surface Emitting Laser) pulse period config --
PRE_RANGE_CONFIG_VCSEL_PERIOD           = const(0x50)
PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI      = const(0x51)
PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO      = const(0x52)

# -- Histogram configuration (not typically used in basic ranging) --
SYSTEM_HISTOGRAM_BIN                    = const(0x81)
HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT   = const(0x33)
HISTOGRAM_CONFIG_READOUT_CTRL           = const(0x55)

# -- Final range VCSEL period and timeout --
FINAL_RANGE_CONFIG_VCSEL_PERIOD         = const(0x70)
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI    = const(0x71)
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO    = const(0x72)

# -- Crosstalk compensation --
CROSSTALK_COMPENSATION_PEAK_RATE_MCPS   = const(0x20)

# -- MSRC timeout --
MSRC_CONFIG_TIMEOUT_MACROP              = const(0x46)

# -- Soft reset register --
SOFT_RESET_GO2_SOFT_RESET_N             = const(0xBF)

# -- Identification registers (used to verify sensor presence) --
IDENTIFICATION_MODEL_ID                 = const(0xC0)
IDENTIFICATION_REVISION_ID              = const(0xC2)

# -- Oscillator calibration --
OSC_CALIBRATE_VAL                       = const(0xF8)

# -- Global VCSEL width --
GLOBAL_CONFIG_VCSEL_WIDTH               = const(0x32)

# -- SPAD (Single Photon Avalanche Diode) enable reference map registers --
GLOBAL_CONFIG_SPAD_ENABLES_REF_0        = const(0xB0)
GLOBAL_CONFIG_SPAD_ENABLES_REF_1        = const(0xB1)
GLOBAL_CONFIG_SPAD_ENABLES_REF_2        = const(0xB2)
GLOBAL_CONFIG_SPAD_ENABLES_REF_3        = const(0xB3)
GLOBAL_CONFIG_SPAD_ENABLES_REF_4        = const(0xB4)
GLOBAL_CONFIG_SPAD_ENABLES_REF_5        = const(0xB5)

# -- SPAD reference configuration --
GLOBAL_CONFIG_REF_EN_START_SELECT       = const(0xB6)
DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD    = const(0x4E)
DYNAMIC_SPAD_REF_EN_START_OFFSET       = const(0x4F)

# -- Power management --
POWER_MANAGEMENT_GO1_POWER_FORCE        = const(0x80)

# -- Voltage regulator pad configuration --
VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV       = const(0x89)

# -- Phase calibration --
ALGO_PHASECAL_LIM                       = const(0x30)
ALGO_PHASECAL_CONFIG_TIMEOUT            = const(0x30)

# -- VCSEL period type selectors --
VCSEL_PERIOD_PRE_RANGE                  = const(0)
VCSEL_PERIOD_FINAL_RANGE                = const(1)


# ============================================================================
# Module-level helper functions for timeout encoding/decoding
# These convert between the sensor's internal macro-clock timeout
# representation and human-readable microsecond values.
# ============================================================================

def _decode_timeout(val):
    """Decode a timeout register value from the VL53L0X format.

    The sensor stores timeouts in a compressed format:
        (LSByte * 2^MSByte) + 1
    This function reverses that encoding to recover the original value.
    """
    return float(val & 0xFF) * (2.0 ** ((val & 0xFF00) >> 8)) + 1


def _encode_timeout(timeout_mclks):
    """Encode a timeout in macro-clocks into the VL53L0X register format.

    Compresses the timeout value into: (MSByte << 8) | LSByte
    where the original value ≈ LSByte * 2^MSByte + 1.
    """
    timeout_mclks = int(timeout_mclks) & 0xFFFF
    ls_byte = 0
    ms_byte = 0
    if timeout_mclks > 0:
        ls_byte = timeout_mclks - 1
        while ls_byte > 255:
            ls_byte >>= 1
            ms_byte += 1
        return ((ms_byte << 8) | (ls_byte & 0xFF)) & 0xFFFF
    return 0


def _timeout_mclks_to_microseconds(timeout_period_mclks, vcsel_period_pclks):
    """Convert a timeout from macro-clocks to microseconds.

    Uses the VCSEL period (in PCLKs) to compute the macro-period in
    nanoseconds, then scales the timeout accordingly.
    """
    macro_period_ns = ((2304 * (vcsel_period_pclks) * 1655) + 500) // 1000
    return ((timeout_period_mclks * macro_period_ns)
            + (macro_period_ns // 2)) // 1000


def _timeout_microseconds_to_mclks(timeout_period_us, vcsel_period_pclks):
    """Convert a timeout from microseconds to macro-clocks.

    Inverse of _timeout_mclks_to_microseconds.
    """
    macro_period_ns = ((2304 * (vcsel_period_pclks) * 1655) + 500) // 1000
    return ((timeout_period_us * 1000)
            + (macro_period_ns // 2)) // macro_period_ns


# ============================================================================
# VL53L0X Driver Class
# ============================================================================

class VL53L0X:
    """MicroPython driver for the VL53L0X Time-of-Flight laser distance sensor.

    This class communicates with the VL53L0X over I2C to perform single-shot
    or continuous distance measurements. It supports multiple sensors on the
    same I2C bus via runtime I2C address reassignment.

    Key improvement in v2.0: All I2C communication buffers are now instance
    attributes rather than class-level shared buffers. This ensures that
    multiple VL53L0X instances can operate independently without risk of
    one instance corrupting another's in-progress I2C transaction data.

    Usage example:
        from machine import SoftI2C, Pin
        import vl53l0x

        i2c = SoftI2C( scl=Pin("3A"), sda=Pin("3B"))
        sensor1 = vl53l0x.VL53L0X(i2c, address=0x29)
        sensor2 = vl53l0x.VL53L0X(i2c, address=0x30)

        print("Sensor 1:", sensor1.range, "mm")
        print("Sensor 2:", sensor2.range, "mm")
    """

    def __init__(self, i2c, address=0x29, io_timeout_ms=0):
        """Initialise the VL53L0X sensor driver.

        Args:
            i2c: A MicroPython machine.I2C bus instance.
            address: The 7-bit I2C address of the sensor (default 0x29).
            io_timeout_ms: Timeout in milliseconds for I2C operations.
                           0 means no timeout (wait indefinitely).
        """
        self.i2c = i2c
        self.address = address
        self.io_timeout_ms = io_timeout_ms

        # --- Instance-level I2C communication buffers ---
        # These buffers are used internally by read/write methods to
        # assemble I2C transactions. By making them per-instance, each
        # sensor object has its own private working memory, ensuring
        # safe concurrent usage of multiple sensor instances.
        self._buf1 = bytearray(1)   # 1-byte buffer (for register addressing)
        self._buf2 = bytearray(2)   # 2-byte buffer (for 8-bit read/write)
        self._buf3 = bytearray(3)   # 3-byte buffer (for 16-bit write)
        self._buf5 = bytearray(5)   # 5-byte buffer (for 32-bit write)

        # Track whether the sensor is in continuous measurement mode
        self.continuous_mode = False

        # ----------------------------------------------------------
        # Sensor identification check
        # Verify that the device at the given I2C address is actually
        # a VL53L0X by reading identification registers (datasheet §3.2).
        # ----------------------------------------------------------
        if (self._read_u8(0xC0) != 0xEE
                or self._read_u8(0xC1) != 0xAA
                or self._read_u8(0xC2) != 0x10):
            raise RuntimeError(
                "Failed to find expected ID register values. Check wiring!")

        # ----------------------------------------------------------
        # Sensor initialisation sequence
        # Based on the Pololu VL53L0X Arduino library:
        # https://github.com/pololu/vl53l0x-arduino/blob/master/VL53L0X.cpp
        # ----------------------------------------------------------

        # Set I2C standard mode and read the stop variable
        for pair in ((0x88, 0x00), (0x80, 0x01), (0xFF, 0x01), (0x00, 0x00)):
            self._write_u8(pair[0], pair[1])
        self._stop_variable = self._read_u8(0x91)
        for pair in ((0x00, 0x01), (0xFF, 0x00), (0x80, 0x00)):
            self._write_u8(pair[0], pair[1])

        # Disable SIGNAL_RATE_MSRC (bit 1) and SIGNAL_RATE_PRE_RANGE
        # (bit 4) limit checks by setting those bits high
        config_control = self._read_u8(MSRC_CONFIG_CONTROL) | 0x12
        self._write_u8(MSRC_CONFIG_CONTROL, config_control)

        # Set the return signal rate limit to 0.25 MCPS (mega counts/sec)
        self.signal_rate_limit = 0.25

        # Enable all sequence steps initially
        self._write_u8(SYSTEM_SEQUENCE_CONFIG, 0xFF)

        # ----------------------------------------------------------
        # SPAD (Single Photon Avalanche Diode) calibration
        # Read and configure the reference SPAD map to ensure
        # accurate distance measurements.
        # ----------------------------------------------------------
        spad_count, spad_is_aperture = self._get_spad_info()

        # Read the current SPAD enable reference map (6 bytes)
        ref_spad_map = bytearray(6)
        self._buf1[0] = GLOBAL_CONFIG_SPAD_ENABLES_REF_0
        self.i2c.writeto(self.address, self._buf1)
        self.i2c.readfrom_into(self.address, ref_spad_map)

        # Configure the reference SPAD start and count
        for pair in (
            (0xFF, 0x01),
            (DYNAMIC_SPAD_REF_EN_START_OFFSET, 0x00),
            (DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD, 0x2C),
            (0xFF, 0x00),
            (GLOBAL_CONFIG_REF_EN_START_SELECT, 0xB4),
        ):
            self._write_u8(pair[0], pair[1])

        # Enable the correct number of reference SPADs
        # Aperture SPADs start at index 12; non-aperture start at 0
        first_spad_to_enable = 12 if spad_is_aperture else 0
        spads_enabled = 0
        for i in range(48):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                # Disable this SPAD - it is before the first valid one
                # or we have already enabled enough SPADs
                ref_spad_map[i // 8] &= ~(1 << (i % 8))
            elif (ref_spad_map[1 + (i // 8)] >> (i % 8)) & 0x1 > 0:
                spads_enabled += 1

        # Write the updated SPAD map back to the sensor
        self.i2c.writeto(self.address, ref_spad_map)

        # ----------------------------------------------------------
        # Default tuning settings
        # A long sequence of register writes that configure internal
        # analog and digital parameters of the sensor. These values
        # come from the ST API reference implementation.
        # ----------------------------------------------------------
        for pair in (
            (0xFF, 0x01), (0x00, 0x00), (0xFF, 0x00), (0x09, 0x00),
            (0x10, 0x00), (0x11, 0x00), (0x24, 0x01), (0x25, 0xFF),
            (0x75, 0x00), (0xFF, 0x01), (0x4E, 0x2C), (0x48, 0x00),
            (0x30, 0x20), (0xFF, 0x00), (0x30, 0x09), (0x54, 0x00),
            (0x31, 0x04), (0x32, 0x03), (0x40, 0x83), (0x46, 0x25),
            (0x60, 0x00), (0x27, 0x00), (0x50, 0x06), (0x51, 0x00),
            (0x52, 0x96), (0x56, 0x08), (0x57, 0x30), (0x61, 0x00),
            (0x62, 0x00), (0x64, 0x00), (0x65, 0x00), (0x66, 0xA0),
            (0xFF, 0x01), (0x22, 0x32), (0x47, 0x14), (0x49, 0xFF),
            (0x4A, 0x00), (0xFF, 0x00), (0x7A, 0x0A), (0x7B, 0x00),
            (0x78, 0x21), (0xFF, 0x01), (0x23, 0x34), (0x42, 0x00),
            (0x44, 0xFF), (0x45, 0x26), (0x46, 0x05), (0x40, 0x40),
            (0x0E, 0x06), (0x20, 0x1A), (0x43, 0x40), (0xFF, 0x00),
            (0x34, 0x03), (0x35, 0x44), (0xFF, 0x01), (0x31, 0x04),
            (0x4B, 0x09), (0x4C, 0x05), (0x4D, 0x04), (0xFF, 0x00),
            (0x44, 0x00), (0x45, 0x20), (0x47, 0x08), (0x48, 0x28),
            (0x67, 0x00), (0x70, 0x04), (0x71, 0x01), (0x72, 0xFE),
            (0x76, 0x00), (0x77, 0x00), (0xFF, 0x01), (0x0D, 0x01),
            (0xFF, 0x00), (0x80, 0x01), (0x01, 0xF8), (0xFF, 0x01),
            (0x8E, 0x01), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00),
        ):
            self._write_u8(pair[0], pair[1])

        # ----------------------------------------------------------
        # GPIO interrupt configuration
        # Configure the sensor's GPIO pin for new-sample-ready interrupt,
        # active low polarity, and clear any pending interrupt.
        # ----------------------------------------------------------
        self._write_u8(SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)
        gpio_hv_mux_active_high = self._read_u8(GPIO_HV_MUX_ACTIVE_HIGH)
        self._write_u8(
            GPIO_HV_MUX_ACTIVE_HIGH,
            gpio_hv_mux_active_high & ~0x10)  # Set active low
        self._write_u8(SYSTEM_INTERRUPT_CLEAR, 0x01)

        # ----------------------------------------------------------
        # Measurement timing budget
        # Read, save, and then restore the timing budget. The budget
        # controls the trade-off between measurement speed and accuracy.
        # ----------------------------------------------------------
        self._measurement_timing_budget_us = self.measurement_timing_budget
        self._write_u8(SYSTEM_SEQUENCE_CONFIG, 0xE8)
        self.measurement_timing_budget = self._measurement_timing_budget_us

        # ----------------------------------------------------------
        # VHV and phase calibration
        # Perform single reference calibrations required after power-up.
        # ----------------------------------------------------------
        self._write_u8(SYSTEM_SEQUENCE_CONFIG, 0x01)
        self._perform_single_ref_calibration(0x40)

        self._write_u8(SYSTEM_SEQUENCE_CONFIG, 0x02)
        self._perform_single_ref_calibration(0x00)

        # Restore the previous sequence configuration
        self._write_u8(SYSTEM_SEQUENCE_CONFIG, 0xE8)

    # ================================================================
    # Low-level I2C read/write methods
    # Each method uses instance-level buffers (self._buf*) instead of
    # class-level shared buffers, ensuring thread/instance safety.
    # ================================================================

    def _read_u8(self, address):
        """Read an 8-bit unsigned value from the specified register."""
        self._buf1[0] = address & 0xFF
        self.i2c.writeto(self.address, self._buf1)
        self.i2c.readfrom_into(self.address, self._buf1)
        return self._buf1[0]

    def _read_u16(self, address):
        """Read a 16-bit big-endian unsigned value from the specified register."""
        self._buf1[0] = address & 0xFF
        self.i2c.writeto(self.address, self._buf1)
        self.i2c.readfrom_into(self.address, self._buf2)
        return (self._buf2[0] << 8) | self._buf2[1]

    def _write_u8(self, address, val):
        """Write an 8-bit unsigned value to the specified register."""
        self._buf2[0] = address & 0xFF
        self._buf2[1] = val & 0xFF
        self.i2c.writeto(self.address, self._buf2)

    def _write_u16(self, address, val):
        """Write a 16-bit big-endian unsigned value to the specified register."""
        self._buf3[0] = address & 0xFF
        self._buf3[1] = (val >> 8) & 0xFF
        self._buf3[2] = val & 0xFF
        self.i2c.writeto(self.address, self._buf3)

    def _write_u32(self, address, val):
        """Write a 32-bit big-endian unsigned value to the specified register."""
        self._buf5[0] = address & 0xFF
        self._buf5[1] = (val >> 24) & 0xFF
        self._buf5[2] = (val >> 16) & 0xFF
        self._buf5[3] = (val >> 8) & 0xFF
        self._buf5[4] = val & 0xFF
        self.i2c.writeto(self.address, self._buf5)

    # ================================================================
    # SPAD information retrieval
    # ================================================================

    def _get_spad_info(self):
        """Query the sensor for SPAD count and type (aperture vs non-aperture).

        This information is needed during initialisation to correctly
        configure the reference SPAD map for accurate ranging.

        Returns:
            A tuple (count, is_aperture) where count is the number of
            reference SPADs and is_aperture indicates the SPAD type.
        """
        for pair in ((0x80, 0x01), (0xFF, 0x01), (0x00, 0x00), (0xFF, 0x06)):
            self._write_u8(pair[0], pair[1])
        self._write_u8(0x83, self._read_u8(0x83) | 0x04)
        for pair in ((0xFF, 0x07), (0x81, 0x01), (0x80, 0x01),
                     (0x94, 0x6B), (0x83, 0x00)):
            self._write_u8(pair[0], pair[1])

        # Wait for the SPAD info to become available
        start = time.ticks_ms()
        while self._read_u8(0x83) == 0x00:
            if (self.io_timeout_ms > 0
                    and time.ticks_diff(time.ticks_ms(), start)
                    >= self.io_timeout_ms):
                raise RuntimeError("Timeout waiting for VL53L0X!")

        self._write_u8(0x83, 0x01)
        tmp = self._read_u8(0x92)
        count = tmp & 0x7F
        is_aperture = ((tmp >> 7) & 0x01) == 1

        for pair in ((0x81, 0x00), (0xFF, 0x06)):
            self._write_u8(pair[0], pair[1])
        self._write_u8(0x83, self._read_u8(0x83) & ~0x04)
        for pair in ((0xFF, 0x01), (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00)):
            self._write_u8(pair[0], pair[1])

        return count, is_aperture

    # ================================================================
    # Reference calibration
    # ================================================================

    def _perform_single_ref_calibration(self, vhv_init_byte):
        """Perform a single reference calibration step.

        This is called twice during initialisation: once for VHV
        calibration (vhv_init_byte=0x40) and once for phase calibration
        (vhv_init_byte=0x00). Based on VL53L0X_perform_single_ref_calibration
        in the ST API.
        """
        self._write_u8(SYSRANGE_START, 0x01 | (vhv_init_byte & 0xFF))

        # Wait for the calibration to complete (interrupt status bit 0)
        start = time.ticks_ms()
        while (self._read_u8(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            if (self.io_timeout_ms > 0
                    and time.ticks_diff(time.ticks_ms(), start)
                    >= self.io_timeout_ms):
                raise RuntimeError("Timeout waiting for VL53L0X!")

        # Clear the interrupt and stop ranging
        self._write_u8(SYSTEM_INTERRUPT_CLEAR, 0x01)
        self._write_u8(SYSRANGE_START, 0x00)

    # ================================================================
    # VCSEL pulse period
    # ================================================================

    def _get_vcsel_pulse_period(self, vcsel_period_type):
        """Read the VCSEL pulse period for the specified ranging phase.

        The VCSEL period determines the laser pulse timing and affects
        both range and accuracy. The register value is decoded as:
            period = (register_value + 1) << 1

        Args:
            vcsel_period_type: VCSEL_PERIOD_PRE_RANGE or VCSEL_PERIOD_FINAL_RANGE

        Returns:
            The VCSEL period in PCLKs.
        """
        if vcsel_period_type == VCSEL_PERIOD_PRE_RANGE:
            val = self._read_u8(PRE_RANGE_CONFIG_VCSEL_PERIOD)
            return (((val) + 1) & 0xFF) << 1
        elif vcsel_period_type == VCSEL_PERIOD_FINAL_RANGE:
            val = self._read_u8(FINAL_RANGE_CONFIG_VCSEL_PERIOD)
            return (((val) + 1) & 0xFF) << 1
        return 255

    # ================================================================
    # Sequence step enables and timeouts
    # ================================================================

    def _get_sequence_step_enables(self):
        """Read which measurement sequence steps are currently enabled.

        The VL53L0X measurement sequence consists of up to 5 steps:
        TCC, DSS, MSRC, pre-range, and final-range. Each can be
        individually enabled or disabled.

        Returns:
            A tuple (tcc, dss, msrc, pre_range, final_range) of booleans.
        """
        sequence_config = self._read_u8(SYSTEM_SEQUENCE_CONFIG)
        tcc        = (sequence_config >> 4) & 0x1 > 0
        dss        = (sequence_config >> 3) & 0x1 > 0
        msrc       = (sequence_config >> 2) & 0x1 > 0
        pre_range  = (sequence_config >> 6) & 0x1 > 0
        final_range = (sequence_config >> 7) & 0x1 > 0
        return tcc, dss, msrc, pre_range, final_range

    def _get_sequence_step_timeouts(self, pre_range):
        """Read the timeout values for each enabled measurement sequence step.

        Args:
            pre_range: Boolean indicating whether pre-range step is enabled.

        Returns:
            A tuple of timeout values and VCSEL periods used for
            timing budget calculations.
        """
        pre_range_vcsel_period_pclks = self._get_vcsel_pulse_period(
            VCSEL_PERIOD_PRE_RANGE)

        msrc_dss_tcc_mclks = (self._read_u8(MSRC_CONFIG_TIMEOUT_MACROP) + 1) & 0xFF
        msrc_dss_tcc_us = _timeout_mclks_to_microseconds(
            msrc_dss_tcc_mclks, pre_range_vcsel_period_pclks)

        pre_range_mclks = _decode_timeout(
            self._read_u16(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI))
        pre_range_us = _timeout_mclks_to_microseconds(
            pre_range_mclks, pre_range_vcsel_period_pclks)

        final_range_vcsel_period_pclks = self._get_vcsel_pulse_period(
            VCSEL_PERIOD_FINAL_RANGE)
        final_range_mclks = _decode_timeout(
            self._read_u16(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI))

        if pre_range:
            final_range_mclks -= pre_range_mclks

        final_range_us = _timeout_mclks_to_microseconds(
            final_range_mclks, final_range_vcsel_period_pclks)

        return (msrc_dss_tcc_us, pre_range_us, final_range_us,
                final_range_vcsel_period_pclks, pre_range_mclks)

    # ================================================================
    # Signal rate limit property
    # ================================================================

    @property
    def signal_rate_limit(self):
        """The signal rate limit in mega counts per second (MCPS).

        This is the minimum signal rate (in 9.7 fixed-point format)
        that the sensor requires for a valid range reading. Lower values
        allow weaker returns but may increase noise.
        """
        val = self._read_u16(FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT)
        return val / (1 << 7)

    @signal_rate_limit.setter
    def signal_rate_limit(self, val):
        assert 0.0 <= val <= 511.99
        val = int(val * (1 << 7))
        self._write_u16(FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, val)

    # ================================================================
    # Measurement timing budget property
    # ================================================================

    @property
    def measurement_timing_budget(self):
        """The measurement timing budget in microseconds.

        The timing budget determines the maximum time the sensor spends
        on a single measurement. A longer budget yields higher accuracy
        but slower readings. The minimum budget is ~20ms.
        """
        budget_us = 1910 + 960  # Start overhead + end overhead

        tcc, dss, msrc, pre_range, final_range = \
            self._get_sequence_step_enables()
        step_timeouts = self._get_sequence_step_timeouts(pre_range)
        msrc_dss_tcc_us, pre_range_us, final_range_us, _, _ = step_timeouts

        if tcc:
            budget_us += (msrc_dss_tcc_us + 590)
        if dss:
            budget_us += (2 * (msrc_dss_tcc_us + 690))
        elif msrc:
            budget_us += (msrc_dss_tcc_us + 660)
        if pre_range:
            budget_us += (pre_range_us + 660)
        if final_range:
            budget_us += (final_range_us + 550)

        self._measurement_timing_budget_us = budget_us
        return budget_us

    @measurement_timing_budget.setter
    def measurement_timing_budget(self, budget_us):
        assert budget_us >= 20000

        used_budget_us = 1320 + 960  # Start (diff from get) + end overhead

        tcc, dss, msrc, pre_range, final_range = \
            self._get_sequence_step_enables()
        step_timeouts = self._get_sequence_step_timeouts(pre_range)
        msrc_dss_tcc_us, pre_range_us, _, \
            final_range_vcsel_period_pclks, pre_range_mclks = step_timeouts

        if tcc:
            used_budget_us += (msrc_dss_tcc_us + 590)
        if dss:
            used_budget_us += (2 * (msrc_dss_tcc_us + 690))
        elif msrc:
            used_budget_us += (msrc_dss_tcc_us + 660)
        if pre_range:
            used_budget_us += (pre_range_us + 660)
        if final_range:
            used_budget_us += 550
            if used_budget_us > budget_us:
                raise ValueError("Requested timeout too big.")
            final_range_timeout_us = budget_us - used_budget_us
            final_range_timeout_mclks = _timeout_microseconds_to_mclks(
                final_range_timeout_us, final_range_vcsel_period_pclks)
            if pre_range:
                final_range_timeout_mclks += pre_range_mclks
            self._write_u16(
                FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI,
                _encode_timeout(final_range_timeout_mclks))

        self._measurement_timing_budget_us = budget_us

    # ================================================================
    # Range reading (main measurement interface)
    # ================================================================

    @property
    def range(self):
        """Perform a distance measurement and return the result in mm.

        Automatically selects between single-shot and continuous mode
        depending on whether continuous mode has been started.
        """
        if self.continuous_mode:
            return self._read_range_continuous_millimeters()
        return self._read_range_single_millimeters()

    def _read_range_continuous_millimeters(self):
        """Read a range measurement when in continuous mode.

        Waits for a new measurement to become available by polling the
        interrupt status register, then reads the 16-bit range result.

        Returns:
            Distance in millimeters.
        """
        start = time.ticks_ms()
        while (self._read_u8(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            if (self.io_timeout_ms > 0
                    and time.ticks_diff(time.ticks_ms(), start)
                    >= self.io_timeout_ms):
                raise RuntimeError("Timeout waiting for VL53L0X!")

        # Read the 16-bit range value (register 0x14 + 10 byte offset)
        range_mm = self._read_u16(RESULT_RANGE_STATUS + 10)
        self._write_u8(SYSTEM_INTERRUPT_CLEAR, 0x01)
        return range_mm

    def _read_range_single_millimeters(self):
        """Perform a single-shot range measurement.

        Sets up the sensor for a one-off reading by writing the stop
        variable and triggering a measurement, then waits for the result.

        Returns:
            Distance in millimeters.
        """
        # Prepare for single measurement
        for pair in (
            (0x80, 0x01), (0xFF, 0x01), (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00),
            (SYSRANGE_START, 0x01),
        ):
            self._write_u8(pair[0], pair[1])

        # Wait for measurement to start (SYSRANGE_START bit 0 clears)
        start = time.ticks_ms()
        while (self._read_u8(SYSRANGE_START) & 0x01) > 0:
            if (self.io_timeout_ms > 0
                    and time.ticks_diff(time.ticks_ms(), start)
                    >= self.io_timeout_ms):
                raise RuntimeError("Timeout waiting for VL53L0X!")

        return self._read_range_continuous_millimeters()

    # ================================================================
    # Continuous measurement mode
    # ================================================================

    def start_continuous(self, period_ms=0):
        """Start continuous ranging measurements.

        Args:
            period_ms: Inter-measurement period in milliseconds.
                       If 0 (default), uses back-to-back mode where
                       the sensor measures as fast as possible.
                       If >0, uses timed mode with the given interval.
        """
        for pair in (
            (0x80, 0x01), (0xFF, 0x01), (0x00, 0x00),
            (0x91, self._stop_variable),
            (0x00, 0x01), (0xFF, 0x00), (0x80, 0x00),
        ):
            self._write_u8(pair[0], pair[1])

        if period_ms != 0:
            # Timed continuous mode: adjust period using oscillator calibration
            osc_calibrate_val = self._read_u16(OSC_CALIBRATE_VAL)
            if osc_calibrate_val != 0:
                period_ms *= osc_calibrate_val
            self._write_u32(SYSTEM_INTERMEASUREMENT_PERIOD, period_ms)
            self._write_u8(SYSRANGE_START, 0x04)  # Timed mode
        else:
            self._write_u8(SYSRANGE_START, 0x02)  # Back-to-back mode

        self.continuous_mode = True

    def stop_continuous(self):
        """Stop continuous ranging measurements."""
        for pair in (
            (SYSRANGE_START, 0x01), (0xFF, 0x01), (0x00, 0x00),
            (0x91, 0x00), (0x00, 0x01), (0xFF, 0x00),
        ):
            self._write_u8(pair[0], pair[1])
        self.continuous_mode = False

    # ================================================================
    # I2C address management
    # ================================================================

    def set_address(self, new_address):
        """Change the I2C address of this sensor instance.

        This is used when multiple VL53L0X sensors share the same I2C
        bus. After power-up, all sensors default to address 0x29. To
        differentiate them:
          1. Hold all sensors in reset (XSHUT low).
          2. Release one sensor at a time (XSHUT high).
          3. Call set_address() with a unique address for each sensor.

        Args:
            new_address: The new 7-bit I2C address (must not conflict
                         with other devices on the bus).
        """
        self._write_u8(I2C_SLAVE_DEVICE_ADDRESS, new_address & 0x7F)
        self.address = new_address
'''
# Test script
# Initialize I2C bus and sensor.
from machine import Pin, SoftI2C
i2c = SoftI2C(sda = Pin("P3B"), scl=Pin("P3A"))

from time import sleep_ms

from vl53lox import VL53LOX
vl53 = VL53L0X(i2c) # Create the distance sensor object
vl53.start_continuous() # Optionally start continuous measurement mode.

while True:
    print("Range: {0}mm".format(vl53.range))
    time.sleep(0.5)
'''