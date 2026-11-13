
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

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

phase_deg[valid] = np.degrees(
    np.unwrap(np.angle(H[valid]))
)

# ==========================================
# THEORETICAL RC RESPONSE
# ==========================================

R = 2400
C = 10e-9

fc = 1 / (2 * np.pi * R * C)

w = 2 * np.pi * frequencies
H_theory = 1 / (1 + 1j * w * R * C)

theory_gain = 20 * np.log10(np.abs(H_theory))
theory_phase = np.degrees(np.angle(H_theory))

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

axes[0].semilogx(
    frequencies[1:],
    theory_gain[1:],
    label="Theoretical RC"
)

axes[0].axvline(
    fc,
    linestyle="--",
    label=f"Cutoff = {fc:.2f} Hz"
)

axes[0].set_title("RC Low-Pass Filter - Magnitude Response")
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

axes[1].semilogx(
    frequencies[1:],
    theory_phase[1:],
    label="Theoretical RC"
)

axes[1].axvline(
    fc,
    linestyle="--",
    label=f"Cutoff = {fc:.2f} Hz"
)

axes[1].set_title("RC Low-Pass Filter - Phase Response")
axes[1].set_xlabel("Frequency (Hz)")
axes[1].set_ylabel("Phase (degrees)")
axes[1].grid(True, which="both")
axes[1].legend()

plt.tight_layout()

plt.savefig("results/bode_from_pulse.png", dpi=300)

plt.show()

print("\nSampling frequency:", sampling_frequency, "Hz")
print("FFT frequency resolution:", sampling_frequency / N, "Hz")
print("Theoretical cutoff:", fc, "Hz")
print("Saved: results/bode_from_pulse.png")
