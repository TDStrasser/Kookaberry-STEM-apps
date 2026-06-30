# Explaining the `PiicoDev_SSD1306_Kookaberry.py` Script

This document explains how the `PiicoDev_SSD1306_Kookaberry.py` script works for students who are new to MicroPython and small display modules. The script is a MicroPython driver for a PiicoDev SSD1306 OLED display, adapted so it can run in the Kookaberry environment without depending on the original PiicoDev unified library [file:1].

## What the script does

The script gives a Kookaberry program a simple way to control a 128 by 64 pixel OLED display over I2C, which is a common communication method used by small electronic modules [file:1]. It sets up the display, stores pixel data in memory, sends that data to the screen, and provides helper functions for drawing shapes, showing text, loading images, and plotting simple graphs [file:1].

In other words, the script acts like a translator between student code and the SSD1306 display hardware. A student can call methods such as `fill()`, `pixel()`, `line()`, `rect()`, `text()`, and `show()` without needing to understand every low-level command sent to the display chip [file:1].

## Script structure

The script is organised into four main parts [file:1]:

- A group of constant values, such as `_SET_CONTRAST` and `_SET_DISP`, which represent command codes understood by the SSD1306 display controller [file:1].
- A main display class called `PiicoDev_SSD1306`, which contains methods for initialising the screen, writing commands, writing pixel data, and drawing extra shapes [file:1].
- A helper class called `graph2D`, which stores recent values and draws a basic graph on the display [file:1].
- A child class called `PiicoDev_SSD1306_MicroPython` plus the `create_PiicoDev_SSD1306()` function, which make it easier to create and use the display object [file:1].

Near the end of the file there is also a block of test code inside triple quotes. Because it is inside a triple-quoted string, it does not run as part of the driver, but it gives examples of how the display can be used in a real Kookaberry program [file:1].

## The constants at the top

At the top of the file, the script defines many names such as `_SET_CONTRAST = 0x81` and `_SET_DISP = 0xAE` [file:1]. These are hexadecimal command values used by the SSD1306 chip, and using names instead of raw numbers makes the code easier to read and maintain [file:1].

The script also defines `WIDTH = 128` and `HEIGHT = 64`, which match the resolution of the OLED display this driver is written for [file:1]. These values are used throughout the code when calculating memory size, screen positions, and drawing limits [file:1].

## Imported modules

The script imports several MicroPython modules and functions [file:1]:

- `cos`, `sin`, and `radians` from `math`, used for drawing arcs [file:1].
- `sleep_ms` from `utime`, used in the example test code for short delays [file:1].
- `pack_into` from `ustruct`, although in this version it is imported but not used later in the script [file:1].
- `framebuf`, which is very important because it provides the `FrameBuffer` class used for drawing graphics in memory before showing them on the display [file:1].

For beginners, `framebuf` is one of the key ideas in the whole script. It allows drawing to happen in a memory buffer first, and then the whole buffer is copied to the OLED screen when `show()` is called [file:1].

## The main display class

The class `PiicoDev_SSD1306` inherits from `framebuf.FrameBuffer`, which means it gains useful built-in drawing methods such as `fill()`, `pixel()`, `line()`, `rect()`, and text-related features supported by the Kookaberry environment [file:1]. This is a common MicroPython pattern because it lets a custom display driver reuse standard graphics tools instead of creating everything from scratch [file:1].

### `init_display()`

The `init_display()` method prepares the display to be used [file:1]. It sets the width and height, calculates the number of pages with `HEIGHT // 8`, and creates `self.buffer`, a `bytearray` that will hold the display image in memory [file:1].

A **page** is a horizontal band of 8 pixels in height, which is how SSD1306 displays store their screen data internally. Since the display is 64 pixels high, `64 // 8` gives 8 pages, and the total buffer size becomes `8 * 128 = 1024` bytes [file:1].

After creating the buffer, the method sends a series of setup commands in a loop using `self.write_cmd(cmd)` [file:1]. These commands turn the display off during setup, select horizontal memory addressing, define the screen layout, set timing and voltage options, enable the charge pump, and finally turn the display on [file:1].

Students do not need to memorise each command, but it is useful to know that this block is the hardware setup stage. Without it, the display chip would not be properly configured to show the data in the buffer [file:1].

### `poweroff()` and `poweron()`

