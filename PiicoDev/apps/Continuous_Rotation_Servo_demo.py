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

# Speeds in this script are in the range -100 to +100
current_speed = 0 #

def ramp(servo,s1,s2):
  if s2 == s1: return # Skip zero changes
  direction = int((s2-s1)/abs(s2-s1))
  for s in range(s1,s2+direction,direction):
    servo.speed = s/100
    sleep_ms(20)

speeds = [0,-100,100,0,-50,50,0,-25,25,0] # Put the speeds you want in this array (-100 to +100)
# Step the servos
for speed in speeds:
  if speed < -100: speed = -100 # limit out of range
  if speed > 100: speed = 100
  ramp(servo_2,current_speed, speed)
  current_speed = speed # Record the last target speed
  sleep_ms(1000) # Stay at the sppeed for a while

servo_2.release() # Stop the servo driver PWM so it doesnt creep