# Kookaberry Library Modules
This is a repository of library modules for use with the Kookaberry micro-computer.
There are two types of Kookaberry distinguished by the microprocessor they use:
- RP2040 - this is the Raspberry Pi Pico microprocessor that is used by V2-x and later Kookaberries and also when a Raspberry Pi Pico is loaded with Kookaberry firmware.
- STM - The STM32 microprocessor used by V1-x Kookaberries.

MicroPython defines the concept of an .mpy file which is a binary container file format that holds precompiled code, and which can be imported like a normal .py module.  The bytecode, however, differs between the RP2040 and STM microprocessors.  The two mpy folders contain the bytecode module files for the respective microprocessors.

To use the mpy module files, download them from the repository and then download them to the Kookaberry's *lib* folder.

The code folder contains the MicroPython source code for each of the library modules.  These are provided as-is for information and need not be downloaded to the Kookaberry.

## Utility Library Modules
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
- **rttl** - provides the ability to play legacy Nokia ringtones. See the app **RTTLMusicDemo.py** for an example of usage.
- **songs** - a selection of RTTL Nokia ringtones to play on the Kookaberry.

## Sensor Library Modules
### Frozen Sensor Library Modules
The Kookaberry has a variety of sensor driver modules frozen in its firmware.  These include:
- bme280 — Atmospheric multi-sensor
- CCS811 — Atmospheric Carbon Dioxide Sensor
- dht — Atmospheric temperature and humidity sensor
- ds18x20 — Digital temperature sensor
- ds3231 — Battery-powered Real Time Clock
- ina219 — Digital wattmeter
- lsm303 — control of LSM303C/AGR accelerometer/magnetometer
- mcp23008 — I2C input/output expander
- mlx90614 — Infra-red digital temperature sensor
- neopixel — RGB colour LED array
- nrf5 — interface to the NRF51/NRF52 coprocessor
- onewire — interface to a 1-wire serial bus
- veml7700 — Digital Lux Meter 
The Kookaberry Reference Guide contains a section on the [Peripherals Module Library](https://kookaberry-reference-guide.readthedocs.io/en/latest/peripherals.html) that describes the peripherals and their modules' usages.

### Supplementary Sensor Library Modules
The Kookaberry can use other sensors beyond those catered for in the Kookaberry firmware.  To use these other sensors, library modules are required containing the necessary driver software.

Included here are library modules for the following supplementary sensors:
- **hcsr04** (and **rcwl-1601**) - Ultrasonic distance sensor.
  - The sensor uses ultrasonic echolocation to detect objects within a range of 2 to 450 cm.
  - Note the HCSR04 is a 5 volt module and so not compatible with the Kookaberry which uses 3.3 volts.
  - Instead use the 3.3V RCWL-1601 ultrasonic distance sensor, optionally with the Quokka QK-02-065 adapter module for convenient connection with the Kookaberry.

```
Usage:
    from hcsr04 import HCSR04

    sensor = HCSR04(trigger_pin='P3A', echo_pin='P3B') # Uses connector P3 on the Kookaberry
    distance, pulse = sensor.distance_mm() # Return distance in mm and pulse echo delay in microseconds.
    print('D: %d mm' % distance, 0, 30 )
    print('P: %d usec' % pulse, 0, 40)
```

- **pt100** - Module to measure temperature using a PT100 resistance temperature detector (RTD) probe # which is interfaced via a wheatstone bridge and analogue amplifier module.
  - The sensor is a DFRobot SEN0198 High Temperature Sensor
  - The equation given by DFRobot to convert the module analogue voltage to sensor resistance is ```res =  (1800 * voltage + 220.9 * 18) / (2.209 * 18 - voltage)``` 
  - The resistance is then converted to temperature by this equation inferred from curve fitting of RTD resistance vs temperature data: ```temp = 0.0012 * res^2 + 2.3024 * res - 242.89``` in deg C
  - On the Kookaberry the sensor connects to plugs **P4** or **P5**. Results may be unpredictable if plugged in elsewhere
```
Usage:
    import pt100
    rtd = pt100.PT100('P4')    # create the RTD object on P4
    resistance = rtd.resistance    # reads the RTD resistance
    temperature = rtd.temperature    # computes the RTD temperature
    theoretical_rtd_resistance = pt100.rtd_resistance(temperature)
    # The last function is provided to compute the theoretical RTD resistance for a given temperature
```
- **sds101** - A driver for the SDS011 particulate matter sensor.
  - The SDS011 sensor has a serial interface connected to the Kookaberry's UART, usually plug **P3**.
```
Usage:
    from machine import UART # The UART class
    from sds011 import SDS011 # The SDS011 dust sensor class
    uart = UART(1, 9600) # Create the UART object
    uart.init(9600, bits=8, parity=None, stop=1) # Initialise the UART to match the SDS011 serial interface
    dust_sensor = SDS011(uart) # Create the dust sensor object
    # Periodically (say once a minute or longer):
    if dust_sensor.read(): # Attempt to obtain data from the dust sensor - True is successful
        pm25 = dust_sensor.pm25 # Returns the 2.5 micron dust density in parts per million
        pm10 = dust_sensor.pm10 # Returns the 10 micron dust density in parts per million
```
- **sen15901** - Class and functions module for the Shenzen Fine Offset SEN15901 weather sensor comprising an anemometer, a windvane, and a tipping bucket rain gauge.
```
Usage -
    # Create the sensor object:
    weather = sen15901.SEN15901(anem_pin,rgauge_pin,wvane_pin,vcc=3.3,pullup=4700)
    # Gather the sensor readings:
    windspeed = weather.windspeed # Wind speed in kilometres / hour
    wind_azimuth = weather.azimuth # Wind direction in degrees from North or -1
    wind_direction = weather.direction # String sub-cardinal eg. 'NNE' or 'None'
    rainfall = weather.rainfall # Total rainfall in mm since startup
    weather.reset_rainfall() # zeroes the rainfall accumulator
    # Utility constants and functions:
    weather.anem_calib # constant containing the windspeed per anemometer pulse per sec
    weather.rgauge_calib # constant containing the rainfall per pulse of the rain gauge
    weather.vcc # the Vcc voltage applied to the windvane
    weather.pullup # the pullup resistor value in ohms for the windvane
    weather.wvane_calib()  # recalculates the windvane direction voltage array
    # Use this whenever any windvane constant is changed
    weather.windvane_read() # reads the windvane voltage and returns an index to the direction array if successful, or -1 is the read fails
```
- **veml6070_i2c** - Class and functions to measure UV light level (default Watts/sqm) using a VEML6070 digital UV sensor.
  - Based on the driver at https://github.com/cmur2/python-veml6070 with pure I2C bus for the Kookaberry adaptation
  - Redundant SMBbus code lines have been commented out and replaced by I2C code
```
Usage:
    from veml6070_i2c import Veml6070 # The veml6070 class
    uv = Veml6070(i2c) # Create the Veml6070 object on the I2C bus - create the i2c object using **machine.SoftI2C**

    # Periodicall read the UV sensor
    uv_light = uv.get_uva_light_intensity() / 10 # Scale from W/sqm to mw/sqcm
    uv_index = int(uv_light / 2.5) # Calculate the UV index
    # Use with care
    uv_risk = uv.get_estimated_risk_level(uv_light)    # not consistent with Australian BOM risk which is 1 point per 25mW/sqm

```