These methods send one command each to switch the display off or on [file:1]. They are useful when a program wants to blank the display without erasing the stored buffer contents [file:1].

### `setContrast()`

This method sends the contrast command followed by the contrast value chosen by the user [file:1]. Contrast changes how bright the display appears, although the exact visual result can vary slightly between OLED modules [file:1].

### `invert()`

This method swaps the display between normal and inverted colours by changing the SSD1306 normal/invert setting [file:1]. On a monochrome OLED, that means lit pixels can become dark and dark pixels can become lit [file:1].

### `rotate()`

This method changes the display orientation by modifying the COM output direction and segment remapping settings [file:1]. In simple terms, it flips the way the display maps memory positions to the physical screen so the image can be viewed in the opposite orientation [file:1].

### `show()`

The `show()` method is one of the most important methods in the script [file:1]. It sets the column and page address range for the full screen, then sends the entire contents of `self.buffer` to the display using `self.write_data(self.buffer)` [file:1].

This means drawing commands usually happen in two stages: first the program changes the buffer, then `show()` copies that buffered picture to the real display. If a student forgets to call `show()`, the new graphics may exist in memory but will not appear on the screen yet [file:1].

## Sending data over I2C

### `write_cmd()`

The `write_cmd()` method sends a single command byte to the display using `self.i2c.writeto_mem()` [file:1]. It uses `0x80` as the control byte, which tells the SSD1306 that the following byte should be treated as a command rather than display data [file:1].

The method also uses `try` and `except` so the script can catch communication problems [file:1]. If an error happens, it prints an error message using `i2c_err_str.format(self.addr)` and sets `self.comms_err = True`, although beginners should notice that `i2c_err_str` is not defined inside this file, so it must exist elsewhere in the Kookaberry environment or the error handler could itself cause a problem [file:1].

### `write_data()`

The `write_data()` method sends a block of display data bytes to the OLED [file:1]. It uses a control byte of `0x40`, stored in `self.write_list[0]`, which tells the SSD1306 that the following bytes are display RAM data rather than commands [file:1].

This method is mainly used by `show()`, which sends the full 1024-byte screen buffer to the display in one operation [file:1]. Like `write_cmd()`, it also catches I2C communication errors and updates `self.comms_err` [file:1].

## Extra drawing functions

### `circ()`

The `circ()` method draws a circle by checking every pixel in a square around the centre point and testing whether that pixel lies inside the circle equation area [file:1]. When `t == 1`, the method fills the whole circle, and when `t` is not 1, it draws a ring-like outline whose thickness depends on `t` [file:1].

Although this is not the fastest possible way to draw a circle, it is easier for beginners to understand because it works directly with coordinates and repeated `pixel()` calls [file:1].

### `arc()`

The `arc()` method draws part of a circle between a start angle and an end angle [file:1]. It uses `cos()` and `sin()` to convert angles into x and y positions, then turns on those pixels one by one [file:1].

This is a good example of how maths can be used in graphics programming. The method loops through angles and radius values, which lets it draw a thin or thicker arc depending on the thickness setting `t` [file:1].

### `load_pbm()`

The `load_pbm()` method reads a PBM image file in binary `P4` format and copies its pixels into the display buffer [file:1]. It first checks that the file begins with the correct PBM header, skips any comment lines, reads the image bytes, and then works through each bit to decide which pixels should be turned on [file:1].

This function is useful for displaying logos or small black-and-white images. Students should note that this version expects image data sized for the display dimensions defined by `WIDTH` and `HEIGHT`, so it is not a general-purpose image loader for any picture size [file:1].

## The `graph2D` class

The `graph2D` class is a helper for plotting changing values on the OLED screen, such as temperature readings or sensor data [file:1]. Its constructor stores the graph position, size, colour, minimum and maximum values, whether bars should be drawn, and a scaling formula used to map data values to screen coordinates [file:1].

The line `self.m = (1-height)/(maxValue-minValue)` creates a slope for converting real data values into y positions on the display, and `self.offset = originY-self.m*minValue` shifts the graph into the correct place on screen [file:1]. In practical terms, these two values convert a measured value like 100 or 200 into a pixel row that can be drawn on the OLED [file:1].

### `updateGraph2D()`

