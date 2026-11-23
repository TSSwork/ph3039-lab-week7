# Report workspace – 2nd-order Chebyshev low-pass (Sallen-Key)

Open `report.ipynb` (already executed, all outputs embedded). Re-run with `uv run --project ../2nd_order/impulse --with jupyter jupyter lab` or any Jupyter with numpy, pandas, scipy, matplotlib.

## What is valid
Only the 100 Hz–100 kHz sine sweep. The impulse/pulse captures (both the first-order RC and the 2nd-order ones) contain only noise and are **not** used as measurements.

## Corrections applied to the sweep
- CH1/CH2 swapped in the raw CSV → `gain = vin_v / vout_v`, phase sign flipped. Raw file untouched.
- Probe-scale error cancels in the gain ratio.
- Points above 10 kHz are noise-limited → `valid = False`, drawn hollow.

## Files
| Path | Contents |
|---|---|
| `data/bode_measurements_raw.csv` | Original sweep, unchanged |
| `data/bode_measurements_corrected.csv` | Swapped/flagged gain, dB, phase, `valid` |
| `data/key_frequencies.csv` | Passband gain, peak, peaking, −3 dB cutoff: measured, fit, theory |
| `data/rolloff_slopes.csv` | Local roll-off slope (dB/decade) |
| `data/simulated_pulse_harmonics.csv` | **Simulated** 5 kHz pulse-train FFT lines |
| `figures/bode_magnitude.png`, `bode_phase.png`, `rolloff.png` | Measured vs theory vs fit |
| `figures/signal_changes_reconstructed.png` | **Reconstructed** waveforms from fitted amplitude/phase |
| `figures/fft_pulse_simulation.png` | **Simulated** pulse spectrum |
| `figures/appendix_failed_impulse_captures.png` | Why the impulse captures are unusable |
| `theory.py` | Sallen-Key transfer function (copy of the experiment one) |

## Headline results
- Measured −3 dB cutoff ≈ 7.1 kHz; passband ≈ 6.1 dB with ≈ 1.4 dB peak near 4 kHz.
- Design/implemented theory: passband 4.5 dB, −3 dB ≈ 6.05 kHz, peaking ≈ 0.07 dB.
- Magnitude fits K ≈ 2.02, f0 ≈ 5.49 kHz, Q ≈ 1.02 (0.09 dB RMS) → suggests Rf/Rg ≈ 1 rather than 0.68. Hypothesis: check Rf and Rg with a multimeter.
- Roll-off steepens to ≈ −46 dB/decade by 10 kHz; −40 dB/decade asymptote not measurable above 10 kHz with this data.

## Friday re-measurement checklist
1. Confirm CH1 = Vout, CH2 = Vin; probe switch = `PROBE_ATTENUATION`.
2. Measure Rf, Rg, R1, R2, C1, C2.
3. Re-run the sweep (vertical auto-scale now on) and save raw waveforms if possible.
4. Impulse: scope stops before generator off; use averaging or a wider pulse.
