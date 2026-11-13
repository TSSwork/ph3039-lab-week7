
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Supplied 2nd-order Chebyshev transfer function:
#
# H(s) = 1.24675439e9 /
#        (s^2 + 46512.2563*s + 1.25934787e9)

NUMERATOR = 1.24675439e9
A1 = 46512.2563
A0 = 1.25934787e9


def sine_fit(time, signal, frequency):
    """Fit a sine wave of known frequency using least squares."""

    time = np.asarray(time, dtype=float)
    signal = np.asarray(signal, dtype=float)

    # Center time to improve numerical stability
    t = time - np.mean(time)
    omega = 2 * np.pi * frequency

    matrix = np.column_stack([
        np.sin(omega * t),
        np.cos(omega * t),
        np.ones_like(t)
    ])

    coefficients, *_ = np.linalg.lstsq(
        matrix, signal, rcond=None
    )

    sin_coefficient, cos_coefficient, offset = coefficients

    amplitude = np.hypot(
        sin_coefficient, cos_coefficient
    )

    phase = np.arctan2(
        cos_coefficient, sin_coefficient
    )

    return amplitude, phase, offset


def calculate_bode(time, vin, vout, frequency):

    input_amplitude, input_phase, input_offset = sine_fit(
        time, vin, frequency
    )

    output_amplitude, output_phase, output_offset = sine_fit(
        time, vout, frequency
    )

    if input_amplitude <= 1e-12:
        raise ValueError(
            f"Input amplitude too small at {frequency} Hz"
        )

    gain = output_amplitude / input_amplitude
    magnitude_db = 20 * np.log10(gain)

    phase_deg = np.degrees(output_phase - input_phase)
    phase_deg = (phase_deg + 180) % 360 - 180

    return {
        "frequency_hz": frequency,
        "vin_v": input_amplitude,
        "vout_v": output_amplitude,
        "vin_offset_v": input_offset,
        "vout_offset_v": output_offset,
        "gain": gain,
        "magnitude_db": magnitude_db,
        "phase_deg": phase_deg
    }


def theoretical_response(frequency):
    """Return magnitude (dB) and phase (degrees)."""

    frequency = np.asarray(frequency, dtype=float)
    omega = 2 * np.pi * frequency

    s = 1j * omega

    H = NUMERATOR / (s**2 + A1 * s + A0)

    magnitude_db = 20 * np.log10(np.abs(H))
    phase_deg = np.degrees(np.unwrap(np.angle(H)))

    return magnitude_db, phase_deg


def plot_bode(csv_path, output_dir):

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df.sort_values("frequency_hz")

    frequencies = df["frequency_hz"].to_numpy()

    measured_phase = np.degrees(
        np.unwrap(np.radians(df["phase_deg"].to_numpy()))
    )

    theoretical_frequencies = np.logspace(
        np.log10(frequencies.min()),
        np.log10(frequencies.max()),
        1000
    )

    theoretical_gain, theoretical_phase = theoretical_response(
        theoretical_frequencies
    )

    # Magnitude plot
    plt.figure(figsize=(10, 6))

    plt.semilogx(
        frequencies,
        df["magnitude_db"],
        "o",
        label="Measured"
    )

    plt.semilogx(
        theoretical_frequencies,
        theoretical_gain,
        "-",
        label="Theoretical Chebyshev"
    )

    plt.axvline(
        3000,
        linestyle="--",
        label="3 kHz passband edge"
    )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("2nd-Order Chebyshev Low-Pass Filter - Magnitude")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_dir / "bode_magnitude.png",
        dpi=300
    )

    # Phase plot
    plt.figure(figsize=(10, 6))

    plt.semilogx(
        frequencies,
        measured_phase,
        "o",
        label="Measured"
    )

    plt.semilogx(
        theoretical_frequencies,
        theoretical_phase,
        "-",
        label="Theoretical Chebyshev"
    )

    plt.axvline(
        3000,
        linestyle="--",
        label="3 kHz passband edge"
    )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (degrees)")
    plt.title("2nd-Order Chebyshev Low-Pass Filter - Phase")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_dir / "bode_phase.png",
        dpi=300
    )

    plt.show()

    return df
