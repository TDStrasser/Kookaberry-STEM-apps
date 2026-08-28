# Quokka Motor and Servo Driver Board Examples

These MicroPython example programs run on a **Kookaberry** (a small microcontroller board used in Australian STEM classrooms) and show how to control motors, servos, and stepper motors using two different Quokka driver boards:

- The **Quokka PCA9685 Motor-Servo Driver Board**, which uses a PCA9685 chip to create very precise **PWM** signals (PWM = *pulse-width modulation*, a way of switching a signal on and off very fast so a motor, servo, or stepper can understand a position, speed, or step command).
- The **Quokka DRV8833/L9110 H-Bridge Motor Driver Board**, which uses the Kookaberry's own GPIO pins in PWM mode to drive a simple DC motor without needing the PCA9685 chip.

An **H-bridge** is a small driver circuit that lets a low-power control signal from a microcontroller safely run a motor forwards or backwards at different speeds. Both boards in these examples use an H-bridge internally — the difference is *how* the Kookaberry talks to that H-bridge (I2C and the PCA9685 chip, or direct GPIO pins).

These examples are written for students studying STEM up to Year 12. They are a good introduction to real-world concepts like digital communication buses (I2C), PWM, feedback and timing, and safe handling of powered hardware.

---

## `pca9685_servo_example-5.py` — Positional (angle) servo

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 servo board connected to port **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A standard angular hobby servo, such as an SG90 or FS90, connected to servo channel **1**.
- A suitable external servo power supply, with its ground wire shared with the Kookaberry/PCA9685 board.

A **positional servo** is a small motor that turns to a specific angle and holds that position. It is the kind of motor used to move a robot arm joint, a steering mechanism, or a pointer.

### What the code does

The script connects to the PCA9685 chip over **I2C** — a two-wire communication bus that lets the Kookaberry send commands to other chips — and sets up one servo object on channel 1:

```python
servo = Servo(controller, 1, midpoint_us=1500, range_us=2400,
              degrees=180, freq_compensation=12,
              clockwise=True, mid_zero=True)
```

Because `mid_zero=True`, an angle of `0` means the middle of the servo's travel, so the example can use both negative and positive angles (`-90` to `+90`) to describe a 180-degree range of motion.

The program then:

1. Steps the servo to `0`, then `-45`, then `-90` degrees, pausing 1 second at each position.
2. Returns the servo to `0` degrees.
3. Slowly sweeps the servo from `0` to `90` degrees in 5-degree steps, waiting 40 ms between each step.
4. Calls `servo.release()` so the driver stops sending a control pulse.

### What you should see

The servo horn should move in clear, distinct steps to each commanded angle, then perform a smooth, slow sweep across half its range. Once released, it may no longer actively hold its position.

If the servo buzzes, gets hot, or strains at the end of its travel, stop the program and check the wiring and angle settings before trying again.

### Things to try next

- Change `-45` to `-20` to see a smaller movement.
- Change the sweep step in `range(0, 95, 5)` from `5` to `10` for bigger jumps.
- Increase `sleep_ms(40)` to `100` to slow the sweep down.
- Test a small, safe range such as `range(0, 50, 5)` before trying full-range movements.

---

## `pca9685_continuous_servo_example-3.py` — Continuous-rotation servo

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 servo board connected to port **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A **continuous-rotation servo**, such as an SG90R or FS90R, connected to servo channel **1**.
- A suitable external servo power supply, with its ground wire shared with the Kookaberry/PCA9685 board.

Unlike a normal servo, a **continuous-rotation servo** does not move to a fixed angle. Instead, the control signal tells it how fast to spin and in which direction — similar to a simple motor, but controlled the same way as a positional servo.

### What the code does

The script sets up a continuous servo object on channel 1:

```python
servo = Servo(controller, 1, midpoint_us=1500, range_us=600,
              freq_compensation=12, clockwise=True, mid_zero=True)
```

It defines a helper function, `ramp()`, which gradually changes the servo's speed from a starting value to an ending value in small steps, printing each speed to the REPL console as it goes and pausing between steps.

