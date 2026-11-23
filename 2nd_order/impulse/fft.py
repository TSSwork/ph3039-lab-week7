
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from theory import DESIGN, PRACTICAL, response

# --------------------------------------------------
# Configuration
# --------------------------------------------------

PASSBAND_EDGE = 3000     # Hz (Chebyshev ripple bandwidth)

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
# Theoretical 2nd-order Chebyshev (Sallen-Key) response
# --------------------------------------------------

theory_frequencies = np.logspace(
    np.log10(frequencies.min()),
    np.log10(frequencies.max()),
    1000,
)

curves = [
    (PRACTICAL, "-", *response(theory_frequencies, PRACTICAL)),
    (DESIGN, "--", *response(theory_frequencies, DESIGN)),
]

# Wrapped phase of the practical circuit at the measured bins
practical_gain_db, _ = response(frequencies, PRACTICAL)
practical_phase = np.degrees(
    np.angle(np.exp(1j * np.radians(response(frequencies, PRACTICAL)[1])))
)
gain_error_db = gain_db - practical_gain_db

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

for circuit, style, g_db, _ in curves:
    ax1.semilogx(theory_frequencies, g_db, style, label=circuit["label"])

ax1.set_title("2nd-Order Chebyshev Low-Pass Filter - Bode Plot (FFT of pulse)")
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

for circuit, style, _, p_deg in curves:
    ax2.semilogx(theory_frequencies, p_deg, style, label=circuit["label"])

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
print(f"Valid FFT bins: {len(frequencies)}")
print(f"Mean gain error vs implemented theory: {np.mean(gain_error_db):.2f} dB")
print(f"RMS gain error vs implemented theory : "
      f"{np.sqrt(np.mean(gain_error_db**2)):.2f} dB")

if len(frequencies) < 5:
    print("WARNING: very few usable bins - the captured input has little "
          "pulse energy (noise-only capture or wrong trigger/scale).")

print(f"\nBode plot: {plot_path}")
print(f"FFT data:  {fft_csv}")
