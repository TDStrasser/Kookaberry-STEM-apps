# Web_BME280 Script — How It Works

**Script:** `Web_BME280.py`  
**Author:** Tony Strasser, AustSTEM Foundation Limited  
**Platform:** Kookaberry RP2040W / RP2350W  
**MicroPython Version:** 1.24  

---

## Overview

`Web_BME280` turns your Kookaberry into a miniature **weather station web server**. It reads temperature, humidity, and air pressure from a BME280 sensor and serves those readings as a web page that any device on the same Wi-Fi network can view in a browser. The page automatically refreshes every 10 seconds so you always see the latest readings.

---

## What You Need

| Item | Detail |
|---|---|
| Kookaberry | RP2040W or RP2350W model (has built-in Wi-Fi) |
| BME280 sensor | Plugged into port **P3** on the Kookaberry |
| A phone, tablet, or computer | Used to view the web page |

> **Tip about wiring:** The PiicoDev BME280 plugs straight in. If you use the Gravity BME280 instead, you need to swap the Vcc/Gnd and SCL/SDA wires before it will work.

---

## Section-by-Section Walkthrough

### 1. Importing Modules

```python
import network
import socket
import time
from machine import Pin, SoftI2C
import kooka, fonts
from bme280 import BME280
```

Before the script can do anything, it must load the **libraries** (pre-written collections of code) it needs:

| Module | What it does |
|---|---|
| `network` | Controls the Kookaberry's Wi-Fi hardware |
| `socket` | Lets the script send and receive data over a network connection |
| `time` | Provides timing functions (for controlling how often readings are taken) |
| `machine.Pin` / `SoftI2C` | Accesses the physical pins on the Kookaberry and creates a software-driven I²C communication bus |
| `kooka`, `fonts` | Controls the Kookaberry's built-in OLED display |
| `bme280.BME280` | Communicates with the BME280 sensor |

---

### 2. Wi-Fi Credentials

```python
ssid = 'kookaberry'
password = '12345678'
```

These two variables set the **name** (SSID) and **password** for the Wi-Fi network the Kookaberry will create. You can change them to anything you like — just remember to use the new values when connecting from your device.

---

### 3. The `webpage()` Function — Building the HTML

```python
def webpage(temperature, humidity, pressure):
    html = f"""
    ...
    """
    return str(html)
```

This function is responsible for building the web page that your browser displays. It uses an **f-string** (a Python string that can include variable values directly inside `{}` curly braces) to create a block of HTML — the language web browsers use to display pages.

Key features built into the HTML:

- **`<meta http-equiv="refresh" content="10">`** — this HTML tag tells the browser to automatically reload the page every 10 seconds, so the sensor readings stay current without you needing to press refresh.
- The three measurement values (`temperature`, `humidity`, `pressure`) are inserted directly into the HTML using `{temperature}`, `{humidity}`, and `{pressure}`.
- The function **returns** the completed HTML string so it can be sent to the browser later.

---

### 4. Setting Up the BME280 Sensor

```python
SCL = 'P3A'
SDA = 'P3B'
i2c = SoftI2C(scl=Pin(SCL), sda=Pin(SDA), freq=50000)
bme = BME280(address=0x77, i2c=i2c)
```

The BME280 sensor communicates with the Kookaberry using a standard protocol called **I²C** (pronounced "I-squared-C"). I²C uses just two wires:

- **SCL** (Serial Clock Line) — carries a timing signal that keeps both devices in sync
- **SDA** (Serial Data Line) — carries the actual data

`SoftI2C` creates a *software-driven* I²C bus on the P3A and P3B pins of port P3, running at 50,000 bits per second (`freq=50000`).

The `address=0x77` tells the script which I²C address the BME280 sensor uses — `0x77` is the hexadecimal number 119, and it is the default address used by the PiicoDev BME280.

The measurement variables are initialised to zero:

```python
bme_temperature = 0
bme_pressure = 0
bme_humidity = 0
```

---

### 5. Setting Up the Wi-Fi Access Point

```python
wlan = network.WLAN(network.AP_IF)
wlan.config(essid=ssid, password=password)
wlan.active(True)
while wlan.active() == False:
    pass
addr = wlan.ifconfig()[0]
```

Instead of *joining* an existing Wi-Fi network, the Kookaberry creates its **own** Wi-Fi network — this is called **Access Point (AP) mode**. The `network.AP_IF` argument tells the Wi-Fi hardware to operate this way.

- `wlan.config(...)` — sets the network name and password.
- `wlan.active(True)` — turns the Wi-Fi on.
- The `while` loop waits until the Wi-Fi hardware confirms it is actually active before continuing.
- `wlan.ifconfig()[0]` — retrieves the IP address assigned to the Kookaberry on its own network. This is the address you type into your browser — usually `192.168.4.1`.

The Kookaberry display shows the SSID and IP address so students know what to connect to.

---

### 6. Creating the Web Server Socket

```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)
```

A **socket** is a software endpoint that sends and receives network data. Think of it like an electrical socket on the wall — devices "plug in" to it to exchange information.

- `socket.AF_INET` — use IPv4 addresses (the standard `xxx.xxx.xxx.xxx` format).
- `socket.SOCK_STREAM` — use TCP, a reliable connection-based protocol used by web browsers.
- `s.bind(('', 80))` — attach the socket to **port 80**, which is the standard port for HTTP (web) traffic. The empty string `''` means "accept connections on any available network interface."
- `s.listen(1)` — tell the socket to start listening for incoming connections (up to 1 at a time).

---

### 7. Timing Intervals

```python
bme_interval = 2000      # Read the sensor every 2 seconds
_timer_bme = time.ticks_ms()

wlan_interval = 1000     # Check for web connections every 1 second
_timer_wlan = time.ticks_ms()
```

