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
    # Set up the I2C bus and RFID reader
    i2c = SoftI2C(sda = Pin("P3B"), scl=Pin("P3A"))
    rfid = PiicoDev_RFID(i2c)   # Initialise the RFID module at the default address (0x2c)
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
