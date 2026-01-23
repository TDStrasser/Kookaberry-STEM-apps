# Example script setting the RGB LEDs to successive hues around the colour wheel
from machine import Pin, SoftI2C
from time import sleep_ms
from PiicoDev_RGB_Kookaberry import PiicoDev_RGB, wheel

# First set up the I2C bus
i2c = SoftI2C(sda=Pin("P3B") ,scl=Pin("P3A"))

# Then instantiate the PiicoDev RGB module using the I2C bus
leds = PiicoDev_RGB(bus=i2c)

while True:
    for x in range(0,360,10): # glow on
        hue = x / 360
        for y in range(10):
            brightness = y/10
            rgb = wheel(h=hue,v=brightness)
            leds.fill( rgb ) # fill() will automatically show()
            sleep_ms(100)