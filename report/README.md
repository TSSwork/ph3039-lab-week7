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
- Magnitude fits K ≈ 2.02, f0 ≈ 5.49 kHz, Q ≈ 1.02 (0.09 dB RMS) → matches the measured resistors: Rf = 6.75 kΩ and Rg = 6.78 kΩ (not the designed 10 kΩ) give K = 2.00. The f0 offset corresponds to an effective C of about 10.4 nF (capacitors not measured).
- Roll-off steepens to ≈ −46 dB/decade by 10 kHz; −40 dB/decade asymptote not measurable above 10 kHz with this data.

## Friday re-measurement checklist
1. Confirm CH1 = Vout, CH2 = Vin; probe switch = `PROBE_ATTENUATION`.
2. Measure Rf, Rg, R1, R2, C1, C2.
3. Re-run the sweep (vertical auto-scale now on) and save raw waveforms if possible.
4. Impulse: scope stops before generator off; use averaging or a wider pulse.

## First-order low-pass (impulse / FFT)

`lowpass_impulse.ipynb` analyses the 1-pole pulse captures from another group (`../kenura/.../1-pole_bode_data-{1,2,3}.json`, read in place, git-ignored, not copied here). Outputs: `figures/lp_*.png`, `data/lowpass_fit_summary.csv`, `data/lowpass_key_frequencies.csv`. Result: fc about 15.5 kHz, -20 dB/decade roll-off, phase to -90 deg. The 2nd-order Chebyshev part of the report uses only our own sine sweep.

## Written report (Typst)

`report.typ` is the lab report (preview in VS Code with the Typst/Tinymist extension, or `typst compile report.typ`). Figures and numbers for it come from `make_figures.py` (reads `data/` and the partner's pulse captures in `../kenura/`), which also writes `data/report_numbers.json`. `fonts/` holds static Regular and Bold instances of Manrope for matplotlib. `theory.py` now uses the measured components (R1 = 2.72 kΩ, R2 = 2.77 kΩ, Rf = 6.75 kΩ, Rg = 6.78 kΩ).