The main program then uses `ramp()` three times to:

1. Increase the speed smoothly from `0` up to `99` (nearly full speed in one direction).
2. Ramp all the way down through `0` and up to `-99` (nearly full speed in the other direction).
3. Ramp back from `-99` to `0`.

Finally, `servo.stop()` is called to stop the servo turning.

### What you should see

The servo should spin up smoothly, slow to a stop, reverse direction, spin up the other way, then slow back to a stop. The REPL console prints each speed value as the ramp runs, which is useful for understanding how the `speed` value relates to real-world motion.

### Things to try next

- Change `speed_max` from `99` to a smaller value such as `50` to limit the top speed.
- Change `speed_step` to a smaller number for a smoother, slower ramp.
- Change `step_delay` to see how ramp timing affects how the servo accelerates.
- Compare this script with `pca9685_servo_example-5.py` to see how `angle` and `speed` are used differently for the two servo types.

---

## `pca9685_motor_example-4.py` — Bi-directional variable-speed DC motor (PCA9685)

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 motor-servo board connected to port **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A DC motor connected to motor output **1** on the PCA9685 board.
- A suitable external motor power supply, with its ground wire shared with the Kookaberry/PCA9685 board.

The PCA9685 does not power the motor directly. It sends PWM control signals to an onboard H-bridge, and the H-bridge switches the higher-current motor supply on the motor's behalf.

### What the code does

The script sets up one motor object:

```python
motor = Motor(controller, 1)
```

This uses motor output 1, which internally maps to PCA9685 channels 8 and 9 — one channel for each direction the H-bridge can drive the motor.

The program then runs through a list of speeds:

```python
speeds = [0, -25, -50, -75, -99.9, -50, 50, 75, 99.9, 50, 0]
```

The `motor.speed` value is a percentage from `-99.9` to `99.9`, where `0` means stopped, negative values drive the motor one way, and positive values drive it the other way — larger numbers mean faster.

For each speed in the list, the code:

1. Sets `motor.speed`.
2. Works out the H-bridge's actual PWM duty cycle percentages by reading the raw PCA9685 channel data (channels 8 and 9) — a more advanced technique for students curious about what is happening "under the hood".
3. Prints the speed and duty-cycle values to the REPL console.
4. Waits 2 seconds before moving to the next speed.

At the end, `motor.release()` stops the motor and removes drive power from the H-bridge.

### What you should see and hear

The motor should start stopped, run in one direction at increasing then decreasing speed, stop, then repeat in the opposite direction, and stop again. The motor's sound should change with speed, and the REPL console should print matching speed and duty-cycle values.

### Things to try next

- Use a smaller speed list, such as `[-20, -10, 0, 10, 20]`, to see gentler changes.
- Change `sleep_ms(2000)` to `sleep_ms(1000)` to move through the list faster.
- Remove the highest speed values while first testing an unfamiliar motor.
- Add extra `0` entries between direction changes to let the motor fully stop before reversing.

---

## `pca9685_stepper_example-6.py` — Stepper motor

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 motor-servo board connected to port **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A stepper motor wired to motor outputs **3 and 4** (PCA9685 channels 13–16).
- A suitable external motor power supply, with its ground wire shared with the Kookaberry/PCA9685 board.

A **stepper motor** moves in small, fixed increments called *steps* rather than spinning freely. The driver energises its internal coils in a set sequence, and each step turns the shaft by a precise, repeatable amount. This makes steppers ideal for jobs that need accurate, known movement, like turning a dial or positioning a small platform.

### What the code does

The script creates a stepper object:

```python
stepper = Stepper(controller, 2)
```

This uses stepper output 2, and by default assumes a motor with `512` steps per full revolution. A comment in the code shows how to use a `200`-step motor instead:

```python
stepper = Stepper(controller, 2, steps_per_rev=200)
```

The program then:

1. Records the start time using `time.ticks_ms()`.
2. Calls `stepper.angle(360, rpm=6)` to turn the motor through one full revolution (360 degrees) at 6 revolutions per minute.
3. Records the end time and prints the elapsed time in seconds.

