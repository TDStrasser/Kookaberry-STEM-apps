# Explaining `PiicoDev_VL53L1X_Kookaberry.py`

This document explains how the `PiicoDev_VL53L1X_Kookaberry.py` script works for students and beginners who are learning MicroPython on the Kookaberry. The script is a library for a PiicoDev VL53L1X distance sensor and is designed to work with the Kookaberry MicroPython environment rather than the original PiicoDev unified library. [file:1]

## What the script is for

The script provides a Python class called `PiicoDev_VL53L1X` that lets a Kookaberry program talk to a VL53L1X distance sensor over I2C. It handles sensor startup, register reading and writing, distance measurement, and optional I2C address changes. [file:1]

In simple terms, this file is a **driver**. A driver is code that knows how to control a piece of hardware so other programs can use it more easily. [file:1]

## The example at the top

Near the top of the file, the script includes a short usage example. That example shows how to set up the Kookaberry display, create a software I2C bus on pins `P3B` and `P3A`, create the distance sensor object, and then repeatedly read and display the measured distance in millimetres until Button A is pressed. [file:1]

```python
from time import sleep_ms
from machine import Pin, SoftI2C
import kooka

disp = kooka.display

i2c = SoftI2C(sda=Pin("P3B"), scl=Pin("P3A"))
distSensor = PiicoDev_VL53L1X(bus=i2c)

while not kooka.button_a.was_pressed():
    disp.clear()
    distance = distSensor.read()
    disp.print(str(distance) + ' mm')
    sleep_ms(100)
```

This example is important because it shows the normal pattern for using the library: set up I2C, create the sensor object, call `read()`, and display or use the result. [file:1]

## Imports and constants

The script imports `sleep_ms` from the `time` module. This function pauses the program for a short number of milliseconds, which gives the sensor time to reset and finish setup steps. [file:1]

A very large constant named `VL51L1X_DEFAULT_CONFIGURATION` appears near the top of the file. This is a block of bytes that stores the sensor's startup configuration values, and the program writes those values into the sensor's internal registers during initialisation. [file:1]

Students do not need to memorise every byte in this configuration table. The important idea is that many sensors need a set of low-level setup values before they can work properly, and this list provides those values. [file:1]

## The class structure

The main part of the file is the `PiicoDev_VL53L1X` class. A class is like a blueprint that groups related data and functions together so one object can represent one sensor. [file:1]

When a program creates `distSensor = PiicoDev_VL53L1X(bus=i2c)`, it makes an object that stores the I2C bus, remembers the sensor address, and provides methods such as `read()`, `reset()`, and `change_addr()`. [file:1]

## The `__init__()` method

The `__init__()` method runs automatically when the object is created. In this script, it stores the I2C bus in `self.i2c`, stores the sensor address in `self.addr`, sets `self.status` to `None`, resets the sensor, checks the sensor model ID, writes the default configuration block, and then updates another register value used during ranging setup. [file:1]

### Step-by-step startup

1. `self.i2c = bus` stores the I2C connection so the object can talk to the sensor later. [file:1]
2. `self.addr = address` stores the device address, which defaults to `0x29`. [file:1]
3. `self.status = None` creates a place to store the latest measurement status. [file:1]
4. `self.reset()` performs a hardware-style reset through a control register. [file:1]
5. `sleep_ms(1)` gives the sensor a brief pause after reset. [file:1]
6. `self.read_model_id()` reads register `0x010F` and checks that the returned ID is `0xEACC`. If not, the code raises a `RuntimeError` telling the user to check the wiring. [file:1]
7. The script writes `VL51L1X_DEFAULT_CONFIGURATION` into the sensor starting at register `0x2D`. [file:1]
8. After another pause, the script updates register `0x001E` using a value read from register `0x0022`, multiplied by 4. [file:1]

This startup sequence is a good example of why device drivers exist. A beginner program can create one object, but inside that object the library quietly performs many detailed setup actions. [file:1]

## Register helper methods

Several short methods make it easier to read from and write to the sensor's registers. Registers are small storage locations inside the sensor chip that hold settings and measurement results. [file:1]

### `writeReg(self, reg, value)`

This method writes one byte to a 16-bit register address using `writeto_mem()`. It is used for single-byte settings such as reset control. [file:1]

### `writeReg16Bit(self, reg, value)`

This method writes a 16-bit value as two bytes, high byte first and low byte second. This is needed because some sensor registers store values larger than 255. [file:1]

### `readReg(self, reg)`

This method reads one byte from a register and returns that single value. It is useful for simple status or control registers. [file:1]

### `readReg16Bit(self, reg)`

This method reads two bytes from a register and combines them into one number using `(data[0] << 8) + data[1]`. That means the first byte becomes the high part of the number and the second byte becomes the low part. [file:1]

These helper methods are useful for students because they hide repetitive I2C details. Other parts of the class can call clear method names instead of repeating byte-handling code each time. [file:1]

## Sensor identification

The method `read_model_id()` reads a 16-bit value from register `0x010F`. The script expects this value to be `0xEACC`, and that check is used during startup to confirm that the correct sensor is connected and responding. [file:1]

This check helps catch wiring mistakes early. If the wrong device is connected, or if the I2C connection is not working, the script stops with a clear error message instead of continuing with unreliable behaviour. [file:1]

## Resetting the sensor

The `reset()` method writes `0x00` to register `0x0000`, waits 100 milliseconds, and then writes `0x01` to the same register. This sequence resets the sensor hardware through software control. [file:1]

A reset is often used to place a device into a known starting state. That makes later configuration more reliable. [file:1]

## How `read()` works