The script uses **non-blocking timers** — instead of using `time.sleep()` (which would freeze the whole program), it records the current time and then checks on each loop pass whether enough time has elapsed. This lets the sensor reading and web server checking happen independently and concurrently.

`time.ticks_ms()` returns the number of milliseconds since the Kookaberry started — it is used as a reference point for timing.

---

### 8. The Main Loop

```python
while True:
    ...
```

Everything from here onwards runs **forever** (until the Kookaberry is reset or powered off). The loop has two main jobs, each controlled by its own timer.

#### 8a. Reading the BME280 Sensor

```python
if time.ticks_diff(time.ticks_ms(), _timer_bme) >= 0:
    _timer_bme += bme_interval
    try:
        bme_temperature = bme.values[0]
        bme_pressure    = bme.values[1]
        bme_humidity    = bme.values[2]
        bme_read = True
    except:
        bme_temperature = 0
        bme_pressure    = 0
        bme_humidity    = 0
```

- `time.ticks_diff(...)` — calculates how many milliseconds have passed since the last reading.
- When the interval has elapsed, `_timer_bme` is advanced by `bme_interval` (2000 ms) to schedule the next reading.
- `bme.values` — returns a list of three values from the sensor: `[0]` temperature in °C, `[1]` pressure in hPa, `[2]` relative humidity in %.
- The `try/except` block handles the case where the sensor is not plugged in or fails to respond. If an error occurs, the measurements are reset to zero and `bme_read` is set to `False`.

#### 8b. Updating the Kookaberry Display

```python
disp.fill(0)
disp.setfont(fonts.mono8x8)
disp.text('%s' % __name__, 0, 6)
...
disp.show()
```

The OLED display is cleared (`fill(0)`) and then redrawn with the latest values on each sensor reading cycle:

- If `bme_read` is `True` — temperature, humidity and pressure are shown.
- If `bme_read` is `False` — the message `Plug sensor into P3` is shown instead.
- The SSID and IP address are always shown at the bottom of the screen.
- `disp.show()` — sends all the drawn content to the physical display (nothing appears until this is called).

#### 8c. Handling Web Browser Connections

```python
if time.ticks_diff(time.ticks_ms(), _timer_wlan) >= 0:
    _timer_wlan += wlan_interval
    try:
        conn, addrx = s.accept()
        request = conn.recv(1024)
        response = webpage(round(bme_temperature,1),
                           round(bme_humidity,1),
                           round(bme_pressure,1))
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()
    except OSError as e:
        conn.close()
```

Every second the script checks whether a browser has made a connection request:

1. **`s.accept()`** — waits for (accepts) an incoming connection from a browser. `conn` is the connection object; `addrx` is the browser's IP address.
2. **`conn.recv(1024)`** — reads the HTTP request sent by the browser (up to 1024 bytes). This is the standard "GET /" request a browser sends when it wants a page.
3. **`webpage(...)`** — calls the HTML builder function with the latest sensor readings, rounded to 1 decimal place.
4. **`conn.send('HTTP/1.0 200 OK...')`** — sends the HTTP response header. `200 OK` means "success". `Content-type: text/html` tells the browser to expect HTML content.
5. **`conn.send(response)`** — sends the HTML page body.
6. **`conn.close()`** — closes the connection cleanly once the page has been delivered.
7. If any network error occurs (`OSError`), the connection is closed without crashing the program.

---

## Program Flow Diagram

```
Start
  │
  ├─ Import modules
  ├─ Set Wi-Fi credentials
  ├─ Define webpage() HTML builder function
  ├─ Initialise BME280 sensor on I²C bus (P3)
  ├─ Create Wi-Fi Access Point (SSID: kookaberry)
  ├─ Wait for Wi-Fi to become active
  ├─ Get IP address → show on display
  ├─ Create TCP socket on port 80 → start listening
  │
  └─ MAIN LOOP (runs forever)
       │
       ├─ Every 2 seconds:
       │    ├─ Read BME280 → temperature, humidity, pressure
       │    └─ Update Kookaberry OLED display
       │
       └─ Every 1 second:
            ├─ Accept browser connection (if any)
            ├─ Read HTTP request from browser
            ├─ Build HTML page with latest sensor values
            ├─ Send HTTP response + HTML to browser
            └─ Close connection
```

---

## Key Concepts Introduced by This Script

| Concept | Where it appears |
|---|---|
| **Importing libraries** | `import network`, `from bme280 import BME280`, etc. |
| **Functions with parameters** | `def webpage(temperature, humidity, pressure)` |
| **f-strings** | `html = f"""..."""` — inserting variables into text |
| **I²C communication** | `SoftI2C`, `BME280` sensor initialisation |
| **Wi-Fi in AP mode** | `network.WLAN(network.AP_IF)` |
| **Sockets and HTTP** | `socket.socket()`, `s.bind()`, `conn.send()` |
| **Non-blocking timers** | `time.ticks_ms()` and `time.ticks_diff()` |
| **Try/except error handling** | Sensor read failure, network `OSError` |
| **Infinite loops** | `while True:` — the main program loop |
| **Conditional display** | Showing different content if sensor read succeeds or fails |

---

## Modifying the Script

Here are some simple changes you can try once you understand the script:

- **Change the Wi-Fi name or password:** Edit the `ssid` and `password` variables near the top.
- **Change the refresh rate:** Find `content="10"` inside the `webpage()` function and change `10` to a different number of seconds.
- **Change the sensor reading interval:** Edit `bme_interval = 2000` — the number is in milliseconds (2000 ms = 2 seconds). Do not set it below 2000 as the BME280 needs time between readings.
- **Add more information to the web page:** Edit the HTML inside the `webpage()` function to include extra text, headings, or styling.
