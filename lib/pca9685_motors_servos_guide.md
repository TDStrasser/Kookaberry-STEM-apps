# Driving Servos, DC Motors, and Steppers with the Kookaberry PCA9685 Module

*A student guide to the embedded principles behind `pca9685.py`*

This guide explains **why** the `PCA9685`, `Servo`, `Motor`, and `Stepper` classes in `pca9685.py` work the way they do, so that you can use them confidently — and eventually write similar drivers yourself. It assumes no prior embedded electronics knowledge beyond basic MicroPython (variables, classes, loops).

*This revision covers the updated driver (28 August 2026 build), which changes the continuous-servo and DC-motor speed convention to -99..+99, adds API-compatible `stop()` methods, and inserts a 50 ms software-requested zero-output interval before a commanded DC-motor direction reversal.*

---

## 0. What changed since the previous driver revision

*(this revision dated 28 August 2026 — earlier fixes and features remain documented in the later sections)*

| Issue / feature | Where | What changed |
|---|---|---|
| Speed convention changed to -99..+99 | `Servo.speed` and `Motor.speed` setters | Continuous-servo remapping changed from `-1..+1` to `-99..+99`. The DC-motor public convention changed from `-100..+100` to `-99..+99`; its internal remap endpoint is `99.99`, keeping a documented maximum command of 99 away from the PCA9685 boundary value that caused the earlier full-speed alias. |
| API-compatible stop method | `Servo.stop()` and `Motor.stop()` | Both new methods write the same channel values as their class's existing `release()` method. The source comment explicitly describes `Servo.stop()` as an API-compatibility alias; `Motor.stop()` is also byte-for-byte equivalent to `Motor.release()`. |
| Inductive-current protection during DC-motor reversal | `Motor.__init__` and the `Motor.speed` setter | The motor now remembers its last command in `_speed`. If the new and previous commands have opposite signs (`x * self._speed < 0`), the setter calls `stop()`, waits 50 ms, and only then applies the new direction. This is a fixed zero-output interval, not a gradual ramp and not a measured-current control loop. |

**Source-code precision note:** the revision header says “-99.9 to +99.9,” the class description says “-99 to +99,” and the motor calculation uses an internal endpoint of `99.99`. The executable code does not reject out-of-range values: `remap()` saturates them. This guide therefore documents **-99..+99** as the intended public API, matching the class descriptions and keeping normal commands clear of the boundary special case. 

---

## 1. The big idea: one chip, sixteen PWM channels, one I2C bus

Your Kookaberry has a limited number of GPIO pins, and generating a precise, continuous PWM signal for eight servos and four motors at once would be difficult for the RP2040/RP2350 to do directly while also running your program. The **PCA9685** solves this by being a dedicated 16-channel, 12-bit PWM generator chip that sits on the I2C bus ([NXP PCA9685 datasheet](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)).

Instead of your code toggling pins in a tight loop, you send short I2C messages telling the PCA9685 chip *what waveform to generate*, and the chip keeps generating that waveform continuously and independently — even while your MicroPython program goes off and does something else. This is a core embedded systems principle: **offload real-time, repetitive signal generation to dedicated hardware, and use software only to configure it.**

### How the PCA9685 represents a PWM signal

Every PWM channel repeats a waveform on a fixed cycle called the **period**. The PCA9685 divides each period into **4096 discrete time slots** (12-bit resolution: \(2^{12} = 4096\)) ([NXP PCA9685 datasheet](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)). For each channel it stores two 12-bit numbers:

- **ON count** — the slot number where the output switches high
- **OFF count** — the slot number where the output switches low again

This is exactly what the `pwm()` method reads and writes:

```python
def pwm(self, index, on=None, off=None):
    if on is None or off is None:
        data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
        return unpack('<HH', data)
    data = pack('<HH', on, off)
    self.i2c.writeto_mem(self.address, 0x06 + 4 * index, data)
```

Each channel's ON/OFF registers live at `0x06 + 4 * index` — four bytes per channel, sixteen channels, all in a predictable block of memory. This register-block pattern is common to almost every I2C peripheral chip, so once you understand it here you can apply it elsewhere.

Because most students only care about *how long the pulse is*, not *when in the cycle it starts*, the driver provides the simpler `duty()` method, which always starts the pulse at slot 0 and just varies where it turns off:

```python
def duty(self, index, value=None, invert=False):
    ...
    self.pwm(index, 0, value)   # ON at slot 0, OFF at slot `value`
```

`value` is a number from 0 (always off) to 4095 (always on) — this is the fundamental building block every other class in the file is built on.

### Setting the frequency, and why the internal oscillator isn't perfectly accurate

All 16 channels share **one** PWM frequency — you cannot run some channels at 50 Hz and others at 1 kHz simultaneously ([NXP PCA9685 datasheet](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)). This matters because servos expect roughly 50 Hz, while some other PWM applications (e.g. dimming an LED) work fine at much higher frequencies — but on this board, everything you connect must tolerate the frequency you chose in `PCA9685(i2c, freq=50)`.

