# Driving Servos, DC Motors, and Steppers with the Kookaberry PCA9685 Module

*A student guide to the embedded principles behind `pca9685.py`*

This guide explains **why** the `PCA9685`, `Servo`, `Motor`, and `Stepper` classes in `pca9685.py` work the way they do, so that you can use them confidently — and eventually write similar drivers yourself. It assumes no prior embedded electronics knowledge beyond basic MicroPython (variables, classes, loops).

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

### Setting the frequency

All 16 channels share **one** PWM frequency — you cannot run some channels at 50 Hz and others at 1 kHz simultaneously ([NXP PCA9685 datasheet](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)). This matters because servos expect roughly 50 Hz, while some other PWM applications (e.g. dimming an LED) work fine at much higher frequencies — but on this board, everything you connect must tolerate the frequency you chose in `PCA9685(i2c, freq=50)`.

The chip has an internal ~25 MHz oscillator. To get an arbitrary output frequency, the driver calculates a **prescale** value and writes it to a register:

```python
prescale = int(25000000.0 / 4096.0 / f + 0.5)
```

This is a standard technique: a fast internal clock is divided down by an integer prescaler to produce the frequency you actually want. You don't need to memorise the formula, but understanding *that* dividing a fixed oscillator produces your target frequency is a transferable embedded-systems concept.

### The `PCA9685.__init__` and I2C addressing

```python
def __init__(self, i2c, address=_I2C_ADDRESS, freq=50):
```

The PCA9685 defaults to I2C address `0x40` ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)). Before using the driver, it's good practice to run `i2c.scan()` in a fresh MicroPython session to confirm the Kookaberry can actually see the chip on the bus — if `0x40` (64 decimal) doesn't appear, check your wiring before debugging your code ([MicroPython I2C docs](https://docs.micropython.org/en/latest/library/machine.I2C.html)).

**Usage pattern for all classes below** — you always build a small object hierarchy:

```python
from machine import SoftI2C, Pin
i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PCA9685(i2c, address=0x40)   # one controller per board
servo = Servo(controller, 1)              # channel 1
motor = Motor(controller, 1)              # motor output 1
stepper = Stepper(controller, 1)          # stepper output 1
```

Every `Servo`, `Motor`, and `Stepper` object *wraps* the shared `controller` and simply calls `controller.duty(channel, value)` behind the scenes. This is a good example of **object-oriented hardware abstraction**: the low-level chip details (registers, I2C addresses, prescalers) are hidden inside `PCA9685`, so the classes built on top of it can expose a much simpler interface (`.angle`, `.speed`, `.step()`).

---

## 2. Angular (positional) servos

### The physical device

A hobby servo is a small package containing a DC motor, a gear train, and — critically — an internal potentiometer that senses shaft position and a tiny built-in control circuit (its own miniature H-bridge) that drives the motor toward whatever angle you command ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)). You are not switching the servo's internal motor directly — you are sending it a *position command* and letting its internal electronics do the driving.

### Why pulse *width*, not duty cycle percentage, is what matters

This is the single most important concept for angular servos: **the servo cares about the absolute time (in microseconds) that the pulse stays high, not the percentage of the cycle it occupies.** A pulse of about 1000 µs commands one extreme of travel, about 1500 µs commands the centre, and about 2000 µs commands the other extreme — repeated roughly every 20 ms (50 Hz) ([Adafruit CircuitPython servo guide](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf), [Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)). The driver defaults to a slightly wider `min_us=600, max_us=2400` because many modern servos can safely use more of their mechanical travel — but the underlying principle is identical.

### Converting microseconds to a PCA9685 duty count

Because the PCA9685 only understands 12-bit counts (0–4095) over the chosen period, the driver must convert your desired pulse width in microseconds into a count:

```python
def _us2duty(self, value):
    return int(4095 * value / self.period + 0.5)
```

At 50 Hz, `self.period` is 20,000 µs, so:

| Pulse width | Approx. duty count (0–4095) |
|---|---:|
| 600 µs | ~123 |
| 1000 µs | ~205 |
| 1500 µs | ~307 |
| 2000 µs | ~410 |
| 2400 µs | ~491 |