This method adds the newest value to the front of the graph's data list and removes the oldest value if the list becomes wider than the graph area [file:1]. It then walks across the stored values from right to left, calculating each y position and drawing either a single pixel or a vertical bar depending on the `bars` setting [file:1].

An interesting detail is that `updateGraph2D()` is placed inside the `graph2D` class but uses `self.pixel(...)`, so it is designed to be called as a display method while receiving a `graph2D` object as the `graph` argument [file:1]. That is a slightly unusual design for beginners, but it works because the display object has the `pixel()` method inherited from `FrameBuffer` [file:1].

## The MicroPython-specific child class

The class `PiicoDev_SSD1306_MicroPython` inherits from `PiicoDev_SSD1306` and performs the object setup needed for this MicroPython version [file:1]. In `__init__()`, it stores the I2C bus and device address, creates small helper byte arrays, calls `init_display()`, then initialises the parent `FrameBuffer` with `super().__init__(self.buffer, WIDTH, HEIGHT, framebuf.MONO_VLSB)` [file:1].

The `framebuf.MONO_VLSB` mode tells the framebuffer how bits are arranged in memory for this monochrome display format [file:1]. After setup, the constructor clears the display with `fill(0)` and immediately calls `show()` so the OLED starts in a blank state [file:1].

## The factory function

The function `create_PiicoDev_SSD1306(address=0x3C, bus=None)` creates and returns a `PiicoDev_SSD1306_MicroPython` object [file:1]. This gives users a simple one-line way to make a display object instead of needing to directly call the class constructor themselves [file:1].

For students, this means code can look like this:

```python
from machine import SoftI2C, Pin
from PiicoDev_SSD1306_Kookaberry import create_PiicoDev_SSD1306

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
disp = create_PiicoDev_SSD1306(bus=i2c, address=0x3C)
```

This example matches the style shown in the test code included at the end of the file [file:1].

## How drawing usually works

Most student programs will follow this pattern when using the display driver [file:1]:

1. Create an I2C object connected to the correct Kookaberry pins [file:1].
2. Create the display object with `create_PiicoDev_SSD1306()` [file:1].
3. Draw into the buffer using methods such as `fill()`, `pixel()`, `line()`, `rect()`, or `text()` [file:1].
4. Call `show()` to send the buffer to the real OLED display [file:1].

A short example is shown below:

```python
from machine import SoftI2C, Pin
from PiicoDev_SSD1306_Kookaberry import create_PiicoDev_SSD1306

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
disp = create_PiicoDev_SSD1306(bus=i2c)

disp.fill(0)
disp.text('Hello', 0, 0)
disp.line(0, 10, 50, 10, 1)
disp.show()
```

The screen does not update line by line in this example. Instead, the text and line are first drawn in memory, and then `show()` copies the final picture to the display [file:1].

## The test code at the end

The triple-quoted test block demonstrates three simple activities: a pixel display test, a geometry test, and a font test [file:1]. It creates a `SoftI2C` connection on pins `P3A` and `P3B`, creates the display object, then loops through those stages until button A is pressed on the Kookaberry [file:1].

The geometry test shows how lines and rectangles can be animated, while the font test changes between different font objects before writing text to the screen [file:1]. This section is useful as a learning example because it shows the normal sequence of clearing the screen, drawing shapes or text, and calling `show()` to make the result visible [file:1].

## Points beginners should notice

There are a few useful lessons hidden in the script [file:1]:

- The driver keeps a full copy of the screen in `self.buffer`, so memory and display are separate until `show()` is called [file:1].
- Inheritance is used twice, first to extend `framebuf.FrameBuffer` and then to build the MicroPython-specific display class [file:1].
- I2C communication is wrapped in helper methods so most student code never needs to send raw SSD1306 command bytes directly [file:1].
- Some items, such as `pack_into` and the undefined `i2c_err_str`, suggest the file has been adapted from a larger code base and may rely on surrounding environment features [file:1].

## Plain-language summary of key ideas

A beginner can think of the script in this way [file:1]:

- The OLED display is the hardware screen [file:1].
- The framebuffer is a hidden sketch pad in memory [file:1].
- Drawing methods change the sketch pad first [file:1].
- The `show()` method copies the sketch pad onto the real screen [file:1].
- The I2C methods are the delivery system that carries commands and pixel data from the Kookaberry to the display [file:1].

That model is enough to understand most of the script's behaviour and to start writing useful display programs with it [file:1].