The chip has an internal oscillator that NXP specifies as "25 MHz typical" ([NXP PCA9685 datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)) — the word *typical* is important, because this is a built-in RC-type oscillator, not a precision crystal, and real chips commonly run a few percent away from exactly 25 MHz. Hobbyist measurements have found individual PCA9685 chips running anywhere from about 23–27 MHz ([va3wam calibrateServoMotor notes](https://github.com/va3wam/calibrateServoMotor)), and Adafruit has similarly observed boards running as high as 27 MHz against the nominal 25 MHz ([Adafruit oscillator frequency discussion](https://groups.io/g/arduini/topic/oscillator_frequency/81444150)). For LED dimming this tiny frequency error is irrelevant, but because servo position is decoded from *absolute pulse duration in microseconds*, a real oscillator running a few percent fast or slow will make every commanded pulse a few percent shorter or longer than intended — a small but real source of servo positioning error. Section 3 explains the `freq_compensation` feature this driver provides to correct for it.

To get an arbitrary output frequency from that oscillator, the driver calculates a **prescale** value and writes it to a register. The corrected formula, matching the NXP datasheet exactly, is:

```python
prescale = int(25000000.0 / 4096.0 / f + 0.5) - 1
...
self._frequency = 25e6 / ((prescale+1)*4096)
```

The `- 1` (and matching `+1` when reading the frequency back) reflects how the PCA9685's PRE_SCALE register is defined: the chip internally uses `(PRE_SCALE + 1)` as the actual divider, so the register value you write must be one less than the divisor you actually want. This is a standard technique — a fast internal clock is divided down by an integer prescaler to produce the frequency you actually want — and a good reminder that when translating a datasheet formula into code, off-by-one errors in register definitions are a common and easy mistake to make (the earlier driver revision had exactly this off-by-one, since fixed).

### The `PCA9685.__init__` and I2C addressing

```python
def __init__(self, i2c, address=_I2C_ADDRESS, freq=50):
```

The PCA9685 defaults to I2C address `0x40` ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)). Before using the driver, it's good practice to run `i2c.scan()` in a fresh MicroPython session to confirm the Kookaberry can actually see the chip on the bus — if `0x40` (64 decimal) doesn't appear, check your wiring before debugging your code ([MicroPython I2C docs](https://docs.micropython.org/en/latest/library/machine.I2C.html)).

**Usage pattern for all classes below** — you always build a small object hierarchy:

```python
from machine import SoftI2C, Pin
i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PCA9685(i2c, address=0x40, freq=50)   # one controller per board
servo = Servo(controller, 1)                        # channel 1
motor = Motor(controller, 1)                         # motor output 1
stepper = Stepper(controller, 1)                     # stepper output 1
```

Every `Servo`, `Motor`, and `Stepper` object *wraps* the shared `controller` and simply calls `controller.duty(channel, value)` behind the scenes. This is a good example of **object-oriented hardware abstraction**: the low-level chip details (registers, I2C addresses, prescalers, oscillator quirks) are hidden inside `PCA9685`, so the classes built on top of it can expose a much simpler interface (`.angle`, `.speed`, `.step()`).

---

## 2. Angular (positional) servos

### The physical device

A hobby servo is a small package containing a DC motor, a gear train, and — critically — an internal potentiometer that senses shaft position and a tiny built-in control circuit (its own miniature H-bridge) that drives the motor toward whatever angle you command ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)). You are not switching the servo's internal motor directly — you are sending it a *position command* and letting its internal electronics do the driving.

### Why pulse *width*, not duty cycle percentage, is what matters

This is the single most important concept for angular servos: **the servo cares about the absolute time (in microseconds) that the pulse stays high, not the percentage of the cycle it occupies.** A pulse of about 1000 µs commands one extreme of travel, about 1500 µs commands the centre, and about 2000 µs commands the other extreme — repeated roughly every 20 ms (50 Hz) ([Adafruit CircuitPython servo guide](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf), [Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)). The driver now defaults to exactly this conventional `min_us=1000, max_us=2000` range, which is a safer starting point for unknown servos than a wider range — you can always widen it deliberately once you've confirmed your specific servo tolerates more travel.

### Converting microseconds to a PCA9685 duty count

Because the PCA9685 only understands 12-bit counts (0–4095) over the chosen period, the driver must convert your desired pulse width in microseconds into a count:

```python
def _us2duty(self, value):
    return int(4095 * value / self.period + 0.5)
```

At 50 Hz, `self.period` is (ideally) 20,000 µs, so:

| Pulse width | Approx. duty count (0–4095) |
|---|---:|
| 1000 µs | ~205 |
| 1500 µs | ~307 |
| 2000 µs | ~410 |

You never need to do this arithmetic yourself — it happens inside `Servo.__init__` and `_us2duty()` — but understanding it explains *why* the class asks for `min_us`/`max_us` rather than raw duty numbers, and why an inaccurate `self.period` (Section 3) would throw every one of these conversions off by the same percentage.

### Using the `angle` property

```python
servo = Servo(controller, 1, min_us=1000, max_us=2000, degrees=180)
servo.angle = 90      # move to the centre of travel
```

The setter linearly maps your requested angle onto the calibrated duty range and writes it straight to the PCA9685 channel:

```python
duty = self.min_duty + (self.max_duty - self.min_duty) * x / self._degrees
```

This is a **linear remap** — the same pattern used throughout the file's helper `remap()` function. Learning to read this one line means you can read almost every other property setter in the module. (Section 3 explains the direction/midpoint transform that now happens to `x` immediately before this line.)

### Calibration: `midpoint_us` + `range_us` as an alternative

```python
servo = Servo(controller, 8, midpoint_us=1500, range_us=2400, degrees=180)
```

Not every servo's centre is exactly 1500 µs, and not every servo accepts exactly 1000–2000 µs. Real servos vary by manufacturer, and pushing a pulse beyond a servo's mechanical limit causes it to buzz, draw excess current, heat up, and can strip its gears ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)). Calibration means experimentally finding the safe `min_us`/`max_us` (or `midpoint_us`/`range_us`) for *your* specific servo before trusting it with a full sweep. Always start a new servo cautiously — command small angle changes first and watch/listen for strain.

### Which physical board is your `Servo` object talking to?

The channel number you pass to `Servo(controller, channel)` is a **software channel number handled entirely by this driver** — it isn't necessarily the same number printed on the silkscreen of whatever physical PCA9685 board you've wired up. Now that the valid range has been extended to the chip's full **1–16**, it's worth being explicit about how that number maps to real hardware, because it differs by board:

