import os
import time
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from instruments import KeysightInstruments


# =====================================================
# EXPERIMENT CONFIGURATION
# =====================================================

FREQUENCY = 5000          # Hz
AMPLITUDE = 3.0           # Vpp
OFFSET = 0.0              # V


PULSE_WIDTH = 40e-9       # 40 ns
LEADING_EDGE = 10e-9      # 10 ns
TRAILING_EDGE = 10e-9    # 10 ns

RESISTANCE = 2400         # Ohms
CAPACITANCE = 10e-9       # Farads

EXPERIMENT_DURATION = 20  # seconds

# Oscilloscope horizontal scale:
# 20 us/div x 10 divisions = 200 us
# This displays one complete 5 kHz period.
TIME_SCALE = 20e-6

OUTPUT_DIR = "results"


# =====================================================
# THEORETICAL CALCULATIONS
# =====================================================

TAU = RESISTANCE * CAPACITANCE

CUTOFF_FREQUENCY = 1 / (2 * np.pi * TAU)

PERIOD = 1 / FREQUENCY

print("\n========================================")
print("       RC LOW-PASS FILTER EXPERIMENT")
print("========================================")

print(f"Resistance       : {RESISTANCE} Ohms")
print(f"Capacitance      : {CAPACITANCE * 1e9:.2f} nF")
print(f"Time constant    : {TAU * 1e6:.2f} us")
print(f"Theoretical fc   : {CUTOFF_FREQUENCY:.2f} Hz")
print(f"Input frequency  : {FREQUENCY} Hz")
print(f"Input period     : {PERIOD * 1e6:.2f} us")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================
# MAIN EXPERIMENT
# =====================================================

instruments = KeysightInstruments()

try:

    # -------------------------------------------------
    # CONNECT INSTRUMENTS
    # -------------------------------------------------

    instruments.connect()

    # -------------------------------------------------
    # CONFIGURE OSCILLOSCOPE
    # -------------------------------------------------

    instruments.configure_scope()

    scope = instruments.scope

    scope.timeout = 120000

    # Display one complete input period.
    scope.write(f":TIM:SCAL {TIME_SCALE}")

    # Trigger on input channel.
    scope.write(":TRIG:EDGE:SOUR CHAN2")
    scope.write(":TRIG:EDGE:SLOP POS")

    # Use maximum available raw acquisition memory.
    scope.write(":WAV:POIN:MODE RAW")

    print("\nOscilloscope ready.")

    # -------------------------------------------------
    # CONFIGURE PULSE GENERATOR
    # -------------------------------------------------

    instruments.configure_pulse_generator(
        frequency=FREQUENCY,
        amplitude=AMPLITUDE,
        offset=OFFSET,
        pulse_width=PULSE_WIDTH,
        leading_edge=LEADING_EDGE,
        trailing_edge=TRAILING_EDGE,
    )

    # -------------------------------------------------
    # RUN EXPERIMENT FOR 20 SECONDS
    # -------------------------------------------------

    print("\n========================================")
    print("          EXPERIMENT STARTED")
    print("========================================")

    print(f"Acquiring for {EXPERIMENT_DURATION} seconds...")

    scope.write(":RUN")

    start_time = time.monotonic()

    while True:

        elapsed = time.monotonic() - start_time

        if elapsed >= EXPERIMENT_DURATION:
            break

        remaining = EXPERIMENT_DURATION - elapsed

        print(
            f"\rTime remaining: {remaining:5.1f} seconds",
            end="",
            flush=True
        )

        time.sleep(min(0.5, remaining))

    print("\n\nExperiment duration completed.")

    # -------------------------------------------------
    # STOP GENERATOR AND OSCILLOSCOPE
    # -------------------------------------------------

    instruments.generator.write("OUTP1 OFF")

    print("Generator output disabled.")

    scope.write(":STOP")
    scope.query("*OPC?")

    print("Oscilloscope acquisition stopped.")

    # -------------------------------------------------
    # ACQUIRE STORED WAVEFORMS
    # -------------------------------------------------

    print("\nDownloading waveform data...")

    time_axis, input_signal, output_signal = instruments.capture()

    # capture() initiates a single acquisition.
    # Stop the scope again after that acquisition.
    scope.write(":STOP")

    print(f"Samples acquired: {len(time_axis)}")

    # -------------------------------------------------
    # SAVE CSV DATA
    # -------------------------------------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = os.path.join(
        OUTPUT_DIR,
        f"rc_pulse_response_{timestamp}.csv"
    )

    data = np.column_stack(
        (time_axis, input_signal, output_signal)
    )

    np.savetxt(
        csv_path,
        data,
        delimiter=",",
        header="Time_s,Vin_V,Vout_V",
        comments="",
        fmt="%.12e"
    )

    print(f"\nCSV saved: {csv_path}")

    # -------------------------------------------------
    # CALCULATE MEASURED VALUES
    # -------------------------------------------------

    input_vpp = np.ptp(input_signal)
    output_vpp = np.ptp(output_signal)

    output_max = np.max(output_signal)
    output_min = np.min(output_signal)

    print("\n========================================")
    print("          MEASUREMENT RESULTS")
    print("========================================")

    print(f"Input Vpp       : {input_vpp:.6f} V")
    print(f"Output Vpp      : {output_vpp:.6f} V")
    print(f"Output maximum  : {output_max:.6f} V")
    print(f"Output minimum  : {output_min:.6f} V")

    print(f"\nTheoretical cutoff: {CUTOFF_FREQUENCY:.2f} Hz")

    # -------------------------------------------------
    # PLOT INPUT AND OUTPUT WAVEFORMS
    # -------------------------------------------------

    time_us = time_axis * 1e6

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True
    )

    axes[0].plot(
        time_us,
        input_signal,
        linewidth=1
    )

    axes[0].set_title("Input Voltage (Vin) - CH2")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].grid(True)

    axes[1].plot(
        time_us,
        output_signal,
        linewidth=1
    )

    axes[1].set_title("Output Voltage (Vout) - CH1")
    axes[1].set_xlabel("Time (us)")
    axes[1].set_ylabel("Voltage (V)")
    axes[1].grid(True)

    fig.suptitle(
        "RC Low-Pass Filter - Pulse Response\n"
        f"R = {RESISTANCE} Ohms, "
        f"C = {CAPACITANCE * 1e9:.1f} nF, "
        f"fc = {CUTOFF_FREQUENCY:.2f} Hz"
    )

    fig.tight_layout()

    plot_path = os.path.join(
        OUTPUT_DIR,
        f"rc_pulse_response_{timestamp}.png"
    )

    fig.savefig(
        plot_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Plot saved: {plot_path}")

    plt.show()

    print("\nExperiment completed successfully.")

finally:

    instruments.close()

    print("\nExperiment finished. Instruments disconnected.")