### What you should see and hear

The stepper should turn through exactly one full revolution, often moving in small, visible jumps rather than a perfectly smooth spin, with a soft clicking or buzzing sound as the coils switch. The REPL console prints how long the movement took.

If the motor only vibrates, moves unevenly, or stalls, check the coil wiring, the power supply, and whether `steps_per_rev` matches your actual motor.

### Things to try next

- Change `360` to `180` for a half revolution.
- Change `360` to `-360` to reverse the direction.
- Try a slower speed, such as `rpm=3`.
- If using a 200-step motor, update the setup line to `Stepper(controller, 2, steps_per_rev=200)`.

---

## `drv8833_motor_example-2.py` — DC motor via Kookaberry GPIO PWM (DRV8833/L9110)

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka DRV8833 or L9110 H-Bridge motor driver board connected to port **P3**.
- The `drv8833.mpy` driver file in `/lib`.
- A small DC motor connected to the driver board's motor output.
- A suitable external motor power supply, with its ground wire shared with the Kookaberry/driver board.

This example is different from the others because it does **not** use the PCA9685 chip or I2C at all. Instead, the Kookaberry's own GPIO pins are set into **PWM mode** and connected straight to the DRV8833 or L9110 H-bridge chip, which then drives the motor. This is a simpler, lower-cost way to control one or two small motors when the extra precision of the PCA9685 is not needed.

### What the code does

The script creates a motor object directly from two Kookaberry GPIO pins:

```python
motor = DRV8833('P3A', 'P3B')
```

These two pins carry PWM signals straight to the H-bridge driver chip, one pin for each direction.

The program then runs through a longer list of speeds, from `0` down to `-99` and back, then up to `99` and back to `0`:

```python
speeds = [0, -10, -20, ..., -99, -50, 10, 20, ..., 99, 50, 0]
```

For each speed, the code:

1. Sets `motor.speed`.
2. Prints both the commanded speed and the value read back from `motor.speed`, letting students compare the command against what the driver actually reports.
3. Waits 1.5 seconds before moving to the next speed.

At the end, `motor.stop()` stops the motor.

### What you should see and hear

The motor should ramp up and down smoothly in one direction, pause near zero, then ramp up and down in the other direction, changing sound with speed. The REPL console shows the commanded and read-back speed values side by side.

### Things to try next

- Compare this script with `pca9685_motor_example-4.py` — both control a bidirectional DC motor, but one uses I2C and the PCA9685 chip while this one drives GPIO pins directly.
- Shorten the speed list to see the motor react to fewer, larger speed jumps.
- Change `sleep_ms(1500)` to a smaller value to move through speeds more quickly.
- Investigate why the "read back" speed might sometimes differ slightly from the commanded speed.

---

## Safety notes

Motors and servos can draw far more current than a microcontroller pin can safely supply on its own. Always use a suitable external power supply for motors and servos, with its ground connected to the Kookaberry/driver board ground.

Never power motors or servos from the Kookaberry's logic rail. Sudden current spikes can reset the board or cause unreliable behaviour.

Keep fingers, hair, loose wires, and clothing away from moving parts — a program can start a motor or servo moving as soon as it runs.

Do not force a servo horn by hand while it is holding position, and do not command a servo past its safe mechanical range. Buzzing, heating, or straining are signs to stop and check your code or calibration.

Do not stall a DC motor or stepper motor for long periods. A stalled motor can draw high current and overheat the driver, motor, or wiring.

Start every new setup gently: test one device at a time, use small movements or low speeds first, and only increase values once the hardware behaves as expected.

---

## Learn more

For a deeper explanation of how the `PCA9685`, `Servo`, `Motor`, and `Stepper` classes work, including PWM timing, channel mapping, servo calibration, H-bridge behaviour, stepper sequencing, and power-safety rules, read the detailed guide:

- [`pca9685_motors_servos_guide.md`](https://github.com/TDStrasser/Kookaberry-STEM-apps/blob/master/lib/pca9685_motors_servos_guide.md)
