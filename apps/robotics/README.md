# Quokka PCA9685 Motor-Servo Driver Board Examples

The **Quokka PCA9685 Motor-Servo Driver Board** helps a Kookaberry control motors and servos using the PCA9685 chip. The PCA9685 creates **PWM** signals — short for *pulse-width modulation*, which means switching a signal on and off very quickly so connected devices can understand a position, speed, or step command. These three example scripts show three common ways to make a project move: a positional servo, a bidirectional DC motor, and a stepper motor.

Each example uses the same starting pattern:

```python
from machine import SoftI2C, Pin

i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
controller = PCA9685(i2c, address=0x40, freq=50)
```

This sets up the Quokka board on Kookaberry port **P3** using I2C, a two-wire communication bus that lets the Kookaberry talk to the PCA9685 board.

---

## `pca9685_servo_example-3.py`

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka/PCA9685 servo board connected to **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- An angular/positional hobby servo, such as an SG90 or FS90.
- The servo connected to servo channel **1** on the PCA9685 board.
- A suitable external servo power supply, with ground shared with the Kookaberry/PCA9685 board.

### What the code does

The script imports the `PCA9685` and `Servo` classes, creates the I2C connection on P3, and starts the PCA9685 controller at address `0x40` and frequency `50` Hz.

It then creates one servo object:

```python
servo = Servo(controller, 1,
              midpoint_us=1500,
              range_us=2400,
              degrees=180,
              freq_compensation=12,
              clockwise=True,
              mid_zero=True)
```

This means the servo is controlled through channel 1. The settings tell the driver how to translate an angle into the correct pulse width for the servo. Because `mid_zero=True`, an angle of `0` is treated as the middle of the servo's movement, so the example uses angles such as `-45` and `-90`.

The script then moves the servo through a short set of positions:

1. Move to `0` degrees and wait 1 second.
2. Move to `-45` degrees and wait 1 second.
3. Move to `-90` degrees and wait 1 second.
4. Move back to `0` degrees and wait 1 second.
5. Slowly sweep from `0` to `90` degrees in 5-degree steps, pausing 40 ms between each step.
6. Call `servo.release()` to stop sending the servo control pulse.

### What you should see

The servo horn should move to the centre position, then move part-way toward one side, then farther to that side, then return to centre. After that, it should sweep smoothly from centre toward the other side. At the end, the servo is released, so it may stop actively holding its position.

If the servo buzzes loudly, gets hot, or tries to push past its mechanical limit, stop the program and check the servo setup before continuing.

### Things to try next

- Change `-45` to a smaller value such as `-20` and observe the smaller movement.
- Change the sweep step size in `range(0, 95, 5)` from `5` to `10` to make the sweep jump in larger steps.
- Change `sleep_ms(40)` in the sweep to a larger value such as `100` to make the sweep slower.
- Try a smaller safe range first, such as `range(0, 50, 5)`, before testing larger movements.

---

## `pca9685_motor_example-2.py`

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 motor-servo board connected to **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A DC motor connected to motor output **4**.
- The motor driven through an H-bridge motor driver, such as the DRV8833 used by the Quokka board.
- A suitable external motor power supply, with ground shared with the Kookaberry/PCA9685 board.

An **H-bridge** is a motor-driver circuit that lets a small control signal run a DC motor forwards or backwards. The PCA9685 does not power the motor directly; it sends control signals to the H-bridge, and the H-bridge switches the motor current.

### What the code does

The script imports the `PCA9685` and `Motor` classes, creates the I2C connection on P3, and starts the PCA9685 controller at address `0x40` and frequency `50` Hz.

It then creates one motor object:

```python
motor = Motor(controller, 4)
```

This selects motor output 4. Internally, that motor output uses two PCA9685 channels: one for one direction and one for the other direction.

The script runs through this list of speeds:

```python
[0, -25, -50, -75, -100, -50, 0, 25, 50, 75, 100, 50, 0]
```

The `Motor.speed` value is a percentage from `-100` to `100`:

- `0` means stopped/released.
- Negative values run the motor in one direction.
- Positive values run the motor in the opposite direction.
- Larger numbers mean faster running.

For each speed, the code:

1. Sets `motor.speed` to the next value.
2. Calculates the PWM duty percentages being sent to the two H-bridge inputs by reading PCA9685 channels 14 and 15.
3. Prints the speed and duty values to the REPL console.
4. Lets the motor run for 2 seconds.

