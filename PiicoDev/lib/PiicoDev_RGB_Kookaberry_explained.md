# Understanding `PiicoDev_RGB_Kookaberry.py`

This document explains how the `PiicoDev_RGB_Kookaberry.py` script works in a student-friendly way. The file is a MicroPython library for controlling a PiicoDev RGB LED module from a Kookaberry-compatible board over I2C, and it removes the need for the standard PiicoDev Unified Library by talking directly to the device registers.[file:1]

## What the script is for

The script is a reusable **library module**, not just a one-off program. It provides a `PiicoDev_RGB` class for controlling the three RGB LEDs on the PiicoDev RGB LED module, and it also provides a helper function called `wheel()` that converts colour values from HSV form into RGB form.[file:1]

In the header comments, the file says it is based on the Core Electronics PiicoDev libraries but adapted for Kookaberry firmware. The usage example shows that students first create an I2C bus, then create a `PiicoDev_RGB` object, and then send colours to the LEDs in a loop.[file:1]

## How the example works

The example in the file imports `Pin` and `SoftI2C`, creates an I2C connection using pins `P3A` and `P3B`, and then creates the RGB LED object with `leds = PiicoDev_RGB(bus=i2c)`. That means the rest of the program can control the RGB module through the `leds` variable.[file:1]

The loop then steps through hue values from 0 to 350 degrees in steps of 10. For each hue, it slowly increases brightness from 0 to 0.9, converts that hue and brightness into an RGB colour using `wheel(h=hue, v=brightness)`, and fills all LEDs with that colour.[file:1]

A simple way to think about this is that `hue` chooses the colour and `brightness` chooses how bright that colour looks. The result is a smooth glow effect that walks around the colour wheel.[file:1]

## Key ideas in the file

The script defines several constants such as `_baseAddr = 0x08`, `_regBright = 0x06`, and `_regLedVals = 0x07`. These are device addresses and register numbers, which are like numbered mailboxes inside the RGB module where the program reads or writes settings.[file:1]

For beginners, the most important idea is that I2C devices are controlled by sending bytes to specific register addresses. In this script, methods such as `setBrightness()`, `show()`, `clear()`, and `pwrLED()` all use `self.i2c.writeto_mem(...)` to send commands to the module.[file:1]

## The `wheel()` function

The `wheel(h, s=1, v=1)` function converts HSV colour values into RGB values. In this script, `h` is expected to be in the range 0 to 1 rather than 0 to 360 degrees, so the example converts degrees into a fraction by using `hue = x / 360`.[file:1]

HSV is often easier for beginners to think about than RGB. Hue means the basic colour, saturation means how strong the colour is, and value means brightness.[file:1]

If `s` is zero, the function returns a grey shade where red, green, and blue are all equal. Otherwise, the function works out which of six colour sectors the hue belongs to, calculates intermediate values, and returns one RGB combination such as `[v, t, p]` or `[q, v, p]` depending on the sector.[file:1]

For example, a hue near 0 gives red, a hue around one-third gives green, and a hue around two-thirds gives blue. This is why the function is called `wheel()` because it walks around the colour wheel.[file:1]

## The `PiicoDev_RGB` class

The class groups together the functions needed to control the RGB module. When a class is used to create an object, that object stores its own settings such as the I2C bus, the device address, the current LED values, and the brightness level.[file:1]

### `__init__()`

The `__init__(self, bus=None, addr=_baseAddr, id=None, bright=50)` method runs automatically when the object is created. It stores the I2C bus in `self.i2c`, chooses the device address either from `addr` or from a four-bit `id` list, creates storage for three LEDs with `self.led = [[0,0,0],[0,0,0],[0,0,0]]`, and then tries to set the brightness and show the initial state.[file:1]

If the module cannot be found, the code prints `* Couldn't find a device - check switches and wiring` and then raises the error again. That is useful because students get both a friendly hint and the real error message.[file:1]

### `setPixel()`

`setPixel(self, n, c)` changes one LED in the internal list `self.led`. The value `n` is the LED number, and `c` is a colour such as `[255, 0, 0]` for red.[file:1]

This method only changes the stored value in memory. It does not send the change to the hardware until `show()` is called.[file:1]

### `show()`

`show(self)` sends the current colour data for all three LEDs to the module. It builds one byte buffer from `self.led[0]`, `self.led[1]`, and `self.led[2]`, and writes that buffer to the LED value register `_regLedVals`.[file:1]

This is an important programming pattern for students to notice: first prepare the data, then send it to the device. That makes it possible to update several LEDs and display them all at once.[file:1]

