__name__ = 'Web_BME280'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 27 May 2025
# Date last modified: 29 May 2026
# Version: 1.0
# MicroPython Version: 1.24 for the Kookaberry Pico RP2040W/RP2350W
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
'''
Measures temperature, humidity and air pressure using a BME280 environmental sensor 
If the sensor is not present prompt is displayed. 
The program suspends until a sensor is detected.

The Kookaberry sets up a stand-alone WiFi Access Point and serves the BME280 measurements as a web page.

Acknowledgements:
 https://RandomNerdTutorials.com/raspberry-pi-pico-web-server-micropython/
 https://www.instructables.com/Creating-a-Wireless-Network-With-Raspberry-Pi-Pico/
'''
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: BME280 sensor plugged into P3
# /lib files: Nil
# /root files: Nil
# Other dependencies: Pico RP2040W/RP2350W with Kookaberry firmware
# Complementary apps: Nil
#------------------------------------------
# Begin code

# Import necessary modules
import network
import socket
import time
from machine import Pin, SoftI2C
import kooka, fonts
from bme280 import BME280

# Enter Wi-Fi credentials below
ssid = 'kookaberry' # WiFi network SSID - modify as needed
password = '12345678' # WiFi network password - modify as needed

disp = kooka.display # Kookaberry display object

# HTML template function for the webpage.
# It displays the BME280 measurements, the browser data, and refreshes itself every 10 seconds
def webpage(temperature, humidity, pressure):
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kookaberry Weather</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ min-width: 310px; max-width: 800px; height: 400px; margin: 0 auto; }}
                h2 {{ font-family: Arial; font-size: 2.5rem; text-align: center; }}
                p {{ font-family: Arial; font-size: 1.5rem; text-align: center; }}
            </style>
        </head>
        <body>
            <h2>Kookaberry Weather</h2>
            <p>Temperature {temperature}C</p>
            <p>Humidity {humidity}%</p>
            <p>Pressure {pressure}hPa</p>
            <br>
            <p><span id="datetime"></span></p>
        <script>
        // create a function to update the date and time
        function updateDateTime() {{
        // create a new `Date` object
            const now = new Date();
        // get the current date and time as a string
            const currentDateTime = now.toLocaleString();
        // update the `textContent` property of the `span` element with the `id` of `datetime`
            document.querySelector('#datetime').textContent = currentDateTime;
         }}
        updateDateTime()
        </script>
        <script>
        // refreshes itself every 10000 milliseconds
        setInterval(function ( ) {{
          location.reload(true);
          }}, 10000 ) ;
        </script>
        </body>
        </html>
        """
    return str(html)
    
# Initialise the BME280
SCL = 'P3A'
SDA = 'P3B'
i2c = SoftI2C(scl=Pin(SCL),sda=Pin(SDA), freq=50000) # Initialise the I2C bus object
bme = BME280(address = 0x77, i2c=i2c) # Initialise the BME280 sensor
# Initialise the weather measurement variables
bme_temperature = 0
bme_pressure = 0
bme_humidity = 0
# Set up the BME280 read timing loop parameters
bme_interval = 2000 # Minimum measurement interval for the BME280 is 2 seconds
_timer_bme = time.ticks_ms()    # timer used measurements

# Show status on the Kookaberry display
disp.print('Weather Web Server')
disp.print('SSID %s' % ssid)

# Connect to WLAN
wlan = network.WLAN(network.AP_IF)
wlan.config(essid=ssid, password=password)
wlan.active(True)

while wlan.active() == False: # Wait for the WiFi to activate
    pass
    
print('AP Mode Is Active, You can Now Connect')
addr = wlan.ifconfig()[0]
print('IP Address to connect to: ' + addr)

disp.print('AP Active')
disp.print('Connect to:')
disp.print(addr)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
s.bind(('', 80))
s.listen(1)

print('Listening on', addr)
disp.print('Listening')

# Set up the web request timing loop parameters
wlan_interval = 1000
_timer_wlan = time.ticks_ms()

# Main loop to listen for connections
while True:
# Read and process the BME280 sensor
    if time.ticks_diff(time.ticks_ms(), _timer_bme) >= 0:
        _timer_bme += bme_interval    # only take a sample every period
        bme_read = False
        try:
            bme_temperature = bme.values[0]
            bme_pressure = bme.values[1]
            bme_humidity = bme.values[2]
            bme_read = True
        except:    # Couldn't take a reading from the sensor
            bme_temperature = 0
            bme_pressure = 0
            bme_humidity = 0
# Update the Kookaberry display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    if bme_read: 
        disp.text('Temp: %6.1f C' % bme_temperature, 12, 20)
        disp.text('RelH: %6.1f %%' % bme_humidity, 12, 30)
        disp.text('Press: %6.1f hPa' % bme_pressure, 12, 40)
    else: disp.text('Plug sensor into P3', 0, 20)
    disp.text('SSID %s' % ssid, 0, 53)
    disp.text('IP Adx %s' % addr, 0, 63)
    disp.show()

# Process any web connections
    if time.ticks_diff(time.ticks_ms(), _timer_wlan) >= 0:
        _timer_wlan += wlan_interval    # only take a sample every period

        try:
            conn, addrx = s.accept()
            print('Got a connection from', addrx)
        
        # Receive and parse the request
            request = conn.recv(1024)
            request = str(request)
            print('Request content = %s' % request) # The whole HTTP request

        # Process the request and update variables
            response = webpage(round(bme_temperature,1),round(bme_humidity,1),round(bme_pressure,1))

        # Send the HTTP response and close the connection
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.send(response)
            conn.close()
#            print(response)

        except OSError as e:
            conn.close()
            print('Connection closed')
