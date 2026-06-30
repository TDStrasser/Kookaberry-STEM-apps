# Example script for using angular servos with the PiicoDev Servo Driver board
from machine import SoftI2C, Pin
from time import sleep_ms
from PiicoDev_Servo_Kookaberry import PiicoDev_Servo, PiicoDev_Servo_Driver

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)

servo_2 = PiicoDev_Servo(controller, 2, midpoint_us=1500, range_us=1800) # Connect a 360° servo to channel 2

# Ramp the servo slowly through its range
for s in range(-10,10,2):
    servo_2.speed = s/10
    sleep_ms(1000)
