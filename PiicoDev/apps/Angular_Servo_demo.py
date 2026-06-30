# Example script for using angular servos with the PiicoDev Servo Driver board
from machine import SoftI2C, Pin
from time import sleep_ms
from PiicoDev_Servo_Kookaberry import PiicoDev_Servo, PiicoDev_Servo_Driver

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)
servo_1 = PiicoDev_Servo(controller, 1)
servo_4 = PiicoDev_Servo(controller, 4)

angles = [0,45,90,135,180,135,90,45,0]
# Step the servos
for angle in angles:
  servo_1.angle = angle
  servo_4.angle = angle
  sleep_ms(1000)

# Sweep the servo slowly 0->180°
for x in range(0,180,5):
    servo_1.angle = x
    servo_4.angle = x
    sleep_ms(40)