| Board | Servo channels available | Software channel → PCA9685 hardware channel | Default I2C address |
|---|---|---|---|
| AustSTEM Quokka Motor-Servo Driver module | 1–8 (channels 9–16 are wired to the on-board H-bridges for `Motor`/`Stepper`, not servo headers) | Straight-through: channel `n` → PCA9685 channel `n-1` | `0x40` |
| Generic 16-channel PCA9685 breakout (e.g. Adafruit's 16-Channel PWM/Servo Driver) | 1–16, all usable as plain servo headers | Straight-through: channel `n` → PCA9685 channel `n-1` | `0x40` ([Adafruit 16-Channel PWM/Servo Driver overview](https://learn.adafruit.com/16-channel-pwm-servo-driver/overview)) |
| Core Electronics PiicoDev Servo Driver | 4 (silkscreen-labelled 1–4 only) | **Reversed**: silkscreen 1 → PCA9685 channel 3, 2 → 2, 3 → 1, 4 → 0 | `0x44` ([Core Electronics PiicoDev Servo Driver product page](https://core-electronics.com.au/piicodev-servo-driver.html)) |

The reversed PiicoDev mapping isn't a guess — it's documented directly in Core Electronics' own driver, which this Kookaberry driver is derived from (see the file header). Their original module maps servo channels with `self.channel = {4:0,3:1,2:2,1:3}[channel]`, explicitly commented `# map {silk label:PCA9685 channel}` ([Core Electronics `PiicoDev_Servo.py`, GitHub](https://github.com/CoreElectronics/CE-PiicoDev-PyPI/blob/main/src/PiicoDev_Servo.py)). This Kookaberry driver keeps that exact line, commented out, immediately above its own simpler replacement:

```python
#        self.channel = {4:0,3:1,2:2,1:3}[channel] # original PiicoDev channel mapping
self.channel = int(channel)-1 # map to PCA9685 channels 0-7 inclusive
```

Because that reversal was left out when this line was replaced, **if you plug a PiicoDev Servo Driver into a Kookaberry running this driver, `Servo(controller, 1)` will actually drive whatever you've physically plugged into the header silkscreened "4", not "1"** — and vice versa for channels 2↔3. Two practical consequences worth flagging to students:

- Either physically remember the reversal (plug your "first" servo into the header labelled **4**, your "second" into **3**, and so on), or translate your own channel number before constructing the `Servo` object, e.g. `Servo(controller, {1:4,2:3,3:2,4:1}[my_channel])`.
- The PiicoDev board's I2C address defaults to `0x44`, not the PCA9685's usual `0x40` ([Core Electronics PiicoDev Servo Driver product page](https://core-electronics.com.au/piicodev-servo-driver.html)) — you must pass it explicitly, e.g. `PCA9685(i2c, address=0x44)`, or the driver won't find the chip on the bus at all.

If you're using the Quokka board itself, there's no reason to go past channel 8 for servos — channels 9–16 are physically wired to the H-bridge motor/stepper outputs, so constructing a `Servo` there won't damage anything, but it also won't do anything useful (you'd be sending servo pulses into a motor driver's logic input). The 1–16 range exists to support generic breakout boards and the PiicoDev board, not to unlock extra servo headers on the Quokka board itself.

### Power supply — why it matters here

Servos draw large, spiky currents, especially several hundred milliamps for small servos and over 1 A for high-torque servos under load ([Adafruit PCA9685 hookup guide](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up)). Never power servos from the Kookaberry's own regulated rail — the current surge can brown out or reset the board. Always give servos their **own stable 5–6 V supply**, and connect that supply's ground to the Kookaberry/PCA9685 ground so all the PWM signal levels share the same 0 V reference ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)).

### `release()`

```python
servo.release()   # sets duty = 0, stops sending a control pulse
```

If the requested zero duty produces no pulse at the pin, most analog servos stop actively holding their position (they go "limp"), which is useful when you want a servo-driven arm to be moved by hand, or simply to reduce noise/current when a servo isn't in active use. See the `PCA9685.duty()` boundary-value note in Section 5 before relying on this driver's present implementation as a guaranteed full-off command.

---

## 3. Servo calibration features: oscillator drift, direction, and midpoint

### `freq_compensation` — correcting for the real oscillator, not the ideal one

```python
def __init__(self, controller, channel, min_us=1000, max_us=2000, degrees=180,
             midpoint_us=None, range_us=None, freq_compensation=0,
             clockwise=True, mid_zero=True):
    if freq_compensation < -15: freq_compensation = -15
    if freq_compensation > 15: freq_compensation = 15
    self.freq_compensation = 1 + freq_compensation/100
    self.freq = controller.frequency
    self.period = 1_000_000/(self.freq * self.freq_compensation)  # microseconds
```

Recall from Section 1 that `controller.frequency` is always calculated assuming the internal oscillator runs at *exactly* 25 MHz — the PCA9685 has no way to measure its own true oscillator speed, so both the frequency you request and the frequency it reports back rely on that same nominal assumption ([NXP PCA9685 datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)). If the chip's real oscillator actually runs faster or slower than 25 MHz, the *true* physical PWM period will be correspondingly shorter or longer than the "nominal" period implied by `controller.frequency` — even though the chip still believes it is producing, say, exactly 50 Hz.

`freq_compensation` is a percentage (clamped to ±15%) that you supply once you know how far off your specific board's oscillator actually is — for example, by measuring the real PWM period on an oscilloscope, or by observing at what commanded pulse width a servo actually reaches a known physical position ([va3wam calibrateServoMotor notes](https://github.com/va3wam/calibrateServoMotor); [kpower.com PCA9685 troubleshooting notes](https://www.kpower.com/insight_servo/7483.html)). A positive value tells the class "this chip's oscillator — and therefore its real output frequency — runs this many percent *faster* than nominal," which shortens the `self.period` used for every microsecond-to-duty conversion, keeping commanded pulse widths accurate to the *real* hardware timing rather than the theoretical 25 MHz assumption:

```python
self.period = 1_000_000/(self.freq * self.freq_compensation)
```

This correction only affects how the `Servo` object converts your requested microseconds into a duty count — it does not change any register on the PCA9685 chip itself. It is a purely software-side calibration, per servo object, and (because it only takes a single percentage) is deliberately simple compared to the alternative of measuring and hard-coding an actual oscillator frequency in Hz, as some other PCA9685 libraries do (e.g. Adafruit's `setOscillatorFrequency()`) ([arduini group oscillator frequency discussion](https://groups.io/g/arduini/topic/oscillator_frequency/81444150)).

**How would a student determine the right value?** Command a known pulse width (e.g. the servo's expected 1500 µs centre) and observe whether the servo actually sits at centre. If it consistently sits slightly off-centre in a repeatable direction, or if a full sweep consistently over/under-shoots a known mechanical limit, that's a sign the real oscillator differs from 25 MHz and a small `freq_compensation` value can be tuned in to correct it. Leaving it at the default `0` is perfectly fine for most classroom purposes — the error is normally only a few percent and most servos have enough mechanical deadband to absorb it without students ever noticing.

### `clockwise` and `mid_zero` — adapting to how the servo is mounted, and what "zero" should mean

These two new boolean flags change how the `angle` property interprets the number you assign to it, *before* it gets remapped to a duty cycle:

```python
@angle.setter
def angle(self, x):
    if self.clockwise == True: x = self._degrees - x        # Transform the direction of rotation
    if self.mid_zero == True:                                # Compensate for zero midpoint
        if self.clockwise == True: x = x - 90
        else: x = x + 90
    duty = self.min_duty + (self.max_duty - self.min_duty) * x / self._degrees
    ...
```

Think of these as two independent, stackable adjustments:

- **`clockwise`** answers "does increasing the angle I command make the servo rotate the way I expect, or the opposite way?" Two servos mounted as mirror images of each other (e.g. on the left and right side of a robot chassis) will rotate in visually *opposite* directions for the same pulse width, unless one of them has `clockwise` set the other way. When `clockwise=True`, the class internally reverses the mapping (`x = self._degrees - x`) so that increasing your commanded angle rotates the shaft in the "clockwise" sense as you've physically mounted it; `clockwise=False` uses the raw, un-reversed mapping.
- **`mid_zero`** answers "should an angle of 0 mean *one mechanical extreme* of the servo's travel, or the *centre* of its travel?" With `mid_zero=False`, angle 0 is one end of travel and angle `degrees` (typically 180) is the other end — the same convention used by the earlier driver revision. With `mid_zero=True` (the new default), angle 0 is redefined to sit at the servo's centre, so a typical 180° servo now naturally accepts roughly **-90 to +90** as its usable angle range — a much more intuitive convention if you're describing, say, a sensor mount pointing "0° = straight ahead, negative = left, positive = right."

Because these two flags combine, it helps to see the effect on a 180° servo (`degrees=180`) worked through directly:

| `clockwise` | `mid_zero` | Commanded angle 0 means... | Increasing angle rotates... |
|---|---|---|---|
| `False` | `False` | one mechanical extreme (`min_duty`) | toward the other extreme (`max_duty`) — same behaviour as the previous driver revision |
| `True` | `False` | the *other* mechanical extreme (`max_duty`) | toward the first extreme (`min_duty`) — direction reversed |
| `False` | `True` | the servo's centre | toward the `max_duty` extreme as angle increases past 0 |
| `True` | `True` (new default) | the servo's centre | toward the `min_duty` extreme as angle increases past 0 |

This matches the module's own test example, which calibrates a servo with the new defaults and then commands it through `0`, `-45`, and `-90`:

```python
servo = Servo(controller, 8, midpoint_us=1500, range_us=2400, degrees=180,
              freq_compensation=12, clockwise=True, mid_zero=True)
servo.angle = 0     # centre of travel
servo.angle = -45   # 45° toward one extreme
servo.angle = -90   # that extreme
```

**A caveat worth knowing:** `mid_zero`'s offset is hard-coded to exactly 90 (`x - 90` / `x + 90`), which assumes a servo with `degrees=180` (so that 90 really is the half-way point). If you ever construct a `Servo` with a different `degrees` value and also set `mid_zero=True`, the "centre" it computes will not actually be at the geometric midpoint of your travel range — worth testing explicitly if you use a non-180° servo with `mid_zero` enabled.

**Resolved in this revision:** an earlier version of the getter returned `self._angle` saved *after* the `clockwise`/`mid_zero` transform had already been applied, so reading back `servo.angle` immediately after `servo.angle = -45` wouldn't necessarily show you `-45` again. The setter now assigns `self._angle = x` at the very start, before any transform runs, so `servo.angle` reliably returns exactly what you last assigned to it — you no longer need to track the commanded angle yourself in a separate variable.

---

## 4. Continuous-rotation servos

### What's actually different inside the servo

A continuous-rotation servo looks identical to a positional servo on the outside, but its feedback potentiometer has been disconnected or replaced with fixed resistors, so its internal control circuit can never detect "I've reached the commanded angle" — it just keeps driving the motor ([Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)). The result: **the same pulse-width signal now means something completely different.**

### Pulse width now means speed and direction, not angle

| Pulse width | Angular servo | Continuous servo |
|---|---|---|
| ~1000 µs | full travel one way | full speed one direction |
| ~1500 µs | centre position | **stopped** |
| ~2000 µs | full travel other way | full speed other direction |

Parallax's own continuous servo documents 1300 µs as full-speed clockwise, 1500 µs as stop, and 1700 µs as full-speed counter-clockwise, with intermediate pulses giving intermediate speeds ([Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)). This is why `servo.angle = 90` is meaningless for these devices — there is no angle to command, only a throttle.

### Using the `speed` property

```python
speed = Servo(controller, 2, min_us=1000, max_us=2000)   # calibrate to your servo's neutral!
speed.speed = 0       # stop (as close to neutral pulse as your calibration allows)
speed.speed = 99      # full commanded speed in one direction
speed.speed = -99     # full commanded speed in the other direction
```

```python
@speed.setter
def speed(self,x):
    self._speed = x
    duty = int(remap(x, -99, 99, self.min_duty, self.max_duty)+0.5)
    self.controller.duty(self.channel, duty)
```

This revision changes the continuous-servo scale from the earlier fractional -1..+1 convention to **-99..+99**, matching the DC-motor API. `remap()` saturates values outside that interval rather than raising an exception, but -99..+99 is the documented range applications should use. The property reuses the exact same `min_duty`/`max_duty` calibration machinery as the angular servo (including the `freq_compensation` correction from Section 3) — note that `speed`, unlike `angle`, does **not** apply the `clockwise`/`mid_zero` transform, so those two flags only affect positional use of the class.

Continuous servos now also have `stop()`. Its implementation is identical to `release()`:

```python
def stop(self):
    self.controller.duty(self.channel, 0)
```

This is intended to remove the PCA9685 control pulse rather than command the calibrated neutral pulse. Therefore `servo.speed = 0` and `servo.stop()` are not the same API operation: the former maps zero to the midpoint pulse that tells a continuous servo to stop under active control, while the latter requests zero duty, like `servo.release()`. What a particular servo does after signal loss is device-dependent, so use `speed = 0` when a defined neutral command is required. Section 5 explains why the driver's current zero-duty register special case is worth verifying on hardware.

**Practical trimming tip:** because the manufactured "neutral point" of a continuous servo is rarely exactly 1500 µs, students should expect to experimentally find the pulse width that actually gives zero rotation for their specific unit, then treat that as the servo's true centre when picking `min_us`/`max_us` (or use the physical trim screw many continuous servos have) ([Adafruit CircuitPython servo guide](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf)).

### Typical uses

Continuous servos are popular for small robot wheels and simple drive systems, because the motor, gearbox, and an entire miniature H-bridge speed controller are all bundled into one servo-shaped, servo-cabled unit — no separate motor driver chip required ([Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)).

The same power-supply advice from Section 2 applies: use a separate, adequately rated supply, common ground, and start with small speed commands before ramping up.

---

## 5. DC motors through an H-bridge (e.g. the DRV8833)

### Why you need an H-bridge at all

A plain brushed DC motor spins one way when current flows through it in one direction, and the opposite way when current is reversed. A microcontroller pin can only ever be high or low, single-direction — it cannot reverse current by itself, and it usually can't supply enough current to run a motor directly. An **H-bridge** is an arrangement of four electronic switches (in the DRV8833's case, MOSFETs) around the motor, shaped like the letter H, that lets you connect either side of the motor to either supply rail — reversing current direction on command ([SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)).

The DRV8833 packs **two** independent H-bridges into one chip, so it can drive two separate DC motors — or, as you'll see in Section 6, be repurposed to drive one bipolar stepper ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)).

### The IN1/IN2 truth table

Each H-bridge is controlled by two logic inputs. The DRV8833 datasheet gives this behaviour ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)):

| IN1 | IN2 | Result |
|---|---|---|
| 0 | 0 | Coast (both outputs high-impedance / freewheel) |
| 0 | 1 | Reverse |
| 1 | 0 | Forward |
| 1 | 1 | Brake (both outputs pulled low) |

Notice this is a **digital** table — forward or reverse is selected by *which* input is high, not by *how much*. Speed control is a separate concept, layered on top by PWM (see next section).

### Where PCA9685 PWM fits in

The PCA9685 is not powerful enough, and not designed, to drive a motor's current directly — its outputs are small-signal logic outputs at the chip's logic voltage level ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)). Instead, PCA9685 channels connect to the DRV8833's IN1/IN2 **logic inputs**, and the DRV8833 itself switches the much larger motor current. This division of labour — small, precise digital signals controlling a separate high-current switching stage — is the same principle used throughout power electronics.

