"""Figures and numbers for report.typ.  Run from report/:  python make_figures.py"""
import json
from pathlib import Path
import numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.optimize import least_squares
from theory import DESIGN, PRACTICAL, response

# Manrope is a variable font; matplotlib needs static Regular/Bold instances
# (made with fontTools.varLib.instancer, see report/README.md).
for p in Path(__file__).resolve().parent.glob("fonts/Manrope-*.ttf"):
    font_manager.fontManager.addfont(str(p))
mpl.rcParams.update({
    "font.family": "Manrope", "font.size": 9, "axes.grid": True, "grid.alpha": .25,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 9.5,
    "axes.titleweight": "bold", "legend.frameon": False, "legend.fontsize": 8,
    "figure.dpi": 150, "savefig.bbox": "tight"})
BLUE, ORANGE, GREEN, GREY, RED = "#1f4e8c", "#e07b00", "#2a9d5c", "#8a8f98", "#c0392b"
FIG = Path("figures"); OUT = {}

# ------------------------------------------------------------ Chebyshev sweep
d = pd.read_csv("data/bode_measurements_corrected.csv"); d = d[d.valid]
f, g, ph = d.frequency_hz.values, d.gain_db.values, d.phase_deg.values
C0 = 10e-9
res = lambda p: g - response(f, PRACTICAL, C=p[0] * 1e-9)[0]
fit = least_squares(res, [10.0]); C_fit = fit.x[0] * 1e-9
OUT["C_fit_nF"] = fit.x[0]
ff = np.logspace(2, 4, 600)

def stats(circ, C):
    db = response(ff, circ, C=C)[0]; i = db.argmax()
    m = response(f, circ, C=C)
    e = g - m[0]; pe = (ph - m[1] + 180) % 360 - 180
    return dict(pass_dB=db[0], peak_dB=db.max() - db[0], peak_Hz=ff[i],
                f3_Hz=ff[np.where(db < db[0] - 3.0103)[0][0]],
                mag_rms=np.sqrt(np.mean(e**2)), phase_rms=np.sqrt(np.mean(pe**2)), phase_max=abs(pe).max())
OUT["built_nominalC"] = stats(PRACTICAL, C0)
OUT["built_fitC"] = stats(PRACTICAL, C_fit)
OUT["design"] = stats(DESIGN, C0)
gm = g; ref = g[:3].mean(); i = np.where(g < ref - 3.0103)[0][0]
OUT["measured"] = dict(pass_dB=ref, peak_dB=g.max() - ref, peak_Hz=f[g.argmax()],
                       f3_Hz=np.interp(ref - 3.0103, [g[i], g[i - 1]], [f[i], f[i - 1]]))
def slope(a, b):
    return (np.interp(b, f, g) - np.interp(a, f, g)) / np.log10(b / a)
OUT["slope_meas_5k_10k"] = slope(5e3, 10e3); OUT["slope_meas_7k_10k"] = slope(7e3, 10e3)
for nm, circ, C in [("built_nominalC", PRACTICAL, C0), ("built_fitC", PRACTICAL, C_fit), ("design", DESIGN, C0)]:
    a = response(np.array([7e3, 10e3]), circ, C=C)[0]; OUT[f"slope_{nm}_7k_10k"] = (a[1] - a[0]) / np.log10(10 / 7)
    a = response(np.array([5e3, 10e3]), circ, C=C)[0]; OUT[f"slope_{nm}_5k_10k"] = (a[1] - a[0]) / np.log10(2)
hi = np.logspace(4.5, 6, 50)
for nm, circ, C in [("built_fitC", PRACTICAL, C_fit)]:
    a = response(hi, circ, C=C)[0]; OUT["slope_theory_asymptote"] = np.polyfit(np.log10(hi), a, 1)[0]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 5.6), sharex=True, gridspec_kw={"hspace": .12})
a1.semilogx(ff, response(ff, DESIGN)[0], ":", color=GREY, lw=1.6, label="Design (R$_g$ = 10 kΩ)")
a1.semilogx(ff, response(ff, PRACTICAL)[0], "--", color=ORANGE, lw=1.6, label="Built, C = 10 nF")
a1.semilogx(ff, response(ff, PRACTICAL, C=C_fit)[0], "-", color=BLUE, lw=1.8, label=f"Built, C = {C_fit*1e9:.1f} nF")
a1.semilogx(f, g, "o", color="k", ms=4, label="Measured")
a1.axvline(3000, color=GREY, lw=.8, ls="-.", alpha=.6); a1.text(3100, 0.2, "3 kHz", color=GREY, fontsize=7.5, va="bottom")
a1.set_ylabel("Gain (dB)"); a1.legend(loc="lower left"); a1.set_title("Second-order Chebyshev low-pass: Bode plot")
a2.semilogx(ff, response(ff, PRACTICAL)[1], "--", color=ORANGE, lw=1.6)
a2.semilogx(ff, response(ff, PRACTICAL, C=C_fit)[1], "-", color=BLUE, lw=1.8)
a2.semilogx(f, ph, "o", color="k", ms=4)
a2.set_ylabel("Phase (°)"); a2.set_xlabel("Frequency (Hz)")
fig.savefig(FIG / "cheb_bode.png", dpi=220); plt.close(fig)

