# HX711 GPIO Driver for MicroPython — Usage Guide

> **Source:** [`hx711_gpio.py`](https://github.com/robert-hh/hx711) by robert-hh, MIT Licence.  
> This guide covers the GPIO variant of the driver (`hx711_gpio.py`), which communicates with the HX711 24-bit ADC using direct bit-banged GPIO pin handling.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Hardware Background](#2-hardware-background)
3. [Wiring](#3-wiring)
4. [Installation](#4-installation)
5. [Constructor](#5-constructor)
6. [API Reference](#6-api-reference)
7. [Calibration Procedure](#7-calibration-procedure)
8. [Usage Examples](#8-usage-examples)
9. [Power Management](#9-power-management)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

The `HX711` class provides a MicroPython interface to the **Avia Semiconductor HX711**, a precision 24-bit analogue-to-digital converter (ADC) designed specifically for bridge-type load cells (strain-gauge weigh scales). The driver communicates using two GPIO lines — a serial clock (`PD_SCK`) and a data line (`DOUT`) — with no hardware SPI or I²C peripheral required.

Key capabilities:

- Read raw 24-bit signed counts from the load cell
- Select input channel (A or B) and gain (128, 64, or 32)
- Apply tare (zero offset) and a user-defined scale factor to return calibrated weight values
- Apply an IIR (infinite-impulse response) low-pass filter to smooth noisy readings
- Enter and exit a low-power sleep mode (< 1 µA total)

---

## 2. Hardware Background

The HX711 contains an input multiplexer, a programmable-gain amplifier (PGA), a sigma-delta ADC, and an on-chip power supply regulator. All configuration is performed through pin states and the serial clock pulse count — there are no internal registers to program.

### Input channels and gain

| PD_SCK pulses per read | Channel | Gain | Full-scale input (@ 5 V AVDD) |
|------------------------|---------|------|-------------------------------|
| 25 | A | 128 | ±20 mV |
| 27 | A | 64 | ±40 mV |
| 26 | B | 32 | ±80 mV |

Channel A (gain 128 or 64) is intended for a load cell bridge. Channel B (gain 32, fixed) is commonly used for battery voltage monitoring.

### Output data rate

The RATE pin on the HX711 IC controls the sample rate:

| RATE pin | Sample rate |
|----------|-------------|
| Low (0)  | 10 Hz       |
| High (1) | 80 Hz       |

On typical breakout modules the RATE pin is pulled low, giving 10 samples per second. The driver's `read()` method will wait up to 500 ms for a conversion to complete before raising `OSError("Sensor does not respond")`.

### Output coding

Data is returned as a 24-bit two's-complement integer. The full-scale range is `0x800000` (−8,388,608) to `0x7FFFFF` (+8,388,607). The driver automatically converts this to a signed Python `int`.

---

## 3. Wiring

Connect the HX711 breakout module to your MicroPython board as follows.

### HX711 module → MCU

| HX711 pin | Function | MCU pin requirement |
|-----------|----------|---------------------|
| `DOUT` | Serial data output from HX711 | Any GPIO input pin (pull-down recommended) |
| `PD_SCK` | Serial clock / power-down input | Any GPIO **output** pin (must not be input-only) |
| `VCC` / `DVDD` | Digital supply | 3.3 V or 5 V matching MCU logic level |
| `GND` | Ground | GND |

### Load cell → HX711

A standard 4-wire load cell connects to the HX711 as follows:

| Load cell wire colour (typical) | HX711 pin |
|----------------------------------|-----------|
| Red (excitation +) | E+ |
| Black (excitation −) | E− |
| White (signal +) | A+ (INA+) |
| Green (signal −) | A− (INA−) |

> **Note:** Wire colours vary between manufacturers. Always verify with your load cell datasheet.

### Example pin assignments

| Board | `data_pin` (DOUT) | `clock_pin` (PD_SCK) |
|-------|-------------------|----------------------|
| ESP32 / ESP8266 | GPIO 12 | GPIO 13 |
| Raspberry Pi Pico | GP12 | GP13 |
| Pycom (WiPy etc.) | P9 | P10 |

---

## 4. Installation

Copy `hx711_gpio.py` to the `/lib` directory (or the root `/`) of your MicroPython device using Thonny, `ampy`, `rshell`, or `mpremote`:

```bash
# Using mpremote
mpremote cp hx711_gpio.py :/lib/hx711_gpio.py

# Using ampy
ampy --port /dev/ttyUSB0 put hx711_gpio.py /lib/hx711_gpio.py
```

No other dependencies are required beyond the standard MicroPython `machine` and `time` modules.

---

## 5. Constructor

```python
from hx711_gpio import HX711
from machine import Pin

data_pin  = Pin(12, Pin.IN,  pull=Pin.PULL_DOWN)
clock_pin = Pin(13, Pin.OUT)

hx = HX711(clock_pin, data_pin, gain=128)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clock` | `Pin` | — | Output pin connected to HX711 `PD_SCK`. **Must** be configured as an output. |
| `data` | `Pin` | — | Input pin connected to HX711 `DOUT`. Configure with `Pin.PULL_DOWN` to avoid floating readings when idle. |
| `gain` | `int` | `128` | Initial gain. Valid values: `128` (ch A), `64` (ch A), `32` (ch B). |

During construction the driver:

1. Drives `clock` low to ensure the HX711 is not in power-down mode.
2. Benchmarks the GPIO read speed to calibrate the polling loop timeout.
3. Calls `set_gain(gain)`, which performs two reads to prime the internal filter state.

---

## 6. API Reference

### `hx.read()` / `hx()`

```python
raw = hx.read()    # explicit call
raw = hx()         # shorthand via __call__
```

Returns one raw 24-bit signed integer from the ADC. Blocks until a conversion is available (DOUT falls low). Raises `OSError` if the sensor does not respond within the timeout.

If the `data` pin supports interrupts (`Pin.irq`), the driver uses a falling-edge interrupt to detect conversion completion. On platforms without IRQ support it falls back to polling.

---

### `hx.read_average(times=3)`

```python
avg = hx.read_average(times=10)
```

Returns the arithmetic mean of `times` raw readings. Useful for one-shot measurements where a small amount of averaging is acceptable.

---

### `hx.read_lowpass()`

```python
filtered = hx.read_lowpass()
```

Returns a single raw reading fed through a first-order IIR low-pass filter:

```
filtered_n = filtered_(n-1) + α × (raw - filtered_(n-1))
```

where `α` is the `time_constant` (default `0.25`). Call this method repeatedly in a loop for continuous smoothed readings. The filter state is initialised during construction.

---

### `hx.set_time_constant(value=None)`

```python
hx.set_time_constant(0.1)        # set α = 0.1 (heavy smoothing)
alpha = hx.set_time_constant()   # get current value
```

Sets or returns the IIR filter coefficient `α`. Valid range: `0 < α < 1.0`.

| `α` value | Effect |
|-----------|--------|
| Close to 1.0 (e.g., 0.9) | Fast response, minimal smoothing |
| Close to 0.0 (e.g., 0.05) | Slow response, heavy smoothing |
| Default: 0.25 | Moderate smoothing |

---

### `hx.set_gain(gain)`

```python
hx.set_gain(64)   # switch to channel A, gain 64
hx.set_gain(32)   # switch to channel B, gain 32
```

Changes the gain/channel for subsequent reads. After a gain change the HX711 requires one conversion cycle to settle; `set_gain()` performs two reads internally to prime the filter. Allow additional settling time (≥ 400 ms at 10 SPS) before trusting readings after a gain change.

---

### `hx.tare(times=15)`

```python
hx.tare()           # zero the scale with 15 averaged readings
hx.tare(times=30)   # use 30 readings for a more stable zero
```

Averages `times` raw readings and stores the result as the zero offset (`OFFSET`). Call this with nothing on the scale before weighing.

---

### `hx.set_offset(offset)` / `hx.set_scale(scale)`

```python
hx.set_offset(12345)    # set zero offset directly (raw counts)
hx.set_scale(420.5)     # set calibration factor (counts per unit)
```

Directly set the stored offset (zero point) and scale factor. Useful for restoring previously determined calibration constants without re-running the calibration procedure.

---

### `hx.get_value()`

```python
val = hx.get_value()
```

Returns `read_lowpass() − OFFSET`. This is the net ADC count above zero with smoothing applied, but before unit conversion.

---

### `hx.get_units()`

```python
weight_g = hx.get_units()
```

Returns `get_value() / SCALE`. After calibration this gives a reading in your chosen physical units (grams, kilograms, etc.).

---

### `hx.power_down()` / `hx.power_up()`

```python
hx.power_down()    # enter sleep mode (PD_SCK held high > 60 µs)
hx.power_up()      # wake up (PD_SCK driven low)
```

See [Section 9 — Power Management](#9-power-management) for details.

---

## 7. Calibration Procedure

Calibration determines two constants:

- **Offset** (`OFFSET`) — the raw count when nothing is on the scale (tare value).
- **Scale** (`SCALE`) — the number of raw counts per unit of weight (e.g., counts per gram).

### Step 1 — Find the offset

```python
from hx711_gpio import HX711
from machine import Pin

data_pin  = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
clock_pin = Pin(13, Pin.OUT)
hx = HX711(clock_pin, data_pin)

# Ensure nothing is on the scale
hx.tare(times=20)
print("Offset:", hx.OFFSET)   # record this value
```

### Step 2 — Find the scale factor

Place a known reference weight on the scale (e.g. 500 g) and read the raw value:

```python
raw_with_weight = hx.read_average(times=20)
known_weight_g  = 500.0

scale_factor = (raw_with_weight - hx.OFFSET) / known_weight_g
print("Scale factor:", scale_factor)   # record this value
```

### Step 3 — Apply the calibration constants

```python
hx.set_offset(hx.OFFSET)       # already set by tare(), shown for clarity
hx.set_scale(scale_factor)

weight = hx.get_units()
print(f"Weight: {weight:.1f} g")
```

### Step 4 — Persist the constants (optional)

Store the offset and scale factor in non-volatile memory so you can restore them on next boot without re-calibrating:

```python
import json

# Save
with open("hx711_cal.json", "w") as f:
    json.dump({"offset": hx.OFFSET, "scale": hx.SCALE}, f)

# Restore on next boot
with open("hx711_cal.json") as f:
    cal = json.load(f)
hx.set_offset(cal["offset"])
hx.set_scale(cal["scale"])
```

> **Important:** Offset will drift with temperature. For high-accuracy applications, re-tare on each power-up. Scale factor is more stable but should be re-verified periodically.

---

## 8. Usage Examples

### Minimal — raw counts

```python
from hx711_gpio import HX711
from machine import Pin

hx = HX711(Pin(13, Pin.OUT), Pin(12, Pin.IN, pull=Pin.PULL_DOWN))
while True:
    print(hx.read())
```

### Basic weigh scale

```python
from hx711_gpio import HX711
from machine import Pin
import time

hx = HX711(Pin(13, Pin.OUT), Pin(12, Pin.IN, pull=Pin.PULL_DOWN))

# --- Calibration constants (determine these using Section 7) ---
OFFSET       = 85432      # raw counts at zero load
SCALE_FACTOR = 430.2      # raw counts per gram
# ---------------------------------------------------------------

hx.set_offset(OFFSET)
hx.set_scale(SCALE_FACTOR)

print("Zeroing scale … keep platform empty …")
hx.tare(times=20)

while True:
    weight = hx.get_units()
    print(f"{weight:8.1f} g")
    time.sleep_ms(200)
```

### Continuous readings with low-pass filter

```python
from hx711_gpio import HX711
from machine import Pin
import time

hx = HX711(Pin(13, Pin.OUT), Pin(12, Pin.IN, pull=Pin.PULL_DOWN))
hx.set_time_constant(0.1)   # heavier smoothing
hx.tare(times=20)
hx.set_scale(430.2)

while True:
    # get_units() calls read_lowpass() internally
    print(f"{hx.get_units():.2f} g")
    time.sleep_ms(100)
```

### Raw millivolt reading

The embedded test script in `hx711_gpio.py` demonstrates how to convert the raw count to millivolts. The formula assumes gain=128 and AVDD = 3.3 V with a 5 V reference ratio:

```python
def read_mv(hx):
    # Full-scale input range at gain 128 = ±20 mV (with 5 V AVDD)
    # Raw full-scale = 2^23 = 8,388,608
    # Adjust for actual AVDD: multiply by (AVDD / 5)
    AVDD_V = 3.3
    return hx.read_average(times=5) / 8_388_608 * 20 * AVDD_V / 5

print(f"{read_mv(hx):.4f} mV")
```

### Channel B — battery voltage monitor

```python
from hx711_gpio import HX711
from machine import Pin

hx = HX711(Pin(13, Pin.OUT), Pin(12, Pin.IN, pull=Pin.PULL_DOWN), gain=32)
# Channel B, gain 32, full-scale ±80 mV @ 5 V AVDD
raw = hx.read_average(times=5)
voltage_mv = raw / 8_388_608 * 80
print(f"Channel B: {voltage_mv:.2f} mV")
```

---

## 9. Power Management

The HX711 can be placed in a deep sleep mode consuming less than 1 µA (analogue + digital combined). This is useful for battery-powered applications.

```python
hx.power_down()     # PD_SCK driven high; HX711 enters sleep after > 60 µs
# ... do other work or sleep the MCU ...
hx.power_up()       # PD_SCK driven low; HX711 resets and resumes
```

After `power_up()` the HX711 performs an internal reset. **Wait for at least one full settling period** before trusting readings:

| RATE pin | Settling time after power-up / reset |
|----------|--------------------------------------|
| 0 (10 Hz) | ~400 ms |
| 1 (80 Hz) | ~50 ms |

Additionally, after any reset the gain reverts to **Channel A, gain 128**. If you were using a different gain/channel, call `set_gain()` again after wake-up.

```python
import time

hx.power_up()
time.sleep_ms(500)      # wait for 10 SPS settling (400 ms typical)
hx.set_gain(64)         # restore desired gain if changed
hx.tare()               # re-zero after power-up
```

---

## 10. Troubleshooting

| Symptom | Likely cause | Solution |
|---------|-------------|----------|
| `OSError: Sensor does not respond` | DOUT never falls low | Check wiring; verify VCC and GND; check that `clock_pin` is low before calling `read()`. |
| `OSError: No trigger pulse found` | Platform has no GPIO IRQ support and polling loop timed out | Rewire, or check that the HX711 is powered. |
| Readings always near ±8,388,607 (saturated) | Load cell output exceeds ADC input range | Reduce gain (`set_gain(64)` or `set_gain(32)`); check load cell excitation voltage. |
| Readings very noisy | Poor PCB layout, electrical interference | Reduce `time_constant` for more filtering; add 100 nF decoupling on HX711 AVDD; keep signal wires short. |
| Weight reads negative | Load cell wired with reversed signal polarity | Swap the A+ and A− wires, or negate the scale factor: `hx.set_scale(-scale_factor)`. |
| Scale factor changes between sessions | Temperature drift of the load cell or HX711 | Re-tare on each power-up; re-calibrate if high accuracy is needed after large temperature changes. |
| Readings correct at calibration weight but wrong at other weights | Non-linearity of load cell | Use a higher-quality load cell; perform multi-point calibration. |
| `gain=32` gives no/wrong readings | Channel B inputs (INB+/INB−) not connected | Gain 32 uses Channel B only; connect signal to INB+/INB− pins. |