You never need to do this arithmetic yourself — it happens inside `Servo.__init__` and `_us2duty()` — but understanding it explains *why* the class asks for `min_us`/`max_us` rather than raw duty numbers.

### Using the `angle` property

```python
servo = Servo(controller, 1, min_us=600, max_us=2400, degrees=180)
servo.angle = 90      # move to the centre of travel
```

The setter linearly maps your requested angle (0 to `degrees`) onto the calibrated duty range and writes it straight to the PCA9685 channel:

```python
duty = self.min_duty + (self.max_duty - self.min_duty) * x / self._degrees
```

This is a **linear remap** — the same pattern used throughout the file's helper `remap()` function. Learning to read this one line means you can read almost every other property setter in the module.

### Calibration: `midpoint_us` + `range_us` as an alternative

```python
servo = Servo(controller, 8, midpoint_us=1600, range_us=2600, degrees=180)
```

Not every servo's centre is exactly 1500 µs, and not every servo accepts exactly 500–2500 µs. Real servos vary by manufacturer, and pushing a pulse beyond a servo's mechanical limit causes it to buzz, draw excess current, heat up, and can strip its gears ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)). Calibration means experimentally finding the safe `min_us`/`max_us` (or `midpoint_us`/`range_us`) for *your* specific servo before trusting it with a full 0–180° sweep. Always start a new servo cautiously — command small angle changes first and watch/listen for strain.

### Power supply — why it matters here

Servos draw large, spiky currents, especially several hundred milliamps for small servos and over 1 A for high-torque servos under load ([Adafruit PCA9685 hookup guide](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up)). Never power servos from the Kookaberry's own regulated rail — the current surge can brown out or reset the board. Always give servos their **own stable 5–6 V supply**, and connect that supply's ground to the Kookaberry/PCA9685 ground so all the PWM signal levels share the same 0 V reference ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)).

### `release()`

```python
servo.release()   # sets duty = 0, stops sending a control pulse
```

With no pulse present, most analog servos stop actively holding their position (they go "limp"), which is useful when you want a servo-driven arm to be moved by hand, or simply to reduce noise/current when a servo isn't in active use.

---

## 3. Continuous-rotation servos

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
drive = Servo(controller, 2, min_us=1000, max_us=2000)   # calibrate to your servo's neutral!
drive.speed = 0.0     # stop (as close to neutral pulse as your calibration allows)
drive.speed = 1.0     # full speed one direction
drive.speed = -1.0    # full speed the other direction
```

```python
@speed.setter
def speed(self,x):
    self._speed = x
    duty = int(remap(x, -1, 1, self.min_duty, self.max_duty)+0.5)
    self.controller.duty(self.channel, duty)
```

This reuses the exact same `min_duty`/`max_duty` calibration machinery as the angular servo — the class doesn't need a separate "continuous servo" class because the *only* thing that differs is how you interpret the number you pass in. This is a nice lesson in software design: one well-parameterised class can serve two different physical behaviours.

**Practical trimming tip:** because the manufactured "neutral point" of a continuous servo is rarely exactly 1500 µs, students should expect to experimentally find the pulse width that actually gives zero rotation for their specific unit, then treat that as the servo's true centre when picking `min_us`/`max_us` (or use the physical trim screw many continuous servos have) ([Adafruit CircuitPython servo guide](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf)).

### Typical uses

Continuous servos are popular for small robot wheels and simple drive systems, because the motor, gearbox, and an entire miniature H-bridge speed controller are all bundled into one servo-shaped, servo-cabled unit — no separate motor driver chip required ([Parallax continuous-rotation servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)).

The same power-supply advice from Section 2 applies: use a separate, adequately rated supply, common ground, and start with small speed commands before ramping up.

---

## 4. DC motors through an H-bridge (e.g. the DRV8833)

### Why you need an H-bridge at all

A plain brushed DC motor spins one way when current flows through it in one direction, and the opposite way when current is reversed. A microcontroller pin can only ever be high or low, single-direction — it cannot reverse current by itself, and it usually can't supply enough current to run a motor directly. An **H-bridge** is an arrangement of four electronic switches (in the DRV8833's case, MOSFETs) around the motor, shaped like the letter H, that lets you connect either side of the motor to either supply rail — reversing current direction on command ([SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)).

The DRV8833 packs **two** independent H-bridges into one chip, so it can drive two separate DC motors — or, as you'll see in Section 5, be repurposed to drive one bipolar stepper ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)).

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

The uploaded `Motor` class allocates **two PCA9685 channels per motor** — one that maps to the H-bridge's forward input, one to reverse:

```python
self.channel_fwd = 8 + (motor-1) * 2
self.channel_rev = 9 + (motor-1) * 2
```

and its `speed` setter drives *one* of those channels with a PWM duty cycle proportional to `abs(speed)`, while forcing the other to zero:

```python
duty = int(remap(abs(x), 0, 100, 0, 4095))
if x > 0:
    self.controller.duty(self.channel_rev, 0)
    self.controller.duty(self.channel_fwd, duty, invert=True)
