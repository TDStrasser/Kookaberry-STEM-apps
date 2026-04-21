# AHT/ENS160 test code
from machine import SoftI2C, Pin
from time import sleep_ms
from ens160 import ENS160
from aht21 import AHT21

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
aht = AHT21(i2c)
ens = ENS160(bus=i2c, address=0x53)
sleep_ms(2000)
import kooka, fonts
disp = kooka.display
while True:
    humidity, temperature = aht.read()
    ens.temperature = temperature
    ens.humidity = humidity
    disp.clear()
    disp.setfont(fonts.mono6x7)
    disp.print("AHT21/ENS160 Data")
    disp.print("AQI:%d %s" % (ens.aqi.value, ens.aqi.rating) )
    disp.print("CO2:%dppm %s" % (ens.eco2.value, ens.eco2.rating) )
    disp.print("TVOC:%dppb" % ens.tvoc)
    disp.print("Temp:%2.fC" % ens.temperature)
    disp.print("Humid:%d%%" % ens.humidity)
    disp.print("Status:%s %s" % (ens.status_validity_flag, ens.operation) )

    sleep_ms(5000)
