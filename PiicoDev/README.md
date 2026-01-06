# PiicoDev for the Kookaberry
This is a repository of MicroPython scripts and library modules to enable the use of PiicoDev hardware with the Kookaberry micro-computer.

The PiicoDev series of hardware peripherals is described at this link: [PiicoDev Guide](http://piico.dev/guides)

The software that can be downloaded from Core Electronics is not compatible with the Kookaberry in most cases.
This repository provides Kookaberry-compatible software that enables PiicoDev modules to be used with the Kookaberry.  The software does not cover every PiicoDev module (as yet) and is steadily being enlarged as time and resources permit.

This repository is organised as follows:
- **apps** - contains pre-coded programs (apps) to demonstrate the functionality of PiicoDev modules.  They are intended as examples. 
- **lib** - contains PiicoDev library modules in the following folders:
  - **code** - contains the source code of the library modules
  - **mpy Pico** - MicroPython bytecode for the RP2040 and RP2350 using Kookaberry firmware
  - **mpy STM** - MicroPython bytecode modules for the STM Kookaberry

## PiicoDev Documentation
Documentation for the PiicoDev modules is available online.  The most relevant documents are here: [PiicoDev for the Raspberry Pico](https://core-electronics.com.au/piicodev-starter-kit-raspberry-pi-pico-guides-0)

The main changes to use the PiicoDev modules with the Kookaberry are:
- The Kookaberry uses JST PH connectors and PiicoDev modules use the physically smaller JST SH connectors. Consequently a 4-pin JST PH to JST SH Cable (available from Core Electronics) is required to connect a PiicoDev module to the Kookaberry.
- Do not use the PiicoDev Unified Library in your scripts as it is not compatible with Kookaberry MicroPython firmware.
- Create an I2C bus object using the Kookaberry SoftI2C() function and then pass the resulting I2C object to the PiicoDev initialisation function. See the script samples in this repository

## PiicoDev Module Scope
The following are the PiicoDev modules covered by this repository (so far):
- BME280 Atmospheric Sensor - plug compatible with the Kookaberry and its standard firmware. No additonal software required.
- RFID Module - library module and sample script included here.
- OLED Display - library module and sample script included here. Note the PiicoDev SSD1306 OLED display module is very small and may be difficult to read.

These other known PiicoDev modules are not as yet catered for but may be in the future:
- RGB LED Module - an alternative is to use NeoPixels connected via a OneWire interface.
- Buzzer Module - an alternative is to use a digital buzzer module with a Pin or PWM interface.
- Capacitive Touch Sensor
- Colour Sensor
- Accelerometer - note the Kookaberry hardware contains an accelerometer (but not the standard Pico boards). An LM303C accelerometer is however supported by the standard Kookaberry firmware.
- Distance Sensor - an alternative in the meantime is to use the 3.3V RCWL-1601 ultrasonic distance sensor and the hcsr04 library module provided elsewhere in this repository.

There are numerous other PiicoDev modules available [here](https://core-electronics.com.au/piicodev.html) which may be catered for over time.


##Important Disclaimer
To the fullest extent permitted by law, AustSTEM and the authors named herein absolutely disclaim all warranties, expressed or implied, including, but not limited to, implied warranties of merchantability and fitness for any particular purpose. 

No warranty is given that this software will be free of errors, or that defects in the software will be corrected.

See the GNU General Public License for more details.