elif x < 0:
    self.controller.duty(self.channel_fwd, 0)
    self.controller.duty(self.channel_rev, duty, invert=True)
else:
    self.release()
```

Rather than holding IN1 permanently high and pulsing IN2 (a very common alternative scheme), this driver **PWMs the active direction input itself** and holds the *other* direction input steady at 0. This still achieves proportional speed control — as duty cycle increases, the motor spends more of each PWM period actually being driven forward or reverse, so its average speed rises, while at 0% duty (or `speed = 0`) the motor coasts/releases ([SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)).

```python
motor = Motor(controller, 1)
motor.speed = 60      # 60% forward
motor.speed = -100    # full reverse
motor.speed = 0       # release() — coast to a stop
```

### Ratings you must respect

The DRV8833 accepts a motor supply from about 2.7 V to 10.8 V, and depending on package, is rated around 1.5 A RMS / 2 A peak per bridge (some carrier boards, e.g. Pololu's, spec closer to 1.2 A continuous per channel) ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833); [Pololu DRV8833 carrier guide](https://www.pololu.com/product-info-merged/2130)). Crucially, a motor's **stall current** (drawn when the shaft can't turn — e.g. jammed or under heavy load) is typically much higher than its free-running current, and this is what actually trips the DRV8833's overcurrent, thermal, or undervoltage protection ([TI DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)). Choose motors and supplies that respect these limits — the built-in protection is a safety net, not a substitute for correct sizing.

### Motor power vs. logic power

Like servos, DC motors need a **separate, adequately rated motor supply** (VM) distinct from the Kookaberry/PCA9685 logic supply, with grounds tied together so the IN1/IN2 logic levels are referenced correctly ([SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)). Motors are **inductive loads** — when current through them is switched, they resist the change and can generate damaging voltage spikes; H-bridge driver ICs like the DRV8833 include internal circuitry to manage this (often described in terms of "fast decay/coast" vs "slow decay/brake" behaviour), which is part of why you should always drive a motor through a proper H-bridge chip rather than switching it with a bare transistor ([TI application note on current recirculation](https://www.ti.com/lit/an/slva321a/slva321a.pdf?ts=1783147782112)).

---

## 5. Stepper motors

### Why steppers are different from both servos and plain DC motors

A stepper motor doesn't spin continuously in response to a single voltage — it rotates in fixed, discrete increments ("steps") as you energise its coils in a particular sequence, one step at a time ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)). A typical stepper might move 1.8° per full step, meaning 200 steps make one full revolution, and — importantly — the position error from one step does not accumulate under normal operation ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). This is what makes steppers so useful for **open-loop positioning**: your program can simply *count* the steps it has commanded and trust that the motor shaft is where it should be, without needing an angle sensor or encoder to confirm it — provided the motor never misses a step.

### Bipolar steppers and why they need two H-bridges

A bipolar stepper has two independent windings ("coils"), and current must be driven through *each* winding in either direction to produce continuous rotation — exactly the same "reverse current to reverse behaviour" problem as a DC motor, just applied to two coils instead of one. That's why a bipolar stepper needs **two H-bridges**: one per winding ([TI DRV8833 product page](https://www.ti.com/product/DRV8833)). This is precisely why the same DRV8833 chip that drives two independent DC motors can, alternatively, be wired to drive one bipolar stepper — it already contains two H-bridges.

### Step sequencing: what "stepping" really means electrically

Full-step drive energises coils in a repeating four-phase sequence, and each transition to the next phase combination is what makes the rotor advance by one step ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). Half-stepping interleaves additional intermediate combinations for finer resolution, and microstepping goes further still, proportioning the current between adjacent phases to produce smoother, smaller effective steps — but microstepping requires actual analog current control in the driver, not just on/off switching ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)).

The uploaded `Stepper` class implements a straightforward **full-step-style** sequence using four PCA9685 channels (mapped to the two H-bridges' four logic inputs):

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
def calculate_pulse(rpm, steps_per_rev, freq):
    pulse_length = int(60000 / rpm / steps_per_rev + 0.5)   # ms per step
    if pulse_length < int(1000 / freq + 0.5):               # can't be faster than one PWM period
        raise Exception("Stepper Motor RPM too high %d" % rpm)
    return pulse_length
```

