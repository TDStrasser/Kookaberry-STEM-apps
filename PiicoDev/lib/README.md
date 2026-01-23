# Kookaberry PiicoDev Library Modules
This is a repository of library modules to enable PiicoDev hardware to be used with the Kookaberry micro-computer.
There are two types of Kookaberry distinguished by the microprocessor they use:
- Pico - this is the Raspberry Pi Pico microprocessor that is used by V2-x and later Kookaberries and also when a Raspberry Pi Pico is loaded with Kookaberry firmware. The Raspberry Pi Pico RP2040 and RP2350 microprocessors are catered for and use the same library modules.
- STM - The STM32 microprocessor used by V1-x Kookaberries.

MicroPython defines the concept of an .mpy file which is a binary container file format that holds precompiled code, and which can be imported like a normal .py module.  The bytecode, however, differs between the Pico and STM microprocessors.  The two mpy folders contain the bytecode module files for the respective microprocessors.

To use the mpy module files, download them from the relevant repository and then download them to the Kookaberry's *lib* folder.

The code folder contains the MicroPython source code for each of the library modules.  These are provided as-is for information and need not be downloaded to the Kookaberry.

## PiicoDev Library Modules
These are modules so far for the Kookaberry.  Links to the PiicoDev user documentation are provided.  Setting up the PiicoDev modules for use by the Kookaberry requires attention to the following:
- The Kookaberry uses JST PH connectors and PiicoDev modules use the physically smaller JST SH connectors. Consequently a 4-pin JST PH to JST SH Cable (available from Core Electronics) is required to connect a PiicoDev module to the Kookaberry.
- Do not use the PiicoDev Unified Library in your scripts as it is not compatible with Kookaberry MicroPython firmware.
- Create an I2C bus object using the Kookaberry SoftI2C() function and then pass the resulting I2C object to the PiicoDev initialisation function. 

See the script samples in this repository.

The modules provided to date are:
- **PiicoDev_RFID_Kookaberry** interfaces the [PiicoDev RFID Module](https://core-electronics.com.au/guides/raspberry-pi-pico/piicodev-rfid-module-guide-for-raspberry-pi-pico/).  See the script RFID_vending_demo.py in the PiicoDev apps folder for a scripting example.
```
Usage:
    from PiicoDev_RFID_Kookaberry import PiicoDev_RFID
    from machine import Pin, SoftI2C
    # Set up the I2C bus
    i2c = SoftI2C(sda = Pin("P3B"), scl=Pin("P3A"))
    # Set up the RFID Reader on the I2C bus
    rfid = PiicoDev_RFID(i2c)   # Initialise the RFID module at the default address (0x2c)
    # Optional parameters: address=0xNN or asw=[x,y] corresponding to the setting of the ASW switch on the hardware.
    # The addresses corresponding to the switch settings are printed on the back of the hardware module.
    # asw= [0,0]: address=0x2c
    # asw= [1,0]: address=0x2d
    # asw= [0,1]: address=0x2e
    # asw= [1,1]: address=0x2f
    # Thereafter use the standard PiicoDev library API calls...

```

- **PiicoDev_SSD1306_Kookaberry** interfaces the [PiicoDev OLED Module SSD1306](https://core-electronics.com.au/guides/raspberry-pi-pico/piicodev-oled-ssd1306-raspberry-pi-pico-guide/). See the script SSD1306_display_demo.py in the PiicoDev apps folder for a scripting example.
```
Usage:
    from PiicoDev_SSD1306_Kookaberry import create_PiicoDev_SSD1306
    from machine import Pin, SoftI2C
    # Set up the I2C bus and OLED display
    i2c = SoftI2C(sda = Pin("P3B"), scl=Pin("P3A"))
    disp = create_PiicoDev_SSD1306(bus=i2c, address=0X3C)  # Initialise the OLED display
    # Thereafter use the standard PiicoDev library API calls...  The Kookaberry framebuf API calls also apply.

```

- **PiicoDev_VL53L1X_Kookaberry** interfaces the [PiicoDev Distance Sensor](https://core-electronics.com.au/guides/piicodev-distance-sensor-vl53l1x-raspberry-pi-pico-guide/). See the script PiicoDev_Distance_Sensor_Demo.py in the PiicoDev apps folder for a scripting example.
```
Usage:
    # Test of PiicoDev Distance Sensor connected to Plug P3
    from time import sleep_ms
    from machine import Pin, SoftI2C
    import kooka
    from PiicoDev_VL53L1X_Kookaberry import PiicoDev_VL53L1X
    
    disp=kooka.display
    
    # First set up the I2C bus
    i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))
    
    # Then instantiate the PiicoDev distance sensor using the I2C bus
    distSensor = PiicoDev_VL53L1X(bus=i2c)
    
    # Start measuring distance and show on the Kookaberry display
    while not kooka.button_a.was_pressed():
        disp.clear()
        disp.print('Distance:')
        distance = distSensor.read() # Returns the measured distance in mm
        disp.print(str(distance)+' mm')
        sleep_ms(100)

```

- **PiicoDev_RGB_Kookaberry** interfaces the [PiicoDev RGB LED Module](https://core-electronics.com.au/guides/raspberry-pi-pico/piicodev-rgb-led-module-raspberry-pi-pico-guide/). See the script PiicoDev_RGB_Demo.py in the PiicoDev apps folder for a scripting example.
```
Usage:
    from machine import Pin, SoftI2C
    from PiicoDev_RGB_Kookaberry import PiicoDev_RGB, wheel
    
    # First set up the I2C bus
    i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))
    
    # Then instantiate the PiicoDev RGB module using the I2C bus
    leds = PiicoDev_RGB(bus=i2c)
    # Optional parameters: address=0xNN or id=[x,y,0,0] corresponding to the setting of the ID switch on the hardware.
    # The addresses corresponding to the switch settings are printed on the back of the hardware module.
    # id = [0,0,0,0]: address=0x08
    # id = [1,0,0,0]: address=0x09
    # id = [0,1,0,0]: address=0x0a
    # id = [1,1,0,0]: address=0x0b
    # Note id allows for 4 switches though only 2 are provided on the PiicoDev hardware module.

    # setPixel
    leds.setPixel(n, colour) will set led #n (range 0 to 2) to the RGB colour colour = [r,g,b] where r,g,b are 0-255
    # Once the pixels are set with setPixel(), the new values must be pushed to the physical LEDs with show().
    
    # show
    leds.show() # Updates the physical LEDs with data set by eg. setPixel().
    
    # clear
    leds.clear() # Blanks all the RGB LEDs. It is not necessary to call show() after calling clear().
    
    # setBrightness
    leds.setBrightness(x) # controls the maximum brightness of the RGB LEDs, where x may be between 0-255. 
    # This function is useful to avoid being dazzled by the bright LEDs, or to keep current consumption low.
    
    # fill
    leds.fill(colour) # where colour is a 3 byte RGB array [rr,gg,bb] each in the range 0-255.
    # Will fill all RGB LEDs with the colour specified by the RGB list colour. Automatically updates the LEDs by calling show()
    
    # wheel
    wheel(h,s,v) # where h is hue (0 to 1), s is saturation (0 to 1) and v is brightness (0 to 1).
    # Returns an RGB colour list [r,g,b] colour from the colour wheel.
    # Note the Core Electronics guide for the function wheel() is incorrectly described
    
    # pwrLED
    leds. pwrLED(True/False) # will set the LED to True = on, False = off

```
