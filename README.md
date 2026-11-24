# PH 3039 – Second-Order Chebyshev Filter Experiments

This repository contains the laboratory experiments for investigating the response of a **second-order Chebyshev Type I low-pass filter** using Keysight test equipment and Python-based data acquisition.

Two experiments are maintained independently:

1. **Impulse Response** – observes the filter's time-domain response to a pulse input.
2. **Frequency Response (100 Hz–100 kHz)** – measures the filter's gain and phase at a range of input frequencies and produces Bode plots.

Each experiment has its own Python environment, instrument-control module, analysis scripts, and results directory.

---

## 1. Filter Design

The filter under investigation is a second-order Chebyshev Type I low-pass filter.

| Parameter               |            Value |
| ----------------------- | ---------------: |
| Filter type             |         Low-pass |
| Approximation           | Chebyshev Type I |
| Passband edge frequency |            3 kHz |
| Passband ripple         |               1% |
| Filter order            |                2 |
| Implementation          |           Analog |
| Circuit topology        |       Sallen-Key |

### Component values

The filter that was actually built used resistors measured with a multimeter:

| Component | Calculated value | Built (measured) |
| --------- | ---------------: | ---------------: |
| R1, R2    |         2.818 kΩ | 2.72 kΩ and 2.77 kΩ (placement not recorded) |
| C1, C2    |            10 nF |   10 nF (nominal, not measured) |
| Rf        |         6.893 kΩ |         6.75 kΩ |
| Rg        |            10 kΩ |         **6.78 kΩ** |

Rg was 6.78 kΩ instead of the designed 10 kΩ, so the built gain is K = 1 + 6.75/6.78 ≈ 2.00 (**+6.0 dB**) and Q ≈ 1.0, not the designed K = 1.69 (+4.5 dB), Q = 0.76. This is what the sweep shows (passband ≈ 6.1 dB, peaking ≈ 1.4 dB).

For reference, the design gain is K = 1 + Rf/Rg ≈ 1.69, i.e. about **+4.5 dB passband gain**, not unity. The theoretical transfer function is

H(s) = K·ω0² / (s² + (3 − K)·ω0·s + ω0²),  ω0 = 1/(R·C)

and is implemented in `theory.py` in both experiment folders. Both the design and practical component values are plotted for comparison.

---

## 2. Repository Structure

```text
ph3039-lab-week7/
│
├── 2nd_order/
│   │
│   ├── impulse/
│   │   ├── main.py
│   │   ├── instruments.py
│   │   ├── test_pulse.py
│   │   ├── fft.py
│   │   ├── bode_from_pulse.py
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── results/
│   │
│   └── 100hz-100khz/
│       ├── main.py
│       ├── instruments.py
│       ├── analysis.py
│       ├── pyproject.toml
│       ├── uv.lock
│       └── results/
│
├── README.md
│
└── [Legacy root-level Python files]
```

The root-level Python files are retained from the earlier experiment setup. The two directories under `2nd_order/` contain the separate experiment implementations.

---

## 3. Hardware and Instrumentation

The experiments use the following Keysight instruments:

| Instrument         | Model              | Purpose                                |
| ------------------ | ------------------ | -------------------------------------- |
| Oscilloscope       | Keysight EDUX1052A | Acquires input and output waveforms    |
| Waveform Generator | Keysight EDU33212A | Generates pulse and sinusoidal signals |

### Instrument connections

Both instruments communicate with the computer through USB using VISA.

**Oscilloscope**

```text
USB0::10893::907::CN64390199::0::INSTR
```

**Waveform Generator**

```text
USB0::10893::36097::CN64480028::0::INSTR
```

The Python instrument-control code uses PyVISA to communicate with the equipment.

### Oscilloscope channel configuration

| Channel | Connection    | Signal |
| ------- | ------------- | ------ |
| CH1     | Filter output | Vout   |
| CH2     | Filter input  | Vin    |

Both oscilloscope probes are configured for 10× attenuation (`PROBE_ATTENUATION` in `instruments.py`). **This must match the physical probe switch.** An earlier sweep showed amplitudes about 10–20× too large, which suggests the probes were physically 1× while the software assumed 10×.

---

## 4. Experiment 1 – Impulse Response

**Location:** `2nd_order/impulse/`

This experiment investigates the time-domain response of the second-order filter by applying a pulse signal and observing the resulting output waveform.

### Purpose

- Observe the filter's response to a pulse input.
- Capture the input and output signals using the oscilloscope.
- Save the acquired waveform data as CSV files.
- Plot the time-domain response.
- Investigate the frequency-domain characteristics using FFT-based analysis.

### Main files

| File                 | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `main.py`            | Runs the pulse-response experiment                    |
| `test_pulse.py`      | Tests pulse-generator configuration                   |
| `instruments.py`     | Handles oscilloscope and generator communication      |
| `fft.py`             | Performs FFT-based analysis                           |
| `bode_from_pulse.py` | Generates frequency-response analysis from pulse data |
| `results/`           | Stores acquired data and generated plots              |

### Running the experiment

```bash
cd 2nd_order/impulse
uv sync
uv run python main.py
```

To test the pulse-generator configuration separately:

```bash
uv run python test_pulse.py
```

### Acquisition order

The scope is stopped **before** the generator output is disabled. Disabling the generator first lets the running (AUTO-trigger) scope overwrite its memory with a noise-only record, which previously produced noisy captures. Volts/div and offset are fitted to the live signals (`auto_vertical_scale()`) before acquisition.