Because the DRV8833 treats roughly 2.0 V and above as a logic "high" on its inputs, and the Kookaberry/PCA9685 logic side runs at 3.3 V, the PCA9685's outputs are comfortably above that threshold with no extra level-shifting needed ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)).

### How the driver implements PWM speed control

The `Motor` class allocates **two PCA9685 channels per motor** — one that maps to the H-bridge's forward input, one to reverse:

```python
self.channel_fwd = 8 + (motor-1) * 2
self.channel_rev = 9 + (motor-1) * 2
```

and its `speed` setter drives *one* of those channels with a PWM duty cycle proportional to `abs(speed)`, while forcing the other to zero:

```python
duty = int(remap(abs(x), 0, 99.99, 0, 4095))
if x > 0:
    self.controller.duty(self.channel_rev, 0)
    self.controller.duty(self.channel_fwd, duty, invert=True)
elif x < 0:
    self.controller.duty(self.channel_fwd, 0)
    self.controller.duty(self.channel_rev, duty, invert=True)
else:
    self.stop()
```

Rather than holding IN1 permanently high and pulsing IN2 (a very common alternative scheme), this driver **PWMs the active direction input itself** and requests zero duty on the *other* direction input. With correctly encoded PCA9685 boundary states, this is the DRV8833's fast-decay PWM scheme: increasing active-input duty increases the fraction of each PWM period spent driving forward or reverse, while two genuinely low inputs select coast ([TI DRV8833 datasheet, Table 2](https://www.ti.com/lit/gpn/DRV8833)). The current `duty(..., 0)` implementation needs the hardware check described below, so this electrical state should not be assumed solely from the method name.

