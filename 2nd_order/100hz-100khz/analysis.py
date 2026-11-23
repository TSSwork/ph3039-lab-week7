
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from theory import DESIGN, PRACTICAL, response


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


def sanity_check(results, expected_vin_amplitude):
    """Print warnings for the wiring/probe faults seen in earlier sweeps.

    results: list of dicts from calculate_bode (in sweep order).
    expected_vin_amplitude: generator amplitude in volts (Vpp / 2).
    Returns the list of warning strings.
    """
    warnings = []
    vin = np.array([r["vin_v"] for r in results])

    # The input is the generator, so it should be flat and near Vpp/2.
    if len(vin) >= 2 and vin.min() < 0.5 * vin.max():
        warnings.append(
            "Vin amplitude varies strongly with frequency "
            f"({vin.min():.3f}-{vin.max():.3f} V). The 'input' channel "
            "looks like the filter OUTPUT: CH1/CH2 are probably swapped."
        )

    ratio = np.median(vin) / expected_vin_amplitude
    if not 0.7 < ratio < 1.3:
        warnings.append(
            f"Median Vin amplitude is {np.median(vin):.3f} V but "
            f"{expected_vin_amplitude:.3f} V was expected (x{ratio:.1f}). "
            "Check the probe 1x/10x switch against PROBE_ATTENUATION in "
            "instruments.py, and the generator load setting."
        )

    for w in warnings:
        print("\nWARNING:", w)
    return warnings


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

    curves = [
        (PRACTICAL, "-", *response(theoretical_frequencies, PRACTICAL)),
        (DESIGN, "--", *response(theoretical_frequencies, DESIGN)),
    ]

    # Magnitude plot
    plt.figure(figsize=(10, 6))

    plt.semilogx(
        frequencies,
        df["magnitude_db"],
        "o",
        label="Measured"
    )

    for circuit, style, gain_db, _ in curves:
        plt.semilogx(
            theoretical_frequencies, gain_db, style,
            label=circuit["label"]
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

    for circuit, style, _, phase_deg in curves:
        plt.semilogx(
            theoretical_frequencies, phase_deg, style,
            label=circuit["label"]
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