The analysis scripts (`fft.py`, `bode_from_pulse.py`) compare the FFT-derived response with the 2nd-order Chebyshev theory.

### Pulse configuration

The pulse generator is configured with the following intended settings:

| Parameter     |          Value |
| ------------- | -------------: |
| Pulse width   |          40 ns |
| Leading edge  |          10 ns |
| Trailing edge |          10 ns |
| Output load   | High impedance |

The pulse settings should be checked against the actual generator output before acquisition.

### Generated results

The `results/` directory stores:

- Captured input and output waveform CSV files.
- Time-domain response plots.
- FFT-based frequency-response data.
- Frequency-response plots derived from pulse measurements.

---

## 5. Experiment 2 – Frequency Response (100 Hz–100 kHz)

**Location:** `2nd_order/100hz-100khz/`

This experiment measures the frequency response of the filter by applying sinusoidal signals at different frequencies and recording the corresponding input and output waveforms.

### Purpose

- Generate sinusoidal input signals.
- Measure the filter response over the frequency range of 100 Hz to 100 kHz.
- Calculate voltage gain and phase difference.
- Generate magnitude and phase Bode plots.
- Compare measured results with the theoretical filter response.

### Frequency sequence

The sweep uses a 1–2–3–...–9 progression within each decade (not a strictly logarithmic spacing, but evenly spread on a log axis):

```text
100, 200, 300, 400, 500, 600, 700, 800, 900,
1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000,
100000 Hz
```

This provides 28 measurement frequencies across the selected range (defined in `main.py`).

### Signal configuration

| Parameter       | Setting                 |
| --------------- | ----------------------- |
| Waveform        | Sine                    |
| Start frequency | 100 Hz                  |
| Stop frequency  | 100 kHz                 |
| Input amplitude | 1 Vpp                   |
| DC offset       | 0 V                     |
| Settling time   | 5 seconds per frequency |
| Generator load  | High impedance          |

The generator holds each frequency for the configured settling period before the oscilloscope measurement is acquired.

### Main files

| File             | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `main.py`        | Controls the frequency sweep and data acquisition         |
| `theory.py`      | Sallen-Key Chebyshev transfer function (design and practical values) |
| `instruments.py` | Handles instrument communication and waveform acquisition |
| `analysis.py`    | Calculates gain, phase, sanity-checks the data, and generates Bode plots |
| `results/`       | Stores CSV measurements and plots                         |

### Running the experiment

```bash
cd 2nd_order/100hz-100khz
uv sync
uv run python main.py
```

### Measurement calculations

The voltage gain is calculated using the measured input and output amplitudes:

\[
A_v(f)=\frac{V_{\mathrm{out}}(f)}{V_{\mathrm{in}}(f)}
\]

The magnitude in decibels is:

\[
G_{\mathrm{dB}}(f)=20\log_{10}(A_v(f))
\]

The phase difference is calculated from the fitted input and output sinusoidal signals:

\[
\phi(f)=\phi_{\mathrm{out}}(f)-\phi_{\mathrm{in}}(f)
\]

### Generated results

The `results/` directory contains:

| File                    | Description                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------- |
| `bode_measurements.csv` | Frequency, input amplitude, output amplitude, gain, magnitude, and phase measurements |
| `bode_magnitude.png`    | Measured and theoretical magnitude response                                           |
| `bode_phase.png`        | Measured and theoretical phase response                                               |

The CSV file is updated during the measurement process so that acquired measurements are saved as the sweep progresses.

---

## 6. Software Requirements

The experiments use Python and the `uv` package manager for dependency management.

### Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- PyVISA
- PyVISA-py
- NumPy
- SciPy
- Matplotlib

The exact dependency versions are maintained separately in each experiment's `pyproject.toml` and `uv.lock` files.

### Install uv on Fedora

If `uv` is not already installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal or reload the shell configuration after installation.

---

## 7. Data Acquisition and Analysis Workflow

Both experiments follow a similar workflow:

```text
          Keysight Waveform Generator
                      |
                      v
                Filter Input
                      |
                      v
             Second-Order Filter
                      |
                      v
                Filter Output
                      |
                      v
             Keysight Oscilloscope
                      |
                      v
              Python / PyVISA
                      |
                      v
              CSV Data Storage
                      |
                      v
              Python Analysis
                      |
                      v
             Plots and Results
```

The impulse experiment focuses on the time-domain response and FFT-based analysis, while the frequency-sweep experiment directly measures the filter response at individual frequencies.

---

## 8. Important Notes

1. Connect the oscilloscope probes to the correct filter input and output nodes before starting an experiment.
2. Confirm that both oscilloscope channels use the correct 10× probe setting.
3. Check the waveform generator's output amplitude and load configuration.
4. Ensure that the filter circuit is powered correctly before applying the input signal.
5. Verify that the oscilloscope displays a reasonable input waveform before running a complete frequency sweep.
6. After a sweep, `analysis.py` prints warnings if the "input" amplitude varies with frequency (CH1/CH2 probably swapped) or is far from Vpp/2 (probe setting or generator load wrong). Do not trust the Bode plot if these appear.
7. Keep the two experiment environments separate. Run `uv sync` inside the relevant experiment directory.
8. Results are saved inside each experiment's own `results/` directory.

---

## 9. Author

**PH 3039 – Electronics Laboratory**

University laboratory experiments involving analog filter design, instrumentation, signal acquisition, and frequency-response analysis.
