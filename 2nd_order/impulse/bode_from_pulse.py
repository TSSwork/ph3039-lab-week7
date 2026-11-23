
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

from theory import DESIGN, PRACTICAL, response

# ==========================================
# LOAD LATEST EXPERIMENT CSV
# ==========================================

files = glob.glob("results/rc_pulse_response_*.csv")

if not files:
    raise FileNotFoundError("No experiment CSV files found.")

csv_file = max(files, key=os.path.getmtime)

print("Loading:", csv_file)

data = pd.read_csv(csv_file)

t = data["Time_s"].to_numpy()
vin = data["Vin_V"].to_numpy()
vout = data["Vout_V"].to_numpy()

# ==========================================
# REMOVE DC COMPONENT
# ==========================================

vin = vin - np.mean(vin)
vout = vout - np.mean(vout)

# ==========================================
# FFT
# ==========================================

dt = np.mean(np.diff(t))
sampling_frequency = 1 / dt

N = len(t)

Vin_fft = np.fft.rfft(vin)
Vout_fft = np.fft.rfft(vout)

frequencies = np.fft.rfftfreq(N, dt)

# ==========================================
# TRANSFER FUNCTION
# ==========================================

threshold = 0.01 * np.max(np.abs(Vin_fft))

valid = np.abs(Vin_fft) > threshold
valid[0] = False

H = np.zeros_like(Vin_fft, dtype=complex)
H[valid] = Vout_fft[valid] / Vin_fft[valid]

gain_db = np.full(len(frequencies), np.nan)
phase_deg = np.full(len(frequencies), np.nan)

gain_db[valid] = 20 * np.log10(np.abs(H[valid]))

# Wrapped phase: bins are non-contiguous, so unwrapping is meaningless.
phase_deg[valid] = np.degrees(np.angle(H[valid]))

# ==========================================
# THEORETICAL 2nd-ORDER CHEBYSHEV (SALLEN-KEY)
# ==========================================

PASSBAND_EDGE = 3000  # Hz

theory_f = np.logspace(
    np.log10(frequencies[1]), np.log10(frequencies[-1]), 1000
)

curves = [
    (PRACTICAL, "-", *response(theory_f, PRACTICAL)),
    (DESIGN, "--", *response(theory_f, DESIGN)),
]

# ==========================================
# PLOT BODE RESPONSE
# ==========================================

fig, axes = plt.subplots(2, 1, figsize=(11, 8))

axes[0].semilogx(
    frequencies[valid],
    gain_db[valid],
    "o",
    markersize=3,
    label="Measured FFT"
)

for circuit, style, g_db, _ in curves:
    axes[0].semilogx(theory_f, g_db, style, label=circuit["label"])

axes[0].axvline(
    PASSBAND_EDGE, linestyle=":", color="gray", label="3 kHz passband edge"
)

axes[0].set_title("2nd-Order Chebyshev Low-Pass - Magnitude (FFT of pulse)")
axes[0].set_ylabel("Gain (dB)")
axes[0].grid(True, which="both")
axes[0].legend()

axes[1].semilogx(
    frequencies[valid],
    phase_deg[valid],
    "o",
    markersize=3,
    label="Measured FFT"
)

for circuit, style, _, p_deg in curves:
    axes[1].semilogx(theory_f, p_deg, style, label=circuit["label"])

axes[1].axvline(
    PASSBAND_EDGE, linestyle=":", color="gray", label="3 kHz passband edge"
)

axes[1].set_title("2nd-Order Chebyshev Low-Pass - Phase (FFT of pulse)")
axes[1].set_xlabel("Frequency (Hz)")
axes[1].set_ylabel("Phase (degrees)")
axes[1].grid(True, which="both")
axes[1].legend()

plt.tight_layout()

plt.savefig("results/bode_from_pulse.png", dpi=300)

plt.show()

print("\nSampling frequency:", sampling_frequency, "Hz")
print("FFT frequency resolution:", sampling_frequency / N, "Hz")
print("Valid FFT bins:", int(valid.sum()))
print("Saved: results/bode_from_pulse.png")