# ------------------------------------------------------------ first-order pulse
K1 = "../kenura/keysight-capture/data/sessions/1-pole_bode_data-{}.json"
fc_th = 1 / (2 * np.pi * 10e3 * 1e-9)
def load(k):
    j = json.load(open(K1.format(k))); t, vi, vo = (np.array(j[x]) for x in ("time_s", "ch1_v", "ch2_v"))
    n = len(t); vi = vi - np.median(vi[-n // 10:]); vo = vo - np.median(vo[-n // 10:]); return t, vi, vo
rows = []; RUN = {}
for k in (1, 2, 3):
    t, vi, vo = load(k); dt = np.median(np.diff(t))
    X, Y, fr = np.fft.rfft(vi), np.fft.rfft(vo), np.fft.rfftfreq(len(t), dt)
    ok = (fr > 0) & (fr < 300e3) & (np.abs(X) > .05 * np.abs(X[1:]).max()); H = Y[ok] / X[ok]; fk = fr[ok]
    mdl = lambda p: 20 * np.log10(p[0] / np.sqrt(1 + (fk / p[1])**2))
    r = least_squares(lambda p: 20 * np.log10(np.abs(H)) - mdl(p), [1, 1e4]); G, fc = r.x
    gdb = 20 * np.log10(np.abs(H)); pe = np.degrees(np.angle(H)) + np.degrees(np.arctan(fk / fc))
    hi_ = (fk >= 50e3)
    sl = np.polyfit(np.log10(fk[hi_]), gdb[hi_], 1)[0]
    rows.append(dict(run=k, bins=int(ok.sum()), G_dB=20 * np.log10(G), fc_Hz=fc, mag_rms_dB=np.sqrt(np.mean(r.fun**2)),
                     phase_rms_deg=np.sqrt(np.mean(pe**2)), slope_dB_dec=sl, adc_levels=len(np.unique(vi))))
    RUN[k] = (fk, H, G, fc)
OUT["first_order"] = rows; OUT["fc_theory"] = fc_th
good = [2, 3]; Gm = np.mean([RUN[k][2] for k in good]); fcm = np.mean([RUN[k][3] for k in good])
OUT["fc_mean_runs23"] = fcm

t, vi, vo = load(3); dt = np.median(np.diff(t))
fig, a = plt.subplots(figsize=(4.4, 2.5))
a.plot(t * 1e6, vi, color=BLUE, lw=1.4, label="Input V$_{in}$")
a.plot(t * 1e6, vo * 5, color=ORANGE, lw=1.4, label="Output V$_{out}$ (× 5)")
a.set_xlim(-3, 40); a.set_xlabel("Time (µs)"); a.set_ylabel("Voltage (V)"); a.legend(loc="upper right")
fig.savefig(FIG / "lp_time.png", dpi=220); plt.close(fig)

ffl = np.logspace(3.3, np.log10(300e3), 400)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.9), gridspec_kw={"wspace": .3})
for k, c, al in [(1, GREY, .6), (2, GREEN, 1), (3, ORANGE, 1)]:
    fk, H, *_ = RUN[k]
    a1.semilogx(fk, 20 * np.log10(np.abs(H)), ".", ms=3, color=c, alpha=al, label=f"Run {k}")
    a2.semilogx(fk, np.degrees(np.angle(H)), ".", ms=3, color=c, alpha=al)
a1.semilogx(ffl, 20 * np.log10(Gm / np.sqrt(1 + (ffl / fcm)**2)), "-", color=BLUE, lw=1.6, label=f"Fit, f$_c$ = {fcm/1e3:.1f} kHz")
a1.semilogx(ffl, 20 * np.log10(1 / np.sqrt(1 + (ffl / fc_th)**2)), "--", color="k", lw=1, label=f"Theory, {fc_th/1e3:.1f} kHz")
a2.semilogx(ffl, -np.degrees(np.arctan(ffl / fcm)), "-", color=BLUE, lw=1.6)
a2.semilogx(ffl, -np.degrees(np.arctan(ffl / fc_th)), "--", color="k", lw=1)
a1.set_xlabel("Frequency (Hz)"); a2.set_xlabel("Frequency (Hz)"); a1.set_ylabel("Gain (dB)"); a2.set_ylabel("Phase (°)")
a1.legend(loc="lower left"); a1.set_title("Magnitude"); a2.set_title("Phase")
fig.savefig(FIG / "lp_bode.png", dpi=220); plt.close(fig)

def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    return float(o) if isinstance(o, (np.floating, float)) else o
json.dump(clean(OUT), open("data/report_numbers.json", "w"), indent=1)
print(json.dumps(clean(OUT), indent=1))
