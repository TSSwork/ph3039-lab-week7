
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --------------------------------------------------
# Configuration
# --------------------------------------------------

R = 2400                 # Resistance (ohms)
C = 10e-9                # Capacitance (farads)
THEORETICAL_FC = 1 / (2 * np.pi * R * C)

RESULTS_DIR = Path("results")
CSV_PATTERN = "rc_pulse_response_*.csv"

# --------------------------------------------------
# Load latest CSV
# --------------------------------------------------

csv_files = sorted(
    RESULTS_DIR.glob(CSV_PATTERN),
    key=lambda file: file.stat().st_mtime,
)

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files matching {CSV_PATTERN} found in {RESULTS_DIR}"
    )

csv_file = csv_files[-1]
print(f"Reading: {csv_file}")

df = pd.read_csv(csv_file)

time = df["Time_s"].to_numpy()
vin = df["Vin_V"].to_numpy()
vout = df["Vout_V"].to_numpy()

# --------------------------------------------------
# Validate and prepare data
# --------------------------------------------------

if len(time) < 10:
    raise ValueError("Not enough samples for FFT.")

dt = np.mean(np.diff(time))

if not np.allclose(np.diff(time), dt, rtol=1e-3, atol=1e-12):
    raise ValueError("Time samples are not uniformly spaced.")

sampling_frequency = 1 / dt
print(f"Sampling frequency: {sampling_frequency:.2f} Hz")
print(f"Number of samples: {len(time)}")

# Remove DC components
vin = vin - np.mean(vin)
vout = vout - np.mean(vout)

# Apply a Hann window to reduce spectral leakage
window = np.hanning(len(time))

vin_fft = np.fft.rfft(vin * window)
vout_fft = np.fft.rfft(vout * window)

frequencies = np.fft.rfftfreq(len(time), dt)

# --------------------------------------------------
# Calculate transfer function
# --------------------------------------------------

input_magnitude = np.abs(vin_fft)

# Ignore DC and bins with insufficient input energy
valid = (
    (frequencies > 0)
    & (input_magnitude > 0.01 * np.max(input_magnitude))
)

frequencies = frequencies[valid]

H = vout_fft[valid] / vin_fft[valid]

gain = np.abs(H)
gain_db = 20 * np.log10(np.maximum(gain, 1e-12))
phase = np.angle(H, deg=True)

# --------------------------------------------------
# First-order RC low-pass fitting
# --------------------------------------------------

def rc_magnitude(f, k, fc):
    return k / np.sqrt(1 + (f / fc) ** 2)


def rc_phase(f, fc):
    return -np.degrees(np.arctan(f / fc))


# Fit magnitude using linear gain, not dB
initial_k = float(np.median(gain[:min(3, len(gain))]))
initial_fc = THEORETICAL_FC

try:
    parameters, covariance = curve_fit(
        rc_magnitude,
        frequencies,
        gain,
        p0=[initial_k, initial_fc],
        bounds=([0, 1], [10, 1e7]),
        maxfev=20000,
    )

    fitted_k, fitted_fc = parameters

    fit_frequencies = np.logspace(
        np.log10(frequencies.min()),
        np.log10(frequencies.max()),
        1000,
    )

    fitted_gain = rc_magnitude(
        fit_frequencies, fitted_k, fitted_fc
    )

    fitted_gain_db = 20 * np.log10(fitted_gain)
    fitted_phase = rc_phase(fit_frequencies, fitted_fc)

    fit_success = True

except (RuntimeError, ValueError) as error:
    print(f"Fitting failed: {error}")
    fit_success = False

# --------------------------------------------------
# Plot Bode response
# --------------------------------------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))

# Magnitude
ax1.semilogx(
    frequencies,
    gain_db,
    "o",
    label="FFT measured",
)

if fit_success:
    ax1.semilogx(
        fit_frequencies,
        fitted_gain_db,
        "-",
        label="First-order RC fitted",
    )

ax1.axvline(
    THEORETICAL_FC,
    linestyle="--",
    label=f"Theoretical fc = {THEORETICAL_FC:.1f} Hz",
)

ax1.set_title("RC Low-Pass Filter - Bode Plot")
ax1.set_ylabel("Gain (dB)")
ax1.grid(True, which="both")
ax1.legend()

# Phase
ax2.semilogx(
    frequencies,
    phase,
    "o",
    label="FFT measured",
)

if fit_success:
    ax2.semilogx(
        fit_frequencies,
        fitted_phase,
        "-",
        label="First-order RC fitted",
    )

ax2.axvline(
    THEORETICAL_FC,
    linestyle="--",
    label="Theoretical cutoff",
)

ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Phase (degrees)")
ax2.grid(True, which="both")
ax2.legend()

plt.tight_layout()

plot_path = RESULTS_DIR / "fft_bode_plot.png"
plt.savefig(plot_path, dpi=300)
plt.show()

# --------------------------------------------------
# Save FFT results
# --------------------------------------------------

fft_results = pd.DataFrame({
    "Frequency_Hz": frequencies,
    "Gain": gain,
    "Gain_dB": gain_db,
    "Phase_deg": phase,
})

fft_csv = RESULTS_DIR / "fft_bode_data.csv"
fft_results.to_csv(fft_csv, index=False)

print("\n---------- RESULTS ----------")
print(f"Theoretical cutoff: {THEORETICAL_FC:.2f} Hz")

if fit_success:
    print(f"Fitted passband gain: {fitted_k:.4f}")
    print(f"Fitted cutoff: {fitted_fc:.2f} Hz")
    print(f"Cutoff difference: {abs(fitted_fc - THEORETICAL_FC):.2f} Hz")

print(f"\nBode plot: {plot_path}")
print(f"FFT data:  {fft_csv}")
