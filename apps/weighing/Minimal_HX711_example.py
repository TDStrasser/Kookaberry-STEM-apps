# Minimal implementation of the HX711 strain gauge reading program.
# Returns the gross value in millivolts from the device
#------------------------------------------
# Dependencies:
# I/O ports and peripherals:
# /lib files:
# /root files:
# Other dependencies:
# Complementary apps:
#------------------------------------------

# Begin code
from hx711_gpio import *
hx = HX711(Pin('P3B'), Pin('P3A'))    # hx711 = HX711(clock_pin, data_pin, gain=128) 
# valid gains are 32, 64 and 128 - gain of 32 is for channel B only
hx.power_up()

# Function to return the raw millivolt reading
def read_mv():
    return hx.read_average(times=5)/8388608*20*3.3/5    # reading in mV

import kooka, time

display = kooka.display
while True:
    display.clear()
    display.print(read_mv())
    display.show()
    time.sleep(1)