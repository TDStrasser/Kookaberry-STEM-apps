# Example script for using angular servos with the PiicoDev Servo Driver board
from machine import SoftI2C, Pin
from time import sleep_ms
from PiicoDev_Servo_Kookaberry import PiicoDev_Servo, PiicoDev_Servo_Driver

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)
servo_1 = PiicoDev_Servo(controller, 1,min_us=600, max_us=2600, degrees=180)
# Note SG90 servos seem to range from 600usec (90 deg) to 2600usec (180 deg) pulse widths

angles = [0,45,90,135,180,135,90,45,0,90]
# Step the servos
for angle in angles:
  servo_1.angle = angle
  sleep_ms(1000)

# Sweep the servo slowly 0->180°
for x in range(0,180,5):
    servo_1.angle = x
    sleep_ms(40)
# Send servo to the middle (90 degrees)
servo_1.angle = 90