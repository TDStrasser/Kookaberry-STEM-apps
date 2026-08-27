## Why DC Motors Need an H-Bridge

A microcontroller GPIO pin can only source a few milliamps at logic voltage (3.3V or 5V) — nowhere near enough current, and only one polarity, to drive a DC motor that may draw hundreds of milliamps to amps at up to 12V. An H-bridge is a circuit of four switches (historically discrete transistors, now integrated as MOSFETs inside a chip like the DRV8833 or L9110) arranged in the shape of the letter "H", with the motor sitting across the middle bar. By turning diagonal pairs of switches on or off, the H-bridge can apply the supply voltage across the motor in either polarity, which is what allows a single low-power control signal to drive a motor forward, in reverse, brake it, or let it coast — something a single GPIO pin could never do alone.

## The Two-Pin Control Interface

Both the DRV8833 and L9110 expose two logic input pins per motor channel (commonly labelled xIN1/xIN2 or IA/IB), and both chips share the same truth table for how those two pins set the H-bridge state:

| xIN1 | xIN2 | Function |
|------|------|----------|
| 0 | 0 | Coast / fast decay (outputs floating) |
| 1 | 0 | Forward (full speed) |
| 0 | 1 | Reverse (full speed) |
| 1 | 1 | Brake / slow decay (outputs shorted together) |

This table explains why the driver module needs exactly two GPIOs per motor — one motor channel maps directly to one half of the DRV8833 chip, and the module's `DRV8833` class takes exactly two pin arguments (`in1`, `in2`) plus a PWM frequency in its constructor to match this hardware layout.

## PWM: Turning Two Digital Pins Into a Speed Control

Full speed forward or reverse is easy — hold one pin high and the other low. Variable speed requires Pulse Width Modulation (PWM): instead of a steady logic level, one pin is switched on and off rapidly, and the fraction of time it spends "on" (the duty cycle) determines the average voltage delivered to the motor, and therefore its effective speed. This is the same principle used across embedded systems for dimming LEDs or controlling servos, but here it is applied specifically per the DRV8833 truth table:

| xIN1 | xIN2 | Function |
|------|------|----------|
| PWM | 0 | Forward PWM, fast decay |
| 1 | PWM | Forward PWM, slow decay |
| 0 | PWM | Reverse PWM, fast decay |
| PWM | 1 | Reverse PWM, slow decay |

The key embedded concept for students to grasp: to PWM in "fast decay" mode, the PWM signal goes on one xIN pin while the other stays at a steady logic 0; to PWM in "slow decay" mode, the PWM signal goes on one pin while the other is held at a steady logic 1. The Kookaberry module's driver deliberately uses the fast decay convention — it always drives the *inactive* direction pin's duty cycle to 0 rather than 100 — because it is simpler to reason about and matches common teaching examples.

## Fast Decay vs Slow Decay: What Actually Happens Inside the Chip

A DC motor's winding is inductive, so when the driving voltage is switched off mid-PWM-cycle, the current does not stop instantly — it must "recirculate" somewhere, and the two decay modes describe two different paths for that current.

- **Fast decay**: the H-bridge output stage goes into a high-impedance (floating) state during the "off" part of the PWM cycle, so recirculation current flows back through internal body diodes and out to the supply — the motor effectively coasts/free-wheels between pulses.
- **Slow decay**: both low-side switches are turned on during the "off" part of the cycle, shorting the motor winding — this actively brakes the motor between pulses, giving more torque and finer low-speed control but generating more heat.

For most beginner robotics projects — buggies, fans, simple actuators — fast decay (the mode this driver implements) is the more forgiving and commonly taught choice, since it behaves more predictably at low duty cycles and is what most example sketches and breakout board tutorials use.

## Why the Chip Supports Both DRV8833 and L9110

The module description notes it works with either the Texas Instruments DRV8833 (2.7–10.8V, up to 1.5A RMS per bridge) or the L9110 (2.5–12V, up to 800mA continuous, 1.5–2A peak per channel), and this is possible because both chips implement the identical two-pin PWM truth table described above, even though they come from different manufacturers and have different voltage/current ratings. This is a useful, generalizable embedded systems lesson: driver software written against a *logical interface* (the truth table) rather than a specific chip's electrical characteristics can be reused across compatible hardware — as long as timing and current limits are respected.