```python
motor = Motor(controller, 1)
motor.speed = 60      # 60% forward
motor.speed = -99     # full commanded reverse
motor.speed = 0       # calls release(); intended zero-drive state
```

Both `release()` and the new `stop()` method, in effect, make the same two calls:

```python
def stop(self):
    self.controller.duty(self.channel_fwd, 0)
    self.controller.duty(self.channel_rev, 0)
    self._speed = 0

def release(self):
    self.stop()
```

At the `Motor` API level, `stop()`, `release()`, and assigning `speed = 0` therefore request the same output state. 
The separate name is useful for compatibility with programs written for other motor-controller APIs.

### Reversal protection: stop, wait 50 ms, then drive the other way

A rotating brushed DC motor presents two related electrical effects during reversal. First, winding inductance resists an instantaneous change in current: TI's DRV8833 datasheet says interrupted motor current must continue to flow as **recirculation current**, with the `0,0` input state defined as coast/fast decay and the `1,1` state as brake/slow decay ([TI DRV8833 datasheet, Sections 7.3.2–7.3.3](https://www.ti.com/lit/gpn/DRV8833)). Second, while the rotor is still turning, the motor also acts as a generator and can return energy to the supply; TI therefore recommends local bulk capacitance and voltage-rating margin for cases where “the motor transfers energy to the supply” ([TI DRV8833 datasheet, Section 9.1](https://www.ti.com/lit/gpn/DRV8833)). “Back-EMF” is often used loosely for this whole reversal transient, although inductive current persistence and speed-generated EMF are physically distinct contributions.

