# Kookaberry Library Modules
This is a repository of library modules for use with the Kookaberry micro-computer.
There are two types of Kookaberry distinguished by the microprocessor they use:
- RP2040 - this is the Raspberry Pi Pico microprocessor that is used by V2-x and later Kookaberries and also when a Raspberry Pi Pico is loaded with Kookaberry firmware.
- STM - The STM32 microprocessor used by V1-x Kookaberries.

MicroPython defines the concept of an .mpy file which is a binary container file format that holds precompiled code, and which can be imported like a normal .py module.  The bytecode, however, differs between the RP2040 and STM microprocessors.  The two mpy folders contain the bytecode module files for the respective microprocessors.

To use the mpy module files, download them from the repository and then download them to the Kookaberry's *lib* folder.

The code folder contains the MicroPython source code for each of the library modules.  These are provided as-is for information and need not be downloaded to the Kookaberry.

## Utility Modules
These are generally applicable modules that extend the functionality of the Kookaberry:
- **Kapputils** - utility module that reads and writes a configuration file that contains key operations parameters, e.g. radio channel, logging interval, and an ID number, plus a variety of lesser used legacy parameters.
  - The app **_Config** creates the following JSON configuration in the file *Kookapp.cfg* - ```{"ID": 1, "INTV": 10, "NAME": "01", "POWER": 6, "BAUD": 0, "SURNAME": "", "CHANNEL": 83}```
```
Usage:
    from Kapputils import config
    params = config('Kookapp.cfg')   # load the configuration into a dictionary params
```

- **kbtimer** - implements a long-press functionality for the Kookaberry's buttons.
```
Usage:
    import kbtimer
    b_timer = kbtimer.KBTimer(kooka.button_a, 1000) # instantiate a buttom timer object
    if b_timer.isexpired(): do something  # test for button expiry
    time_pressed = b_timer.button_time  # record of button millisecond if pressed else zero
    time_since_pressed = b_timer.timer()  # returns the time since pressed or ero if not pressed
    time_to_expiry = b_timer.toexpiry() # returns time to expiry in milliseconds or zero if not pressed
    b_timer.reset()  # housekeeping to reset the expired flag if used multiple times - ie. must be reset every time
```
- **logger** - a class that enables periodic datalogging of collected data into a CSV file in the Kookaberry's file storage system.
```
Usage:
    import logger
    logger.Dlog(file, interval, heading) # initialises the file and logging interval inerrupt
    logger.kill()		# stops the interrupt process
    logger.update(string)    # updates the string to be written to file
    logger.start()    # commence logging every interval
    logger.stop()    # stops logging
    logger.control()    # checks timing, control flag, and battery status to control datalogging - called by a timer interrupt - do not call
    logger.write()    # required every loop - appends the update string to the file
```

- **screenplot** - a class that enables graphing of data trends on the Kookaberry's display.
```
Usage:
    disp = kooka.display
    import screenplot
    screenplot.area(disp, x0, y0, width, height) # initialises the plot area in pixels. disp = framebuffer object
    screenplot.draw_area()    # clears the plot area and draws a border
    screenplot.trend()    # initialises a new trendline
    screenplot.scale(area, xmax, ymin, ymax)		# initialises the scale dimensions for the trend within the plot area given
    screenplot.value(value)    # appends the value to the trend data  
    screenplot.draw_trend(area, autoscale=False)    # draws the trend on the given area and optionally autoscales the y scale
```

## Music Modules
These modules enable the Kookaberry to play music:
- **musictunes** - contains a variety of Micro-bit compatible tunes that can be played by the Kookaberry.
- **rttl** - provides the ability to play legacy Nokia ringtones.
- **songs** - a selection of RTTL Nokia ringtones to play on the Kookaberry.