This converts your desired rotational speed (revolutions per minute) into "how many milliseconds to wait between each step," given how many steps make up one revolution. The built-in sanity check refuses speeds that would require stepping faster than the PCA9685's own PWM period allows — a good example of validating a physical constraint in software before it causes silent, confusing failures.

### Using the class

```python
stepper = Stepper(controller, 1, steps_per_rev=512, rpm=6)
stepper.step(200)          # move 200 steps forward, then release the coils
stepper.step(-50, hold=True)  # move 50 steps backward and keep holding torque afterward
stepper.angle(90, rpm=10)   # rotate 90° at 10 RPM
```

`angle()` is a thin convenience wrapper that just converts a desired angle into a step count using `step_angle = 360 / steps_per_rev`, then calls `step()` — another good example of building a friendlier, physically-meaningful method on top of a more primitive one.

### Torque, speed, and why steppers are used open-loop

Winding inductance limits how fast current can rise in a coil each time it's energised; since torque is roughly proportional to current, driving steps faster than the current has time to build reduces available torque — this is why steppers typically have strong low-speed/holding torque but lose torque at high step rates ([Oriental Motor stepper basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)). Because your program can simply count commanded steps to know the shaft position (no feedback sensor needed), steppers are widely used for open-loop positioning in things like 3D printers and camera rigs — but this trust breaks down if the motor is overloaded, accelerated too abruptly, or driven faster than it can keep up with, causing **missed steps** and a permanently wrong position estimate until the system is re-homed ([Adafruit motor selection guide](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)). Projects that must know an absolute starting position, or must detect missed steps, typically add a limit switch, home switch, or encoder.

---

## 6. Wiring and power safety — the rules that apply to everything above