The `read()` method is the most important method for most users because it gets the measured distance from the sensor. It attempts to read 17 bytes starting from register `0x0089`, which the comment identifies as `RESULT__RANGE_STATUS`. [file:1]

If the I2C read fails, the method prints an error using `i2c_err_str.format(self.addr)` and returns `NaN`, meaning “not a number.” The current script text shows `i2c_err_str` being used but not defined inside this file, so that message depends on something outside this script or may need correction for standalone use. [file:1]

### Values extracted from the result block

After the 17-byte read, the script unpacks several pieces of data:

- `range_status = data[0]`, a status code for the measurement. [file:1]
- `stream_count = data[2]`, used in one of the status decisions. [file:1]
- `dss_actual_effective_spads_sd0 = (data[3] << 8) + data[4]`, a sensor internal value that is read but not used later in this function. [file:1]
- `ambient_count_rate_mcps_sd0 = (data[7] << 8) + data[8]`, another sensor measurement value that is read but not used later in this function. [file:1]
- `final_crosstalk_corrected_range_mm_sd0 = (data[13] << 8) + data[14]`, the final distance value in millimetres. [file:1]
- `peak_signal_count_rate_crosstalk_corrected_mcps_sd0 = (data[15] << 8) + data[16]`, another internal result value that is read but not used later. [file:1]

For beginners, the key line is the one that builds `final_crosstalk_corrected_range_mm_sd0`. That is the actual distance reading returned by the method. [file:1]

### Status checking

The script converts several numeric `range_status` values into text labels and stores the result in `self.status`. For example, some values produce `"HardwareFail"`, `"SignalFail"`, `"WrapTargetFail"`, `"XtalkSignalFail"`, or `"OK"`. [file:1]

This design is helpful because the code separates two ideas: the measured distance itself and the quality or meaning of that reading. A program can read the returned distance and also inspect `distSensor.status` to see whether the measurement was valid. [file:1]

### Return value

If `range_status == 9` and `stream_count` is not zero, the method sets `self.status` to `"OK"` and returns `final_crosstalk_corrected_range_mm_sd0`. In the current script, the `return` line appears inside that final `elif range_status == 9:` block, so other status cases set `self.status` but do not explicitly return a distance value. [file:1]

That means beginners should understand an important programming point: where the `return` statement is placed changes the behaviour of the whole function. In this version of the script, only the final `OK` case clearly returns a distance result. [file:1]

## Changing the I2C address

The method `change_addr(self, new_addr)` writes a new 7-bit address to register `0x0001`, waits 50 milliseconds, and then updates `self.addr` so future communication uses the new address. This can be useful when more than one identical I2C sensor is connected and each device needs a unique address. [file:1]

The line `new_addr & 0x7F` keeps the value within the normal 7-bit I2C address range. That bitwise operation may look advanced, but students can think of it as a safety step that removes any extra upper bits. [file:1]

## How the script uses I2C

I2C is a communication system that lets a microcontroller talk to devices such as sensors using a clock line and a data line. In this script, the Kookaberry creates the bus with `SoftI2C`, then the library uses methods such as `readfrom_mem()` and `writeto_mem()` to talk to specific register addresses inside the sensor. [file:1]

The argument `addrsize=16` appears throughout the script because this sensor uses 16-bit register addresses. That means each register location is identified by two bytes instead of one. [file:1]

## Important beginner ideas

This script teaches several useful MicroPython ideas:

- How to wrap hardware control code inside a class. [file:1]
- How an object stores information using `self`, such as `self.i2c`, `self.addr`, and `self.status`. [file:1]
- How helper methods reduce repeated code. [file:1]
- How sensors are often configured by reading and writing registers. [file:1]
- How programs can separate a measurement result from a measurement status. [file:1]

## A simple mental model

A good way to think about the script is this:

1. The class opens a communication path to the sensor. [file:1]
2. It resets and configures the sensor so it is ready. [file:1]
3. It reads a block of result bytes from the sensor. [file:1]
4. It converts some of those bytes into meaningful numbers. [file:1]
5. It returns the distance reading and stores a status message. [file:1]

That pattern appears in many hardware libraries, not just this one. [file:1]

## Things students should notice

There are a few details in the file that are especially worth discussing in class or during practice. The dependency note mentions an RFID module even though the script is for a distance sensor, which suggests that part of the header may have been copied from another file and not fully updated. [file:1]

The example loop shown in the header also appears to need indentation under the `while` statement to run correctly as normal Python code. In addition, the error message in `read()` refers to `i2c_err_str`, but that name is not defined anywhere in the visible file text. [file:1]

These are useful teaching examples because real code often needs careful review, not just blind copying. Reading code critically is an important skill for new programmers. [file:1]

## Suggested beginner improvements

If this library were being refined for students, these changes would make it easier to learn from:

- Add docstrings to each method explaining its purpose. [file:1]
- Add comments that explain why certain registers are read or written. [file:1]
- Move the `return` statement in `read()` so the distance value is returned more consistently, or clearly document that only valid readings are returned. [file:1]
- Define or remove `i2c_err_str` so the error handling is complete within the file. [file:1]
- Correct the example formatting and dependency notes in the header. [file:1]

## Example of using the status value

A student program could use both the distance and the status like this:

```python
distance = distSensor.read()
print(distance)
print(distSensor.status)
```

This is useful because a number by itself does not always tell the whole story. A distance reading together with a status message can help a student decide whether the measurement should be trusted. [file:1]

## Final understanding

At a beginner level, the most important thing to understand is that this file is a reusable library for a distance sensor. It hides the difficult low-level register operations and gives the user a simpler interface based mainly on creating an object and calling `read()`. [file:1]

Once students understand that pattern, they will be better prepared to read other MicroPython sensor libraries and to write their own hardware classes in the future. [file:1]
