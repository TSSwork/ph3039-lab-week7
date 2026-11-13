
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from instruments import KeysightInstruments
from analysis import calculate_bode, plot_bode


# --------------------------------------------------
# EXPERIMENT CONFIGURATION
# --------------------------------------------------

START_FREQUENCY = 100       # Hz
STOP_FREQUENCY = 10_000     # Hz

frequencies = np.array([
    100, 200, 300, 400, 500, 600, 700, 800, 900,
    1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
    10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000,
    100000
], dtype=float)

NUMBER_OF_POINTS = len(frequencies)

AMPLITUDE_VPP = 1.0
OFFSET_V = 0.0

DWELL_TIME = 5.0            # Seconds per frequency

# Scope channels:
# CH1 = Vout
# CH2 = Vin

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = RESULTS_DIR / "bode_measurements.csv"


# --------------------------------------------------
# MAIN EXPERIMENT
# --------------------------------------------------

instruments = KeysightInstruments()
results = []

print("=" * 55)
print("  2ND-ORDER CHEBYSHEV LOW-PASS FILTER")
print("  LOGARITHMIC SINE-WAVE FREQUENCY SWEEP")
print("=" * 55)

print(f"Start frequency : {START_FREQUENCY} Hz")
print(f"Stop frequency  : {STOP_FREQUENCY} Hz")
print(f"Number of points: {NUMBER_OF_POINTS}")
print(f"Amplitude       : {AMPLITUDE_VPP} Vpp")
print(f"Dwell per point : {DWELL_TIME} seconds")
print(f"Estimated dwell : {NUMBER_OF_POINTS * DWELL_TIME / 60:.2f} minutes")
print(f"CSV output      : {CSV_PATH}")

try:

    # Connect instruments
    instruments.connect()

    # Configure oscilloscope
    instruments.configure_scope()

    # Allow enough time for the oscilloscope to respond
    instruments.scope.timeout = 30000

    print("\nStarting frequency sweep...\n")

    for index, frequency in enumerate(frequencies, start=1):

        print("-" * 55)
        print(
            f"[{index:02d}/{NUMBER_OF_POINTS}] "
            f"Frequency: {frequency:.2f} Hz"
        )

        # Configure scope timebase.
        # Ten horizontal divisions at 0.5/f show approximately
        # five cycles of the input waveform.
        time_scale = 0.5 / frequency

        instruments.scope.write(
            f":TIM:SCAL {time_scale}"
        )

        # Configure sine generator
        instruments.configure_generator(
            frequency=frequency,
            amplitude=AMPLITUDE_VPP
        )

        # Let the signal settle for at least five seconds
        print(f"Waiting {DWELL_TIME:.1f} seconds...")
        time.sleep(DWELL_TIME)

        # Acquire a fresh single waveform record
        instruments.scope.write(":SING")
        instruments.scope.query("*OPC?")

        # Read input and output waveforms
        time_axis, vin, vout = instruments.capture()

        # Calculate gain and phase
        measurement = calculate_bode(
            time_axis,
            vin,
            vout,
            frequency
        )

        results.append(measurement)

        # Save after every completed frequency
        df = pd.DataFrame(results)
        df.to_csv(CSV_PATH, index=False)

        print(
            f"Vin amplitude : {measurement['vin_v']:.5f} V"
        )
        print(
            f"Vout amplitude: {measurement['vout_v']:.5f} V"
        )
        print(
            f"Gain          : {measurement['gain']:.5f}"
        )
        print(
            f"Magnitude     : {measurement['magnitude_db']:.3f} dB"
        )
        print(
            f"Phase         : {measurement['phase_deg']:.2f} degrees"
        )

    print("\n" + "=" * 55)
    print("FREQUENCY SWEEP COMPLETED")
    print("=" * 55)

    # Stop generator output before plotting
    instruments.generator.write("OUTP1 OFF")

    print("\nGenerating Bode plots...")

    plot_bode(
        CSV_PATH,
        RESULTS_DIR
    )

    print("\nResults saved:")
    print(f"CSV: {CSV_PATH}")
    print(f"Magnitude: {RESULTS_DIR / 'bode_magnitude.png'}")
    print(f"Phase: {RESULTS_DIR / 'bode_phase.png'}")

except KeyboardInterrupt:

    print("\nExperiment interrupted by user.")
    print("Completed measurements remain saved in the CSV.")

except Exception as error:

    print("\nEXPERIMENT ERROR:")
    print(repr(error))
    traceback.print_exc()

finally:

    instruments.close()

    print("\nExperiment finished. Instruments disconnected.")