1. **Separate logic power from motor/servo power.** The Kookaberry/PCA9685 logic side should be powered from the board's own logic supply; servo V+ and motor VM/VIN should come from a separate, adequately rated external supply ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all); [SparkFun TB6612FNG hookup guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)).
2. **Always tie the grounds together.** I2C, PWM, and H-bridge logic signals are all measured relative to ground — if the logic and power-supply grounds aren't common, "high" and "low" become meaningless and behaviour becomes erratic ([Adafruit PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)).
3. **Size your supply for the worst case, not the average case.** Several servos moving simultaneously, or a motor stalling under load, draws far more current than gentle, unloaded operation — undersized supplies cause brownouts, resets, or driver shutdown ([Adafruit PCA9685 hookup guide](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up); [Pololu DRV8833 carrier guide](https://www.pololu.com/product-info-merged/2130)).
4. **Never power servos or motors from the Kookaberry's own 3.3 V/5 V logic rail.** Current spikes from actuators can corrupt or reset the whole board.
5. **Test incrementally.** Confirm `i2c.scan()` sees the PCA9685, then confirm one channel's duty cycle changes something measurable, then connect one unloaded actuator, and only then move to multiple actuators or full load ([MicroPython I2C docs](https://docs.micropython.org/en/latest/library/machine.I2C.html)).
6. **Watch and listen.** Buzzing, unexpected heat in a driver chip, motor, or wire, or a servo that won't settle are all signs to stop and re-check calibration or wiring before continuing.
7. **Mind moving parts.** Gears, wheels, and linkages can pinch fingers or hair, especially when a program unexpectedly starts a movement — keep hands and loose items clear while testing new code.

---

## 7. Quick reference — classes and methods

| Class | Construct with | Key methods/properties | What they physically do |
|---|---|---|---|
| `PCA9685` | `PCA9685(i2c, address=0x40, freq=50)` | `.frequency`, `.duty(index, value)`, `.pwm(index, on, off)`, `.reset()` | Low-level 16-channel PWM generator; everything else builds on this. |
| `Servo` (angular) | `Servo(controller, channel, min_us=, max_us=, degrees=180)` | `.angle = x` (0..degrees), `.release()` | Sends a calibrated pulse width commanding a target shaft position. |
| `Servo` (continuous) | Same class, calibrated around the servo's neutral pulse | `.speed = x` (-1..+1), `.release()` | Sends a pulse width that the servo interprets as speed + direction, not position. |
| `Motor` | `Motor(controller, motor)` (motor 1–4) | `.speed = x` (-100..+100), `.release()` | PWMs one of two H-bridge logic inputs to set direction and speed of a DC motor. |
| `Stepper` | `Stepper(controller, stepper, steps_per_rev=512, rpm=6)` (stepper 1–2) | `.step(n, hold=False, rpm=None)`, `.angle(a, hold=False, rpm=None)` | Sequences four H-bridge logic inputs to advance a bipolar stepper by discrete steps. |

**Channel map used by this driver:** servo channels 1–8 map to PCA9685 channels 0–7; motors 1–4 and steppers 1–2 both use PCA9685 channels 8–15 (two channels per motor, four per stepper) — so a `Motor` and a `Stepper` object must never be constructed for overlapping channel ranges on the same board.

---

## Sources

- [NXP PCA9685 datasheet](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf)
- [Adafruit 16-Channel PWM/Servo Driver — overview](https://learn.adafruit.com/16-channel-pwm-servo-driver/overview)
- [Adafruit 16-Channel PWM/Servo Driver — full guide](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)
- [Adafruit 16-Channel PWM/Servo Driver — hooking it up (power)](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up)
- [Adafruit — Using Servos with CircuitPython (PDF)](https://cdn-learn.adafruit.com/downloads/pdf/using-servos-with-circuitpython.pdf)
- [Adafruit Motor Selection Guide — RC Servos](https://learn.adafruit.com/adafruit-motor-selection-guide/rc-servos)
- [Adafruit Motor Selection Guide — Stepper Motors](https://learn.adafruit.com/adafruit-motor-selection-guide/stepper-motors)
- [Texas Instruments DRV8833 datasheet](https://www.ti.com/lit/gpn/DRV8833)
- [Texas Instruments DRV8833 product page](https://www.ti.com/product/DRV8833)
- [Pololu DRV8833 Dual Motor Driver Carrier guide](https://www.pololu.com/product-info-merged/2130)
- [Texas Instruments — Understanding Motor Driver Current Ratings / recirculation (application note)](https://www.ti.com/lit/an/slva321a/slva321a.pdf?ts=1783147782112)
- [SparkFun TB6612FNG Hookup Guide](https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide/all)
- [Parallax Continuous Rotation Servo guide](https://learn.parallax.com/kickstarts/parallax-continuous-rotation-servo/)
- [Oriental Motor — Stepper Motor Basics](https://www.orientalmotor.com/stepper-motors/technology/stepper-motor-basics.html)
- [MicroPython machine.I2C documentation](https://docs.micropython.org/en/latest/library/machine.I2C.html)
- [AustSTEM — What is the Kookaberry](https://auststem.com.au/what-is-the-kookaberry/)
- [AustSTEM — A journey around the Kookaberry](https://learn.auststem.com.au/a-journey-around-the-kookaberry/)
- [Kookaberry releases repository (GitHub)](https://github.com/kookaberry/kooka-releases)
- Uploaded driver: `pca9685.py` (T. Strasser, AustSTEM Foundation)