Immediately commanding the opposite bridge polarity asks the winding current to reverse while existing current and mechanical energy are still present. TI's current-recirculation application note states that an inductive load's existing current direction initially persists even when opposing voltage is applied, and that the bridge needs a safe decay path to avoid damage to its power switches ([TI, *Current Recirculation and Decay Modes*, Section 1](https://www.ti.com/lit/an/slva321a/slva321a.pdf)). TI's H-bridge training material likewise explains that dead time—all FETs off—lets current decay, and labels coast as fast decay and brake as slow decay ([TI, *Brushed DC Motor 2: The H-Bridge*, pp. 5–7](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6059539558001.mp4/subassets/brushed_dc_motor_2-the_h-bridge.pdf)).

The new setter implements a simple, open-loop mitigation:

```python
def speed(self, x):
    duty = int(remap(abs(x), 0, 99.99, 0, 4095))
    if (x * self._speed) < 0:   # opposite signs: a direct reversal
        self.stop()             # request zero output on both channels
        sleep_ms(50)            # fixed decay interval
    # apply the requested forward/reverse channel state ...
    self._speed = x
```

`Motor.__init__` now initialises `_speed = 0`, so the first command cannot be mistaken for a reversal. A delay occurs only when two consecutive non-zero commands have opposite signs; `+60 → -60` triggers it, while `+60 → 0 → -60` does not because assigning zero updates `_speed` to zero. During a direct reversal the method blocks the caller for at least 50 ms, requests zero on both bridge-input channels, then applies the target duty in one step. It does **not** ramp through intermediate speeds, examine the DRV8833 `nFAULT` output, measure winding current, or verify that either electrical current or rotor speed has actually reached zero.

The 50 ms interval is therefore a pragmatic fixed settling time, not a universal motor constant. Actual current-decay and spin-down time depends on the motor's inductance, resistance, speed, inertia, load, supply, decay path, and local capacitance. The DRV8833 itself also provides internal dead time and overcurrent protection, but TI explicitly presents current regulation, protection, supply bypassing, and system-level testing as separate design concerns ([TI DRV8833 datasheet, Sections 6.5, 7.3.3, 7.3.5 and 9.1](https://www.ti.com/lit/gpn/DRV8833)). Software delay should therefore be treated as an additional mitigation, not a replacement for correct current sizing, current limiting, supply decoupling, and hardware validation.

### The historical `speed = 100` bug, and why the new maximum is 99

The previous driver revision had a genuine bug: commanding `motor.speed = 100` (full forward) or `motor.speed = -100` (full reverse) behaved exactly like `motor.speed = 0` — the motor didn't reach full speed, it stopped. Tracing through the old code shows precisely why, and it's a useful lesson in how dangerous it is for a calculation to land exactly on a boundary value.

The old setter computed:

```python
duty = int(remap(abs(x), 0, 100, 0, 4095))   # old, buggy version
```

For `x = 100`, `remap(100, 0, 100, 0, 4095)` comes out to exactly `4095` — the very top of the PCA9685's 12-bit range. That value is then passed through `controller.duty(self.channel_fwd, duty, invert=True)`. Inside `PCA9685.duty()`, `invert=True` flips the value first:

```python
if invert:
    value = 4095 - value   # 4095 - 4095 = 0
```

A commanded duty of exactly 4095 becomes exactly 0 after inversion — and `value == 0` is one of `duty()`'s two special-cased boundary values, writing `self.pwm(index, 0, 4095)` to the chip. Now compare that to what `Motor.release()` writes to the very same channel: `self.controller.duty(self.channel_fwd, 0)`, which (with the default `invert=False`) also hits the `value == 0` branch and writes the *identical* `self.pwm(index, 0, 4095)`. **Full forward speed and a fully released motor were writing the same register values to the forward channel** — not because of some subtle electrical issue, but because two logically distinct commanded states (`100` and `0`) happened to alias to the exact same code path once you follow the arithmetic all the way through.

The 11 July revision fixed this by changing the remap denominator from `100` to `100.001`:

```python
duty = int(remap(abs(x), 0, 100.001, 0, 4095))   # 11 July fix
```

`remap(100, 0, 100.001, 0, 4095)` works out to `4095 * 100/100.001 ≈ 4094.96`, which `int()` truncates down to `4094` — one count short of the boundary. The 28 August revision adopts the cross-driver convention of -99..+99 and changes the internal endpoint again:

```python
duty = int(remap(abs(x), 0, 99.99, 0, 4095))   # current version
```

At the documented maximum `x = 99`, this produces 4054 before inversion, comfortably clear of 4095. Because `remap()` saturates rather than validates, however, `abs(x) >= 99.99` still produces exactly 4095 and re-enters the boundary path. Applications should therefore honour the documented ±99 limit rather than assuming larger values are harmless synonyms for full speed.

### Ratings you must respect

The DRV8833 accepts a motor supply from about 2.7 V to 10.8 V, and depending on package, is rated around 1.5 A RMS / 2 A peak per bridge (some carrier boards, e.g. Pololu's, spec closer to 1.2 A continuous per channel) ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833); [Pololu DRV8833 carrier guide](https://www.pololu.com/product-info-merged/2130)). Crucially, a motor's **stall current** (drawn when the shaft can't turn — e.g. jammed or under heavy load) is typically much higher than its free-running current, and this is what actually trips the DRV8833's overcurrent, thermal, or undervoltage protection ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)). Choose motors and supplies that respect these limits — the built-in protection is a safety net, not a substitute for correct sizing.

### Motor power vs. logic power

Like servos, DC motors need a **separate, adequately rated motor supply** (VM) distinct from the Kookaberry/PCA9685 logic supply, with grounds tied together so the IN1/IN2 logic levels are referenced correctly ([SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)). Motors are **inductive loads** — when current through them is switched, they resist the change and can generate damaging voltage spikes; H-bridge driver ICs like the DRV8833 include internal circuitry to manage this (often described in terms of "fast decay/coast" vs "slow decay/brake" behaviour), which is part of why you should always drive a motor through a proper H-bridge chip rather than switching it with a bare transistor ([TI application note on current recirculation](https://www.ti.com/lit/an/slva321a/slva321a.pdf)).

---

## 6. Stepper motors

### Why steppers are different from both servos and plain DC motors

A stepper motor doesn't spin continuously in response to a single voltage — it rotates in fixed, discrete increments ("steps") as you energise its coils in a particular sequence, one step at a time ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)). A typical stepper might move 1.8° per full step, meaning 200 steps make one full revolution, and — importantly — the position error from one step does not accumulate under normal operation ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). This is what makes steppers so useful for **open-loop positioning**: your program can simply *count* the steps it has commanded and trust that the motor shaft is where it should be, without needing an angle sensor or encoder to confirm it — provided the motor never misses a step.

### Bipolar steppers and why they need two H-bridges

A bipolar stepper has two independent windings ("coils"), and current must be driven through *each* winding in either direction to produce continuous rotation — exactly the same "reverse current to reverse behaviour" problem as a DC motor, just applied to two coils instead of one. That's why a bipolar stepper needs **two H-bridges**: one per winding ([TI DRV8833 product page](https://www.ti.com/product/DRV8833)). This is precisely why the same DRV8833 chip that drives two independent DC motors can, alternatively, be wired to drive one bipolar stepper — it already contains two H-bridges.

### Step sequencing: what "stepping" really means electrically

Full-step drive energises coils in a repeating four-phase sequence, and each transition to the next phase combination is what makes the rotor advance by one step ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). Half-stepping interleaves additional intermediate combinations for finer resolution, and microstepping goes further still, proportioning the current between adjacent phases to produce smoother, smaller effective steps — but microstepping requires actual analog current control in the driver, not just on/off switching ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)).

The `Stepper` class implements a straightforward **full-step-style** sequence using four PCA9685 channels (mapped to the two H-bridges' four logic inputs):

```python
self.coil_1_fwd = 8 + (stepper-1) * 4
self.coil_1_rev = 9 + (stepper-1) * 4
self.coil_2_fwd = 10 + (stepper-1) * 4
self.coil_2_rev = 11 + (stepper-1) * 4
```

`step()` walks through the four channels in order, turning one fully on (`duty = 4095`) while turning its "two steps ago" complementary channel off, and pauses `pulse_length` milliseconds between each transition:

```python
for coil in range(0, abs(steps)):
    self.controller.duty(channels[(coil+2)%4], 0)     # switch off the complementary H-bridge output
    self.controller.duty(channels[coil%4], 4095)       # switch the next coil on
    sleep_ms(self.pulse_length)
```

Because each channel is simply switched fully on or fully off (not proportionally driven), this is genuinely a **full-step** sequence, not microstepping — a useful, honest teaching point: a PCA9685 plus a plain H-bridge chip gives you basic step sequencing, but true microstepping needs a dedicated stepper driver chip with current-sensing/regulation circuitry ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)).

