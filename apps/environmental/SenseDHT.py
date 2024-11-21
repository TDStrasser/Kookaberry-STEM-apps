# File name: 
__name__='SenseDHT'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 17 October 2019
# Date last modified: 26 January 2021
# MicroPython Version: 1.12 for the Kookaberry V4-05
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# Measure temperature and humidity using a DHT11 or DHT22 sensor
# Initially it attempts to detect which sensor it has
# Logs the measurements into a file at an interval specified in Kappconfig.txt
# Broadcasts the sensor readings over the packet radio in the format [DHT,Temp,Humid]
# Jan 2021 - relays sensor reading data via UART 1 (plug P3)
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: DHT22 or DHT11 sensor plugged into port P2
# /lib files: Kapputils.py, logger.py, doomsday.py
# /root files: Kappconfig.txt or Kappconfig.cfg 
# Other dependencies: nil
# Complementary apps: SenseRx.py receives data and sends time update
#                    _Config.py sets up configuration parameters
#------------------------------------------
# Begin code
# Initial conditions

import machine, dht, kooka, fonts, time, json
from Kapputils import config    # module to read the configuration file
import logger    # module to create and run the datalogger
import doomsday    # converts date to day of week

# Use the Kookaberry Real Time Clock - user will have to set the time beforehand.
rtime = [0]*6   # Kookaberry time tuple [YYYY,MM,DD,HH,MM,SS]    # received time
ftime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]    # update time
ktime = [0]*8   # Kookaberry time tuple [YYYY,MM,DD,WD,HH,MM,SS,SUBS]
rtc = machine.RTC()    # instantiate the Real Time Clock

disp = kooka.display    # initialise the OLED display
disp.print(__name__)
disp.print('Initialising...')

# Prepare the UART port to relay the sensor data received.
uart = machine.UART(1, 9600,bits=8, parity=None, stop=1)
column_h = ['Ta-degC','H-%'] # Data column headings for serial port relay

params = config('Kappconfig.txt')   # read the configuration file
# set up the radio for later use
# flag to set up the radio for later use
radio_on = False

# Set up the Kookaberry's ID (more complex for backward compatibility)
id=''
for i in range(0,min(2,len(params['NAME']))): id = id + params['NAME'][i]
for i in range(0,min(2,len(params['SURNAME']))): id = id + params['SURNAME'][i]

# Proforma radio message
sndmsg = [id,'DHT','T','H']

# set up the datalogger
dlog = logger.Dlog(__name__+'.csv',int(params['INTV']),'Date-Time,T-degC,RH%')    # Create the datalogger instance
dlog.start()    # Start the datalogger

sensors = ['No','DHT11','DHT22']
dhtpin = 'P2'
dhtinterval = 2000    # milliseconds between DHT sensor reads
d = dht.DHT11(machine.Pin(dhtpin))
dhtconnected = 0

try:
    d.measure()
except Exception:
    disp.setfont(fonts.mono6x7)
    disp.text('Connect DHT to %s' % dhtpin, 0, 20)
temp = d.temperature()
humid = d.humidity()
if temp < 2 and humid < 5: # DHT22 reads low integers if read by DHT11
    dhtconnected = 2
    d = dht.DHT22(machine.Pin(dhtpin))
else:
    dhtconnected = 1
sndmsg[1] = sensors[dhtconnected]    # modify radio header to sensor type
time.sleep_ms(dhtinterval)
_timer_dht = time.ticks_ms()
# Set up the radio transmission interval timer
tx_interval = params['INTV'] * 1000    # interval between radio update in milliseconds
_timer_tx = time.ticks_ms() + tx_interval    # initialise the radio timer
# This is the main sensing and logging loop
while not kooka.button_a.was_pressed():
# Construct the time string
    ktime = rtc.datetime()  # Refresh the time
    timestr = "%02d-%02d-%04d %02d:%02d:%02d" % (ktime[2],ktime[1],ktime[0],ktime[4],ktime[5],ktime[6])    # Kookaberry time tuple is [YYYY,MM,DD,WD,HH,MM,SS,SUBS]

    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 8)
    disp.setfont(fonts.mono6x7)
    disp.text('%s %s' % (id,sensors[dhtconnected]), 70, 8)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit', 0, 62)
    disp.text('Log in %d' % dlog.log_counter, 60, 62)
    disp.text('%s' % timestr, 0, 52)
    if time.ticks_diff(time.ticks_ms(), _timer_dht) >= 0:
        _timer_dht += dhtinterval
        try:
            d.measure()
            temp = d.temperature()
            humid = d.humidity()
            sndmsg[2] = '%.1f' % temp
            sndmsg[3] = '%.1f' % humid
        except Exception:
            temp = 0
            humid = 0

    if temp == 0 and humid == 0:
        disp.setfont(fonts.mono6x7)
        disp.text('Connect %s to %s' % (sensors[dhtconnected],dhtpin), 0, 25)
    else:
        disp.setfont(fonts.mono8x13)
        disp.text('Temp = %.1f C' % temp, 12, 25)
        disp.text('Humi = %.1f %%' % humid, 12, 40)
    disp.show()

    dlog.update('%s,%0.1f,%0.1f' % (timestr,temp, humid))    # update the string to be logged
    dlog.write()    # writes the datalogger string when next due
    
# Initialise the radio if not already on
    if not radio_on:
        try:    # Restarting the radio
            print('Radio init ', timestr)
            kooka.radio.enable()
            chan = int(params['CHANNEL'])      # use channel from the configuration file
            baud = int(params['BAUD'])      # use data rate from the configuration file
            pwr = int(params['POWER'])      # use transmit power from the configuration file
            kooka.radio.config(channel=chan, data_rate=baud, power=pwr, length=50) # set up the radio
            radio_on = True
        except:
            radio_on = False
# send the radio update
    if time.ticks_diff(time.ticks_ms(), _timer_tx) >= 0:
        _timer_tx += tx_interval    # transmit every period
        if temp and humid: # check if there is a reading to send
            try:
                kooka.radio.send(json.dumps(sndmsg))
                print(sndmsg)
            except:
                radio_on = False
                print('Radio error')
            # Also Relay sensor data via UART
            for i in range(0, len(column_h)):
                series = column_h[i] + "-" + sndmsg[0]
                value = sndmsg[i+2]
                uart.write('{%s:%s}' % (series, value))
#                print('{%s:%s}' % (series, value))

# Check for time updates
    if radio_on: 
        try:
            msg = kooka.radio.receive()    #listen for a message
        except:
            radio_on = False
    if msg:    # radio has received a message
        print(msg)
        if len(msg) == 21 and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
# Check for time updates from the UART
    if uart.any():
        msg = uart.readline().decode('utf-8').rstrip('\n')
    if msg:    # radio has received a message
        print(msg)
        if len(msg) >= 16 and len(msg) <= 21 and msg[0] == '[' and msg[len(msg)-1] == ']' and msg[1].isdigit() and msg[2].isdigit() and msg[3].isdigit() and msg[4].isdigit():  # is a time update so process
            rtime = json.loads(msg)
            for i in range(0,4): ftime[i] = rtime[i]    # transfer date
            for i in range(3,6): ftime[i+1] = rtime[i]    # transfer time
            ftime[3] = doomsday.dow_index(ftime[2],ftime[1],ftime[0])    # update day of week 
            rtc.datetime(tuple((ftime[0],ftime[1],ftime[2],ftime[3],ftime[4],ftime[5],ftime[6],0))) # Update the RTC
        else:  pass  # not a time update so ignore
        
# Clean up and exit
dlog.kill()    # disables the datalogger
kooka.radio.disable()    # turn off the radio


