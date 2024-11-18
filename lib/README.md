# Kookaberry Library Modules
This is a repository of library modules for use with the Kookaberry micro-computer.
There are two types of Kookaberry distinguished by the microprocessor they use:
- RP2040 - this is the Raspberry Pi Pico microprocessor that is used by V2-x and later Kookaberries and also when a Raspberry Pi Pico is loaded with Kookaberry firmware.
- STM - The STM32 microprocessor used by V1-x Kookaberries.

MicroPython defines the concept of an .mpy file which is a binary container file format that holds precompiled code, and which can be imported like a normal .py module.  The bytecode, however, differs between the RP2040 and STM microprocessors.  The two mpy folders contain the bytecode module files for the respective microprocessors.

To use the mpy module files, download them from the repository and then download them to the Kookaberry's *lib* folder.

The code folder contains the MicroPython source code for each of the library modules.  These are provided as-is for information and need not be downloaded to the Kookaberry.