### `fill()`

`fill(self, c)` sets every LED in `self.led` to the same colour and then immediately calls `self.show()`. This is why the example can change all LEDs with one line.[file:1]

Because `fill()` automatically shows the result, it is easier for beginners than calling `setPixel()` three times and then remembering to call `show()`. The trade-off is that it always makes all LEDs the same colour.[file:1]

### `setBrightness()`

`setBrightness(self, x)` changes the module brightness. It rounds the value, makes sure it stays in the range 0 to 255, writes the brightness byte to register `_regBright`, and then waits 1 millisecond.[file:1]

A good teaching point here is that many hardware devices need short delays after commands. The `sleep_ms(1)` call gives the module a brief moment to process the new setting.[file:1]

### `clear()`

`clear(self)` sends a clear command to register `_regClear`, resets the internal LED list to all zero values, and waits 1 millisecond. Zero for red, green, and blue means the LEDs are off.[file:1]

### `setI2Caddr()`

`setI2Caddr(self, newAddr)` changes the device address. It first checks that the new address is between `0x08` and `0x77`, writes the new address to the module, updates `self.addr`, and then waits 5 milliseconds.[file:1]

This method is useful when more than one module is connected to the same I2C bus, because each device needs a unique address. The `assert` statement also shows a simple way to stop bad input before it causes harder-to-find problems.[file:1]

### `readFirmware()` and `readID()`

`readFirmware(self)` reads two bytes from the firmware version register and returns them in the order `(major, minor)`. `readID(self)` reads one byte from the device ID register and returns that value.[file:1]

These methods are examples of reading from hardware instead of writing to it. They help a program check that the correct device is connected and find out what firmware it is running.[file:1]

### `pwrLED()`

`pwrLED(self, state)` controls the power LED on the module. It uses an `assert` statement to require either `True` or `False`, writes that value to the control register, and then pauses for 1 millisecond.[file:1]

This is a useful beginner example because it shows that Boolean values can directly represent an ON/OFF choice in code. `True` means on and `False` means off.[file:1]

## Internal data structure

The object keeps the LED colours in `self.led`, which starts as `[[0,0,0],[0,0,0],[0,0,0]]`. Each inner list represents one LED, and each list holds red, green, and blue values from 0 to 255.[file:1]

This means a value like `[[255,0,0],[0,255,0],[0,0,255]]` would represent red, green, and blue across the three LEDs. That is a helpful mental model when students start editing the code themselves.[file:1]

## A typical control sequence

A beginner-friendly way to think about the library is as a sequence:

1. Create the I2C bus.
2. Create the `PiicoDev_RGB` object.
3. Choose colours, either directly in RGB or by using `wheel()`.
4. Store colours with `setPixel()` or `fill()`.
5. Send the colours to the hardware with `show()` if needed.[file:1]

In the supplied example, `fill()` is used, so step 5 happens automatically. In a custom program that uses `setPixel()`, the extra `show()` step is required before students will see any change on the LEDs.[file:1]

## Things beginners should notice

- `wheel()` uses hue from 0 to 1, not 0 to 360, so dividing by 360 is important in the example.[file:1]
- `setPixel()` updates the stored LED data, while `show()` sends that data to the real hardware.[file:1]
- `fill()` is a shortcut that sets all LEDs to one colour and then calls `show()` for you.[file:1]
- `assert` statements are used to catch invalid input early, such as a bad I2C address or an invalid power LED state.[file:1]
- Small `sleep_ms()` delays are included because hardware often needs a short settling time after a command.[file:1]

## Simple example for students

```python
from machine import Pin, SoftI2C
from PiicoDev_RGB_Kookaberry import PiicoDev_RGB

# Set up I2C
bus = SoftI2C(sda=Pin("P3B"), scl=Pin("P3A"))

# Create the RGB LED object
leds = PiicoDev_RGB(bus=bus)

# Turn all LEDs red
leds.fill([255, 0, 0])
```

This example works because `fill()` updates every LED and then immediately calls `show()`. If students later switch to `setPixel()`, they should remember to call `show()` after setting the colours.[file:1]

## Teaching value of the script

This file is a good teaching example because it shows several core MicroPython ideas in one place: importing modules, creating objects from classes, storing data in lists, using functions with parameters, writing to hardware registers, and handling errors with `assert` and `try/except`.[file:1]

It also helps students see the difference between a library and an application. The library contains reusable building blocks, while the example code shows how another script can import those building blocks and use them to make the LEDs do something visible.[file:1]