Reversing direction is simply reversing the order the four channels are stepped through:

```python
if steps > 0:
    channels = [self.coil_1_fwd, self.coil_2_fwd, self.coil_1_rev, self.coil_2_rev]
elif steps < 0:
    channels = [self.coil_2_rev, self.coil_1_rev, self.coil_2_fwd, self.coil_1_fwd]
```

### Timing: how RPM becomes a delay

```python
def calculate_pulse(self, rpm, steps_per_rev, freq):
    pulse_length = int(60000 / rpm / steps_per_rev + 0.5)   # ms per step
    if pulse_length < int(1000 / freq + 0.5):               # can't be faster than one PWM period
        raise Exception("Stepper Motor RPM too high %d" % rpm)
    return pulse_length
```

This converts your desired rotational speed (revolutions per minute) into "how many milliseconds to wait between each step," given how many steps make up one revolution. This is now a method on `Stepper` itself (called internally as `self.calculate_pulse(...)`) rather than a standalone module function, but its job is unchanged: it validates and computes the same per-step delay. The built-in sanity check refuses speeds that would require stepping faster than the PCA9685's own PWM period allows — a good example of validating a physical constraint in software before it causes silent, confusing failures.

### Using the class

```python
stepper = Stepper(controller, 1, steps_per_rev=512, rpm=6)
stepper.step(200)             # move 200 steps forward, then release the coils
stepper.step(-50, hold=True)  # move 50 steps backward and keep holding torque afterward
stepper.angle(90, rpm=10)     # rotate 90° at 10 RPM
```

`angle()` is a thin convenience wrapper that just converts a desired angle into a step count using `step_angle = 360 / steps_per_rev`, then calls `step()`:

```python
def angle(self, degrees, hold=False, rpm=None):
    steps = int(degrees / self.step_angle + copysign(0.5, degrees))
    self.step(steps, hold, rpm)
```

The `copysign(0.5, degrees)` term is what makes rounding correct for negative angles too. Plain `int(x + 0.5)` rounding works fine for positive numbers (`int(4.6) = 4`, and adding 0.5 first bumps genuine halves and above up to the next integer), but Python's `int()` always truncates *toward zero*, so applying the same `+ 0.5` trick to a negative number rounds it toward zero rather than away from it — e.g. `int(-4.6 + 0.5) = int(-4.1) = -4`, one step short of the correct answer of `-5`. `copysign(0.5, degrees)` returns `+0.5` for a positive angle and `-0.5` for a negative angle, so the correction is always applied in the direction that rounds *away from zero*, giving symmetric, correct rounding for both directions — a nice general-purpose pattern worth remembering any time you round signed values in Python.

### Torque, speed, and why steppers are used open-loop

Winding inductance limits how fast current can rise in a coil each time it's energised; since torque is roughly proportional to current, driving steps faster than the current has time to build reduces available torque — this is why steppers typically have strong low-speed/holding torque but lose torque at high step rates ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). Because your program can simply count commanded steps to know the shaft position (no feedback sensor needed), steppers are widely used for open-loop positioning in things like 3D printers and camera rigs — but this trust breaks down if the motor is overloaded, accelerated too abruptly, or driven faster than it can keep up with, causing **missed steps** and a permanently wrong position estimate until the system is re-homed ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)). Projects that must know an absolute starting position, or must detect missed steps, typically add a limit switch, home switch, or encoder.

---

## 7. Wiring and power safety — the rules that apply to everything above

