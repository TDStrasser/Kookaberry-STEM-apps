# Explaining `PiicoDev_Servo_Kookaberry.py`

This document explains how the `PiicoDev_Servo_Kookaberry.py` script works and is aimed at students who are new to MicroPython. The script is a Kookaberry-ready version of a PiicoDev servo driver and removes the original dependency on the PiicoDev Unified Library while keeping the main job of controlling a PCA9685-based servo driver over I2C. [file:1]

## What the script does

The script gives a Kookaberry program a simple way to control servos through a PiicoDev Servo Driver board. It does this by talking to a PCA9685 chip, which generates PWM signals for the servo channels. [file:1]

There are three main ideas in the file:

- A helper function called `remap()` that converts one numeric range into another. [file:1]
- A `PCA9685` class that talks directly to the servo driver chip using I2C. [file:1]
- A `PiicoDev_Servo` class that lets a user set a servo by angle or speed instead of by low-level PWM values. [file:1]

## The import at the top

The first active lines try to import `pack` and `unpack` from `ustruct`, and if that fails, they import them from `struct`. This makes the code more portable across MicroPython builds and other Python-style environments that may name the module differently. [file:1]

```python
try: from ustruct import pack, unpack
except: from struct import pack, unpack
```

`pack()` and `unpack()` are used later when the script sends or reads 16-bit values to and from the PCA9685 registers. In simple terms, they help turn numbers into bytes and bytes back into numbers. [file:1]

## The `remap()` function

The `remap()` function takes a value from one range and converts it to another range. In this script, it is used by the `speed` property so that a speed command in the range `-1` to `1` can be turned into a matching PWM duty value for the servo output. [file:1]

```python
def remap(old_val, old_min, old_max, new_min, new_max):
    """Remap one range of values to another range and saturate for out-of-bounds"""
    x = (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min
    return min(new_max,max(x,new_min))
```

A useful detail is that the function also clamps the answer so it cannot go below the new minimum or above the new maximum. That means out-of-range inputs are forced back into a safe range. [file:1]

## The `PCA9685` class

The `PCA9685` class is the low-level part of the script. Its job is to communicate with the PWM driver chip over I2C and set up the chip so it can generate servo-friendly pulses. [file:1]

### `__init__()`

When a `PCA9685` object is created, the constructor stores the I2C object, stores the chip address, resets the chip, and sets the PWM frequency to 50 Hz. The 50 Hz setting is important because many hobby servos expect a control signal around that rate. [file:1]

```python
def __init__(self, i2c, address=0x44):
    self.i2c = i2c
    self.address = address
    self.reset()
    self.frequency=50 # Hz
```

### `_write()` and `_read()`

These two methods are small helper methods. `_write()` sends one byte to a register in the PCA9685, and `_read()` reads one byte back from a register. [file:1]

Students do not usually call these methods directly. They are internal building blocks used by the rest of the class. [file:1]

### `reset()`

The `reset()` method writes `0x00` to register `0x00`. This returns the chip to a known starting state before the rest of the setup happens. [file:1]

### The `frequency` property

The `frequency` property lets the script set the PWM output frequency. In the setter, the code calculates a `prescale` value, writes it to the chip, briefly pauses with `sleep_ms(1)`, then restarts the oscillator with auto-increment enabled. [file:1]

```python
@frequency.setter
def frequency(self,f):
    prescale = int(25000000.0 / 4096.0 / f + 0.5)
    old_mode = self._read(0x00)
    self._write(0x00, (old_mode & 0x7F) | 0x10)
    self._write(0xfe, prescale)
    self._write(0x00, old_mode)
    sleep_ms(1)
    self._write(0x00, old_mode | 0xa1)
    self._frequency = 1/((prescale-0.5)*4096/25e6)
```

This is one of the most advanced parts of the file. Beginners do not need to memorise the math, but it helps to know that the code is configuring the chip so each servo channel produces pulses at the correct rate. [file:1]

### `pwm()`

The `pwm()` method can either read or write the raw PWM timing values for one channel. If `on` and `off` are not supplied, it reads four bytes from the correct register block and returns two 16-bit numbers; otherwise it packs the numbers into bytes and writes them to the chip. [file:1]

This is a good example of a method with two jobs: read mode and write mode. That pattern is common in device-driver code. [file:1]

### `duty()`

The `duty()` method is a friendlier way to work with a channel's PWM value. It can read the duty cycle or write a new one, and it checks that written values stay between `0` and `4095`, raising a `ValueError` if the number is out of range. [file:1]

The PCA9685 uses 12-bit PWM resolution, which is why the valid range is `0` to `4095`. The method also has an `invert` option and handles special cases for fully off and fully on outputs. [file:1]

## The `PiicoDev_Servo_Driver` class

`PiicoDev_Servo_Driver` is a child class of `PCA9685`. It mainly adds PiicoDev-style setup logic on top of the lower-level chip class. [file:1]

```python
class PiicoDev_Servo_Driver(PCA9685):
```

In its constructor, the code can calculate a device address from the `asw` argument if `asw` is given as a two-item list containing only `0` or `1`. If `asw` is missing or invalid, the code falls back to the default address. [file:1]

```python
def __init__(self, bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, asw=None):
    if type(asw) is list and len(asw) is 2 and all(element in [0,1] for element in asw):
        addr = _I2C_ADDRESS + asw[0] + 2*asw[1]
    else:
        addr = address
    PCA9685.__init__(self, bus, address=addr)
```

