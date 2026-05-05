# The Goertzel Algorithm — Origins and Usage

## 1. Origins and History

The Goertzel algorithm is a digital signal processing (DSP) technique for efficiently evaluating
individual terms of the Discrete Fourier Transform (DFT). It was first described by
**Dr. Gerald Goertzel** in his 1958 paper published in the *American Mathematical Monthly*:

> Goertzel, G. (1958). *An Algorithm for the Evaluation of Finite Trigonometric Series.*
> American Mathematical Monthly, 65(1), 34–35.

Goertzel framed the problem as evaluating a polynomial on the unit circle of the complex plane —
a technique that converts the DFT computation into a cascaded digital filtering problem solved
using **Horner's rule** (nested polynomial evaluation). This insight predates the
Cooley–Tukey FFT paper by seven years.

### Historical Context

| Year | Event |
|------|-------|
| 1958 | Gerald Goertzel publishes the algorithm |
| 1965 | Cooley & Tukey publish the Fast Fourier Transform (FFT) |
| 1980s–present | Goertzel algorithm gains wide adoption in telecommunications (DTMF detection), audio processing, and embedded systems |

The algorithm achieved its most prominent real-world role in **telephone Dual-Tone Multi-Frequency
(DTMF)** tone detection — the tones produced when pressing digits on a phone keypad. Since only
8 specific frequencies need to be checked, computing the full FFT spectrum would be wasteful;
the Goertzel algorithm processes only the required bins at a fraction of the cost.

---

## 2. Mathematical Foundation

### The DFT as a Polynomial Evaluation

The N-point DFT of a signal `x[n]` is defined as:

```
X[k] = Σ (n=0 to N-1) x[n] · e^(-j·2π·k·n / N)
```

Goertzel recognised that computing a single bin `X[k]` is equivalent to evaluating the
polynomial `X(z) = Σ x[n]·z^n` at `z = e^(j·2π·k/N)`.

### Second-Order IIR Recurrence

The algorithm implements this evaluation as a second-order Infinite Impulse Response (IIR)
filter — often called the **Goertzel filter** — with the recurrence:

```
y[n] = x[n]  +  2·cos(2π·f) · y[n-1]  -  y[n-2]
```

where `y[-1] = y[-2] = 0` (zero initial conditions) and `f = k/N` is the normalised target
frequency (cycles per sample).

After all N samples are consumed, the DFT coefficient is extracted from the final two state
variables `y[N-1]` and `y[N-2]`:

```
Re{X[k]} = 0.5 · 2·cos(2π·f) · y[N-1] - y[N-2]
Im{X[k]} = sin(2π·f) · y[N-1]
|X[k]|²  = y[N-1]² + y[N-2]² - 2·cos(2π·f) · y[N-1] · y[N-2]
```

The key insight is that the inner loop uses only **one real multiplication** per sample
(`w_real * d1`), making it extremely efficient on microcontrollers that lack hardware
floating-point or SIMD units.

### Computational Complexity

| Method | Cost for M bins out of N samples |
|--------|----------------------------------|
| Full FFT then extract | O(N log N) — always computes all bins |
| Direct DFT per bin | O(N) per bin → O(M·N) total |
| Goertzel | O(N) per bin → O(M·N) total, but with a very small constant (1 multiply per sample in the loop) |

The Goertzel algorithm is preferred over FFT when **M ≪ log₂(N)** — i.e., when only a small
number of specific frequencies are needed from a potentially large sample window.

---

## 3. The `goertzel()` Function — Usage Guide

### Function Signature