At the end, the script calls `motor.release()` to stop the motor and remove drive power from the H-bridge inputs.

### What you should see and hear

The motor should start stopped, then run in one direction at increasing speeds, slow down, stop, then run in the other direction at increasing speeds, slow down, and stop again. You may hear the motor sound change as the speed value changes.

On the REPL console, you should see lines showing the commanded speed and the two PWM duty values used for the H-bridge inputs.

### Things to try next

- Change the speed list to use smaller steps, such as `[-20, -10, 0, 10, 20]`.
- Change `sleep_ms(2000)` to `sleep_ms(1000)` to move through the speed list faster.
- Try removing the full-speed values `-100` and `100` while testing a new motor for the first time.
- Add more `0` values between direction changes so the motor has time to stop before reversing.

---

## `pca9685_stepper_example.py`

### What you need

- A Kookaberry Pico RP2040/RP2350 running the Kookaberry firmware.
- The Quokka PCA9685 motor-servo board connected to **P3**.
- The `pca9685.mpy` driver file in `/lib`.
- A stepper motor wired to motor outputs **3 and 4**.
- A suitable external motor power supply, with ground shared with the Kookaberry/PCA9685 board.

A **stepper motor** moves in small fixed movements called *steps*. Instead of simply spinning when power is applied, it moves one step at a time as the driver energises its coils in the correct sequence. This makes steppers useful when a project needs controlled movement, such as turning a wheel or dial by a known amount.

### What the code does

The script imports the `PCA9685` and `Stepper` classes, creates the I2C connection on P3, and starts the PCA9685 controller at address `0x40` and frequency `50` Hz.

It then creates one stepper object:

```python
stepper = Stepper(controller, 2)
```

This selects stepper output 2, which uses the motor 3 and motor 4 H-bridge outputs. The default setting is a stepper with `512` steps per full revolution. The comment in the code shows how to change this for a 200-step motor:

```python
stepper = Stepper(controller, 2, steps_per_rev=200)
```

The script then measures how long one movement takes:

1. Record the start time using `time.ticks_ms()`.
2. Run `stepper.angle(360, rpm=6)`.
3. Record the end time.
4. Print the elapsed time in seconds.

The command `stepper.angle(360, rpm=6)` asks the motor to turn through 360 degrees, which is one full revolution. The speed is set to 6 rpm, meaning 6 revolutions per minute. With the default 512 steps per revolution and the 50 Hz setup, this should take about ten seconds.

### What you should see and hear

The stepper motor should rotate one full turn. It may move in a series of tiny jumps rather than perfectly smooth motion, and you may hear a regular clicking or buzzing sound as the coils are switched in sequence. The REPL console should print the elapsed time after the movement finishes.

If the motor only vibrates, moves unevenly, or does not complete the turn, stop and check the coil wiring, power supply, and whether the `steps_per_rev` value matches your motor.

### Things to try next

- Change `360` to `180` to turn half a revolution.
- Change `360` to `-360` to try the opposite direction.
- Change `rpm=6` to a lower value such as `rpm=3` for slower movement.
- If your stepper is a 200-step motor, change the setup line to `Stepper(controller, 2, steps_per_rev=200)`.

---

## Safety notes

Motors and servos can draw much more current than a microcontroller pin can safely supply. Use a suitable external power supply for motors and servos, and make sure the external supply ground is connected to the Kookaberry/PCA9685 ground.

Do not power motors or servos from the Kookaberry's logic rail. Current spikes can reset the board or cause unreliable behaviour.

Keep fingers, hair, loose wires, and clothing away from moving parts. A program can start a motor suddenly when you run it.

Do not force a servo horn by hand while it is trying to hold position. Do not command a servo past its safe mechanical range; buzzing, heating, or straining are signs to stop and adjust the code or calibration.

Do not stall a DC motor or stepper motor for long periods. A stalled motor can draw high current and heat the driver, motor, or wiring.

Start every new setup gently: test one device at a time, use small movements or low speeds first, and increase values only after the hardware behaves as expected.

---

## Learn more

For a deeper explanation of how the `PCA9685`, `Servo`, `Motor`, and `Stepper` classes work, read the detailed guide:

- [`pca9685_motors_servos_guide.md`](./pca9685_motors_servos_guide.md)

That guide explains the underlying PWM timing, channel mapping, servo calibration, H-bridge behaviour, stepper sequencing, and power-safety rules in more detail.