1. **Separate logic power from motor/servo power.** The Kookaberry/PCA9685 logic side should be powered from the board's own logic supply; servo V+ and motor VM/VIN should come from a separate, adequately rated external supply ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all); [SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)).
2. **Always tie the grounds together.** I2C, PWM, and H-bridge logic signals are all measured relative to ground — if the logic and power-supply grounds aren't common, "high" and "low" become meaningless and behaviour becomes erratic ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)).
3. **Size your supply for the worst case, not the average case.** Several servos moving simultaneously, or a motor stalling under load, draws far more current than gentle, unloaded operation — undersized supplies cause brownouts, resets, or driver shutdown ([Adafruit PCA9685 hookup guide](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up); [Pololu DRV8833 carrier guide](https://www.pololu.com/product-info-merged/2130)).
4. **Never power servos or motors from the Kookaberry's own 3.3 V/5 V logic rail.** Current spikes from actuators can corrupt or reset the whole board.
5. **Test incrementally.** Confirm `i2c.scan()` sees the PCA9685, then confirm one channel's duty cycle changes something measurable, then connect one unloaded actuator, and only then move to multiple actuators or full load ([MicroPython I2C docs](https://docs.micropython.org/en/latest/library/machine.I2C.html)).
6. **Watch and listen.** Buzzing, unexpected heat in a driver chip, motor, or wire, or a servo that won't settle are all signs to stop and re-check calibration or wiring before continuing.
7. **Mind moving parts.** Gears, wheels, and linkages can pinch fingers or hair, especially when a program unexpectedly starts a movement — keep hands and loose items clear while testing new code.

---

## 8. Quick reference — classes and methods

| Class | Construct with | Key methods/properties | What they physically do |
|---|---|---|---|
| `PCA9685` | `PCA9685(i2c, address=0x40, freq=50)` | `.frequency`, `.duty(index, value)`, `.pwm(index, on, off)`, `.reset()` | Low-level 16-channel PWM generator; everything else builds on this. |
| `Servo` (angular) | `Servo(controller, channel, min_us=1000, max_us=2000, degrees=180, midpoint_us=None, range_us=None, freq_compensation=0, clockwise=True, mid_zero=True)` | `.angle = x` (0..degrees, or roughly -degrees/2..+degrees/2 if `mid_zero=True`), `.stop()`, `.release()` | Sends a calibrated, oscillator-corrected pulse width commanding a target shaft position, with adjustable direction and zero-point convention. `.stop()` and `.release()` make identical zero-duty requests. |
| `Servo` (continuous) | Same class, calibrated around the servo's neutral pulse | `.speed = x` (-99..+99), `.stop()`, `.release()` | Sends a pulse width that the servo interprets as speed + direction. `speed = 0` commands neutral; `.stop()` and `.release()` make identical zero-duty requests. `clockwise`/`mid_zero` do not apply here. |
| `Motor` | `Motor(controller, motor)` (motor 1–4) | `.speed = x` (-99..+99), `.stop()`, `.release()` | PWMs one of two H-bridge logic inputs to set direction and speed. A direct sign reversal inserts `stop()` plus a fixed 50 ms delay; `.stop()` and `.release()` are implemented identically. |
| `Stepper` | `Stepper(controller, stepper, steps_per_rev=512, rpm=6)` (stepper 1–2) | `.step(n, hold=False, rpm=None)`, `.angle(a, hold=False, rpm=None)` | Sequences four H-bridge logic inputs to advance a bipolar stepper by discrete steps; `.angle()` now rounds negative angles correctly. |

**Channel map used by this driver:** servo channels 1–16 map straight through to PCA9685 channels 0–15 (`channel - 1`); motors 1–4 and steppers 1–2 both use PCA9685 channels 8–15 (two channels per motor, four per stepper) — so a `Motor` and a `Stepper` object must never be constructed for overlapping channel ranges on the same board. On the **Quokka board specifically**, servo channels 9–16 physically overlap the motor/stepper H-bridge outputs and shouldn't be used for `Servo` objects, even though the software will accept them; on other PCA9685 boards without a fixed motor/servo split (e.g. a generic 16-channel breakout), all 16 channels are free for `Servo` use. The **Core Electronics PiicoDev Servo Driver** exposes only 4 channels, wires them in *reverse* order relative to this driver's straight-through numbering, and defaults to I2C address `0x44` instead of `0x40` — see Section 2.

---

## Sources

- [NXP PCA9685 datasheet (Adafruit-hosted copy)](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)
- [NXP PCA9685 datasheet (NXP official)](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)
- [Adafruit 16-Channel PWM/Servo Driver — overview](https://learn.adafruit.com/16-channel-pwm-servo-driver/overview)
- [Adafruit 16-Channel PWM/Servo Driver — full guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)
- [Adafruit 16-Channel PWM/Servo Driver — hooking it up (power)](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up)
- [Adafruit — Using Servos with CircuitPython (PDF)](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf)
- [Adafruit Motor Selection Guide — RC Servos](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)
- [Adafruit Motor Selection Guide — Stepper Motors](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)
- [Texas Instruments DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)
- [Texas Instruments DRV8833 product page](https://www.ti.com/product/DRV8833)
- [Pololu DRV8833 Dual Motor Driver Carrier guide](https://www.pololu.com/product-info-merged/2130)
- [Texas Instruments — Current Recirculation and Decay Modes (application note)](https://www.ti.com/lit/an/slva321a/slva321a.pdf)
- [Texas Instruments — Brushed DC Motor 2: The H-Bridge](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6059539558001.mp4/subassets/brushed_dc_motor_2-the_h-bridge.pdf)
- [SparkFun TB6612FNG Hookup Guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)
- [Parallax Continuous Rotation Servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)
- [Oriental Motor — Stepper Motor Basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)
- [MicroPython machine.I2C documentation](https://docs.micropython.org/en/latest/library/machine.I2C.html)
- [va3wam — calibrateServoMotor (PCA9685 oscillator calibration notes)](https://github.com/va3wam/calibrateServoMotor)
- [arduini group discussion on PCA9685 oscillator frequency variance](https://groups.io/g/arduini/topic/oscillator_frequency/81444150)
- [kpower.com — Troubleshooting Common PCA9685 Servo Driver Issues](https://www.kpower.com/insight_servo/7483.html)
- [AustSTEM: What is the Kookaberry](https://auststem.com.au/what-is-the-kookaberry/)
- [AustSTEM — A journey around the Kookaberry](https://learn.auststem.com.au/a-journey-around-the-kookaberry/)
- [Kookaberry releases repository (GitHub)](https://github.com/kookaberry/kooka-releases)
- [Core Electronics PiicoDev Servo Driver (4 Channel) — product page](https://core-electronics.com.au/piicodev-servo-driver.html)
- [Core Electronics PiicoDev Servo Driver — Getting Started Guide](https://core-electronics.com.au/guides/piicodev-servo-driver-pca9685-getting-started-guide/)
- [Core Electronics `PiicoDev_Servo.py` source (GitHub)](https://github.com/CoreElectronics/CE-PiicoDev-PyPI/blob/main/src/PiicoDev_Servo.py)
- Uploaded driver: `pca9685.py` (T. Strasser, AustSTEM Foundation), 28 August 2026 revision