```python
freqs, results = goertzel(samples, sample_rate, *freqs)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `samples` | list / array of float | Time-domain audio samples. Should be **windowed** (e.g., Hann or Hamming) to reduce spectral leakage. |
| `sample_rate` | int or float | The rate at which `samples` was digitised, in Hz (e.g., `8000`, `44100`). |
| `*freqs` | variable-length tuples | One or more 2-tuples `(f_start, f_end)` in Hz specifying the frequency bands of interest. |

### Return Values

The function returns a **parallel pair of lists**:

| Return | Type | Description |
|--------|------|-------------|
| `freqs` | list of float | The actual centre frequency (Hz) of each DFT bin that was analysed. |
| `results` | list of 3-tuples | `(real, imag, power)` for each analysed bin. |

Each element of `results` is a tuple:
- **`real`** — Real part of the complex DFT coefficient `X[k]`.
- **`imag`** — Imaginary part of `X[k]`.
- **`power`** — Spectral power `|X[k]|²`. For most detection and energy-measurement tasks,
  this is the only value you need.

### Frequency Resolution and Window Size

The frequency resolution (bin width) is:

```
f_step = sample_rate / len(samples)
```

For example:
- 256 samples at 8 000 Hz → **31.25 Hz per bin**
- 1024 samples at 44 100 Hz → **43.07 Hz per bin**

A larger `samples` array improves frequency resolution but increases computation time linearly.

### Usage Examples

#### Example 1 — Detect energy in two telephone DTMF bands

```python
# Assume `audio` is a list of 320 PCM samples captured at 8 kHz.
freqs_out, results = goertzel(audio, 8000, (697, 750), (1200, 1280))

for f, (re, im, pwr) in zip(freqs_out, results):
    print(f"Bin {f:.1f} Hz  →  power = {pwr:.4f}")
```

#### Example 2 — Identify dominant frequency in a single band

```python
freqs_out, results = goertzel(audio, 44100, (400, 500))

powers = [r[2] for r in results]          # extract power values
peak_idx = powers.index(max(powers))      # find the strongest bin
print(f"Dominant frequency: {freqs_out[peak_idx]:.1f} Hz")
```

#### Example 3 — MicroPython on RP2040 / ESP32 with I2S microphone

```python
import array, goertzel

# `buf` is an array.array('h', ...) of 16-bit PCM samples from an I2S mic
samples = [s / 32768.0 for s in buf]     # normalise to [-1.0, 1.0]

freqs_out, results = goertzel(samples, 16000, (300, 3400))  # voice band

for f, (re, im, pwr) in zip(freqs_out, results):
    if pwr > 0.01:   # threshold — tune to your noise floor
        print(f"Activity at {f:.0f} Hz, power {pwr:.5f}")
```

---

## 4. Important Considerations

### Input Windowing

The function docstring explicitly notes that `samples` should be a **windowed** signal.
Applying a window function (e.g., Hann, Hamming) before calling `goertzel()` reduces
**spectral leakage** — the smearing of energy from one bin into its neighbours, which
occurs when the signal is not perfectly periodic within the sample window.

```python
import math
N = len(raw_samples)
# Apply a Hann window before analysis
windowed = [raw_samples[n] * 0.5 * (1 - math.cos(2 * math.pi * n / (N - 1)))
            for n in range(N)]
freqs_out, results = goertzel(windowed, sample_rate, (440, 460))
```

### Frequency Range Validation

The function raises `ValueError` if any requested frequency range extends beyond the
Nyquist limit (`sample_rate / 2`). Always ensure your `(f_start, f_end)` tuples stay
below half the sample rate.

### Power vs Magnitude

The returned `power` value is `|X[k]|²` (magnitude squared). If you need the linear
magnitude (e.g., for display), take the square root: `magnitude = math.sqrt(power)`.

### MicroPython Suitability

The algorithm is particularly well suited to MicroPython on constrained devices because:
- It requires only the built-in `math` module (no NumPy or scipy).
- Memory usage scales with `window_size` (the input buffer), not with FFT twiddle-factor tables.
- The inner loop is pure Python arithmetic — easily replaced with `viper` or `native`
  decorators for a 5–10× speed gain on RP2040 / ESP32.

---

## 5. References

1. Goertzel, G. (1958). *An Algorithm for the Evaluation of Finite Trigonometric Series.*
   American Mathematical Monthly, **65**(1), 34–35.
2. Wikipedia contributors. *Goertzel algorithm.* Wikipedia, The Free Encyclopedia.
   https://en.wikipedia.org/wiki/Goertzel_algorithm
3. Burrus, C. S. *Fast Fourier Transforms* (LibreTexts). §4.4 Goertzel's Algorithm.
   https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Signal_Processing_and_Modeling/Fast_Fourier_Transforms_(Burrus)/04
4. MathWorks. *DFT Estimation with the Goertzel Algorithm.*
   https://www.mathworks.com/help/signal/ug/dft-estimation-with-the-goertzel-algorithm.html
5. Microstar Laboratories. *Detecting a Single Frequency Efficiently.*
   https://www.mstarlabs.com/dsp/goertzel/goertzel.html