## Reading the DRV8833 Class: A Guided Walkthrough

The attached `drv8833.py` module wraps this hardware behaviour in a Python class so that students interact with speed and direction as simple numbers rather than raw duty cycles. Two independent instances are created to drive the two channels of a single physical chip:

```python
from drv8833 import DRV8833
motor1 = DRV8833(gpio1, gpio2, freq=50)  # first H-bridge half
motor2 = DRV8833(gpio3, gpio4, freq=50)  # second H-bridge half
```

### Constructor (`__init__`)

The constructor takes the two GPIO pin names and an optional PWM frequency (default 50Hz), clamps the frequency into a safe 10Hz–10,000Hz range, and initialises both pins as PWM outputs starting at zero duty cycle — meaning the motor is guaranteed to be stationary the moment the object is created, which is good defensive practice for any actuator driver.

### `frequency` Property

This is implemented as a Python `@property`/`@frequency.setter` pair rather than a plain method, which lets students write natural syntax like `motor1.frequency = 200` to change the PWM rate, or `f = motor1.frequency` to read it back, while the underlying code still clamps the value and applies it to both PWM channels together. Teaching point: properties let a class expose "attribute-like" access while still running validation code behind the scenes — an important pattern for any driver where invalid hardware settings must never be allowed through.

### `speed` Property — the Core of the Driver

The `speed` setter is the most instructive part of the module for students learning embedded motor control. Given a target in the range −99 to +99, it:

1. Clamps the requested value to ±99 and rounds it to the nearest integer, since PWM duty cycle is inherently an integer percentage.
2. Checks whether the motor is being commanded to reverse direction (the sign of the new speed differs from the current stored speed). If so, it first sets both PWM duty cycles to zero and pauses 50ms before applying the new direction.
3. Applies the speed as a duty cycle to only one of the two pins (xIN1 for forward, xIN2 for reverse), holding the other pin's duty cycle at zero — this is precisely the fast-decay PWM row of the truth table above.

Step 2 encodes a real embedded systems safety principle: instantly commanding an H-bridge from full-forward to full-reverse causes a large, near-instantaneous current spike as the motor's inductance and inertia fight the new voltage polarity, which can exceed the chip's current rating and damage it. Inserting a brief zero-duty "dead time" lets the motor's back-EMF and current decay safely before reversing — a technique students should recognise as broadly applicable whenever driving any inductive or inertial load through a bridge circuit.

The `speed` getter works in reverse: it reads back both PWM duty cycles and infers the current signed speed from which pin is non-zero, printing a warning and forcing a stop if both pins somehow show non-zero duty simultaneously (an invalid, unsafe H-bridge state per the truth table).

### `stop()` Method

A convenience method that sets both duty cycles to zero directly — functionally equivalent to setting `speed = 0`, but useful as an explicit, readable "emergency stop" call in student code, and it returns the read-back speed so the caller can confirm the motor actually stopped.

## Practical Guidance for Students

| Concept | Why It Matters | Where It Appears in the Code |
|---|---|---|
| Two-pin H-bridge truth table | Defines every possible motor state from just two logic signals | Constructor pin count; speed setter pin assignment |
| PWM duty cycle | Converts digital on/off switching into an analogue-like average voltage | `speed` property |
| Fast decay vs slow decay | Determines coasting vs braking behaviour between PWM pulses, affecting torque and heat | Held-low pin during PWM in the setter |
| Dead-time before reversal | Protects the chip from current spikes when changing direction | 50ms `sleep_ms` pause in `speed` setter |
| Properties vs methods | Lets validated hardware settings be accessed with plain attribute syntax | `frequency` and `speed` `@property` decorators |
| Multi-chip compatibility | Software written to a logical truth table works across DRV8833 and L9110 hardware | Module header/description |

When experimenting on the Kookaberry, students should start with low PWM frequencies (the 50Hz default is audible and safe for small brushed motors) and use the built-in test script at the bottom of the file — which sweeps speed from 0 through −99 to +99 and back — as a template for verifying that direction reversal, speed scaling, and the stop behaviour all work correctly on real hardware before building it into a larger robotics or automation project.