Notice that the Kookaberry version does not call the original PiicoDev unified I2C helper. Instead, it expects the program to pass in an already-created I2C bus object. That is one of the key changes mentioned in the file header. [file:1]

## The `PiicoDev_Servo` class

This class is the part that most student programs will care about. It turns raw PWM numbers into more meaningful servo controls such as angle and speed. [file:1]

### Constructor

The constructor receives the servo controller object, a channel number, and several timing settings such as frequency, minimum pulse width, maximum pulse width, and servo travel in degrees. It stores these values and calculates the matching duty-cycle limits for the servo. [file:1]

```python
def __init__(self, controller, channel, freq=50, min_us=600, max_us=2400, degrees=180, midpoint_us=None, range_us=None):
    self.period = 1_000_000/freq # microseconds
    if midpoint_us is not None and range_us is not None:
        min_us = midpoint_us - range_us/2
        max_us = midpoint_us + range_us/2
    self.min_duty = self._us2duty(min_us)
    self.max_duty = self._us2duty(max_us)
    self._degrees = degrees
    self.freq = freq
    self.controller = controller
    self.channel = {4:0,3:1,2:2,1:3}[channel]
```

A particularly important line is the channel mapping dictionary: `{4:0,3:1,2:2,1:3}`. This means the silk-screened channel labels on the board are mapped to the underlying PCA9685 channels in reverse order for channels 1 to 4. [file:1]

### `_us2duty()`

This helper method converts a pulse width in microseconds into a 12-bit PWM duty number. That conversion is needed because servo timing is usually described in microseconds, but the chip itself uses duty counts. [file:1]

### The `angle` property

The `angle` property lets a student write simple code such as `servo.angle = 90`. Inside the setter, the script calculates the matching duty value between the configured minimum and maximum duty limits, clamps that result to a safe range, writes it to the controller, and stores the clamped angle value. [file:1]

```python
@angle.setter
def angle(self, x):
    duty = self.min_duty + (self.max_duty - self.min_duty) * x / self._degrees
    duty = min(self.max_duty, max(self.min_duty, int(duty)))
    self.controller.duty(self.channel, duty)
    self._angle = min(self._degrees,max(x,0))
```

This is a strong beginner-friendly design because users can think in angles instead of register values. If a student accidentally sets an angle below `0` or above the configured maximum, the value is saturated into range instead of being sent unchecked. [file:1]

### The `speed` property

The `speed` property is intended for continuous-rotation servos rather than standard position servos. It accepts values from `-1` to `1`, stores the requested speed, remaps that range into PWM duty values, and writes the result to the servo controller. [file:1]

```python
@speed.setter
def speed(self,x):
    self._speed = x
    duty = int(remap(x, -1, 1, self.min_duty, self.max_duty)+0.5)
    self.controller.duty(self.channel, duty)
```

A value near `0` is the stop point, while negative and positive values command motion in opposite directions. The exact behaviour depends on the servo model and how it has been calibrated. [file:1]

### `release()`

The `release()` method sends a duty value of `0` to the channel. In practical terms, this tells the controller to stop actively driving that servo output. [file:1]

## The test script

At the bottom of the file there is a multi-line quoted test script. Because it is inside quotes, it acts like an example block rather than code that runs automatically when the file is imported. [file:1]

The example imports `SoftI2C` and `Pin`, creates an I2C bus on `P3A` and `P3B`, creates the servo driver object, then creates two servo objects on channels `1` and `4`. It then steps both servos through `0`, `90`, and `180` degrees with one-second pauses, and finally performs a slow sweep from `0` to `175` degrees in steps of `5`. [file:1]

```python
from machine import SoftI2C, Pin
from time import sleep_ms

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)
servo_1 = PiicoDev_Servo(controller, 1)
servo_4 = PiicoDev_Servo(controller, 4)
```

This example is useful because it shows the normal order of use:

1. Create the I2C bus. [file:1]
2. Create the servo driver controller. [file:1]
3. Create one or more servo objects. [file:1]
4. Set servo angles or speeds. [file:1]

## How a student would use it

A beginner program would usually place `PiicoDev_Servo_Kookaberry.py` in the `/lib` folder, then import the classes into a main script. The main script would create the I2C interface first, then the controller, then the servo objects. [file:1]

A simple example looks like this:

```python
from machine import SoftI2C, Pin
from time import sleep_ms
from PiicoDev_Servo_Kookaberry import PiicoDev_Servo_Driver, PiicoDev_Servo

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)
servo = PiicoDev_Servo(controller, 1)

servo.angle = 0
sleep_ms(1000)
servo.angle = 90
sleep_ms(1000)
servo.angle = 180
```

That script works at a much higher level than directly writing chip registers. The classes in the file hide the low-level details so the student can focus on what the servo should do. [file:1]

## Beginner tips

- `angle` is for normal position servos; `speed` is mainly for continuous-rotation servos. [file:1]
- Servo movement limits vary, so not every servo will safely reach a true `0` to `180` degrees range. The defaults in the script are common starting values, not a guarantee for every model. [file:1]
- The script clamps several values into range, which helps avoid some mistakes, but students should still test movement carefully. [file:1]
- The class expects the channel argument to be one of `1`, `2`, `3`, or `4` because of the fixed mapping dictionary used in the constructor. [file:1]

## Key idea to remember

This file is a layered design. The `PCA9685` class handles low-level chip communication, `PiicoDev_Servo_Driver` adapts that for the Kookaberry/PiicoDev setup, and `PiicoDev_Servo` provides the student-friendly interface that uses angles and speeds. [file:1]
