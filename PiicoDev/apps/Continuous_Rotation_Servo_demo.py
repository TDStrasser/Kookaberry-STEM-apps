# Example script for using angular servos with the PiicoDev Servo Driver board
from machine import SoftI2C, Pin
from time import sleep_ms
from PiicoDev_Servo_Kookaberry import PiicoDev_Servo, PiicoDev_Servo_Driver

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PiicoDev_Servo_Driver(i2c)

servo_2 = PiicoDev_Servo(controller, 2, midpoint_us=1500, range_us=800) # Connect a 360° servo to channel 2
# Note the FS90R continuous servo has a pulse range of:
#  700usec (max negative speed) to 2300usec (max positive speeed) 
#  1500usec is the zero speed point.

def ramp(servo,s1,s2):
  for s in range(s1,s2,int((s2-s1)/abs(s2-s1))):
    servo.speed = s/10
    print(s/10)
    sleep_ms(1000)

# Ramp the servo slowly through its range
ramp(servo_2,0,-10)
ramp(servo_2,-10,10)
ramp(servo_2,10,-1)
servo_2.release()