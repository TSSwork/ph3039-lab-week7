
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit


def sine_fit(time, signal, frequency):
    """Fit a sine wave at a known frequency."""

    time = np.asarray(time)
    signal = np.asarray(signal)

    omega = 2 * np.pi * frequency

    def model(t, amplitude, phase, offset):
        return (
            amplitude * np.sin(omega * t + phase)
            + offset
        )

    initial = [
        (np.max(signal) - np.min(signal)) / 2,
        0,
        np.mean(signal)
    ]

    parameters, _ = curve_fit(
        model,
        time,
        signal,
        p0=initial,
        maxfev=10000
    )

    amplitude, phase, offset = parameters

    return abs(amplitude), phase


def calculate_bode(time, vin, vout, frequency):

    input_amplitude, input_phase = sine_fit(
        time, vin, frequency
    )

    output_amplitude, output_phase = sine_fit(
        time, vout, frequency
    )

    gain = output_amplitude / input_amplitude

    magnitude_db = 20 * np.log10(gain)

    phase_deg = np.degrees(
        output_phase - input_phase
    )

    # Wrap phase into -180 to +180 degrees
    phase_deg = (phase_deg + 180) % 360 - 180

    return {
        "frequency_hz": frequency,
        "vin_v": input_amplitude,
        "vout_v": output_amplitude,
        "gain": gain,
        "magnitude_db": magnitude_db,
        "phase_deg": phase_deg
    }


def plot_bode(results):

    df = pd.DataFrame(results)

    df = df.sort_values("frequency_hz")

    # Unwrap phase for a continuous phase curve
    phase = np.unwrap(
        np.radians(df["phase_deg"].to_numpy())
    )

    phase = np.degrees(phase)

    plt.figure(figsize=(10, 5))

    plt.semilogx(
        df["frequency_hz"],
        df["magnitude_db"],
        "o-"
    )

    plt.axhline(-3, linestyle="--", color="gray")
    plt.axvline(6631, linestyle=":", color="red",
                label="Theoretical cutoff: 6.63 kHz")

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("RC Low-pass Filter - Magnitude Response")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()

    plt.savefig("plots/bode_magnitude.png", dpi=300)

    plt.figure(figsize=(10, 5))

    plt.semilogx(
        df["frequency_hz"],
        phase,
        "o-"
    )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (degrees)")
    plt.title("RC Low-pass Filter - Phase Response")
    plt.grid(True, which="both")
    plt.tight_layout()

    plt.savefig("plots/bode_phase.png", dpi=300)

    plt.show()

    return df
