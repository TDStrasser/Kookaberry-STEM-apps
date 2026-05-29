# Kookaberry WiFi Apps
This is a repository of pre-coded WiFi apps for use with the Kookaberry RP2040W and RP2350W micro-computers.

Documentation for WiFi using MicroPython can be found here: https://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html (Kookaberry specific documentation is pending)

- **Web_BME280** - A web-server script that displays temperature, humidity and air-pressure readings obtained from a BME280 sensor.  See the Web_BME280_explainer.md file for a detailed explanation:

  1. Attach a BME280 to P3 (uses the PiicoDev BME280 - the Gravity BME280 sensor needs Vcc/Gnd and SCL/SDA swapped)
  2. Run the code and look at the Kookaberry display
  3. On your phone/tablet/computer connect your WiFi to the SSID 'kookaberry', password is 12345678
  4. On your browser navigate to the URL shown on the Kookaberry display - usually 192.168.4.1
  5. You should then see a web page with the BME280 data and the current time - it refreshes every 10 seconds.

