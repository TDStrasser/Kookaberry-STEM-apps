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