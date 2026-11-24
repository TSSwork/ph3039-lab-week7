// PH 3039 - Filter circuits lab report
// Preview in VS Code (Tinymist / Typst extension) or: typst watch report.typ

#set document(title: "Lab Report: Characterisation of First-Order and Second-Order Chebyshev Low-Pass Filters")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.2cm, bottom: 2.4cm),
  footer: context {
    set text(size: 8pt, fill: luma(130))
    align(center)[PH 3039 Filter circuits | Page #counter(page).display() of #counter(page).final().first()]
  },
)
#set text(font: "Manrope", size: 9.5pt, lang: "en", weight: 400)
#set par(justify: true, leading: 0.78em, spacing: 1.15em)

#let accent = rgb("#1f4e8c")
#show heading: set text(fill: accent, weight: 700)
#show heading.where(level: 1): it => block(above: 1.9em, below: 0.9em)[
  #set text(size: 13pt)
  #it.body
  #v(-0.45em)
  #line(length: 100%, stroke: 0.5pt + luma(200))
]
#show heading.where(level: 2): it => block(above: 1.4em, below: 0.7em)[
  #set text(size: 10.5pt, fill: luma(40))
  #it.body
]
#set math.equation(numbering: "(1)")
#show figure.caption: set text(size: 8.5pt, fill: luma(80))
#show figure: set block(above: 1.4em, below: 1.4em)
#show table: set par(justify: false)

// ------------------------------------------------------------------ title
#text(size: 18pt, weight: 800, fill: accent)[Lab Report: Characterisation of First-Order \ and Second-Order Chebyshev Low-Pass Filters]

#v(0.5em)
#grid(
  columns: (auto, 1fr), column-gutter: 1em, row-gutter: 0.55em,
  [*Course Code & Name:*], [PH 3039 - Data Acquisition Laboratory],
  [*Student Name:*], [M.W.T.S. Sampath],
  [*Student ID:*], [2023s20138],
  [*Lab Partner(s):*], [Kenura Gunarathna, Kaweesha Induwara],
)

= Abstract

This report characterises two low-pass filters using the Keysight EDU33212A generator and EDUX1052A oscilloscope. A first-order RC filter was measured from the FFT of its response to a 2 µs pulse. It gave a cutoff frequency of 15.6 kHz, 2.2 % below the calculated 15.92 kHz, and a roll-off of −19.4 dB/decade. A second-order Sallen-Key Chebyshev filter, designed for a 3 kHz passband edge with 1 % ripple, was measured with a sine sweep from 100 Hz to 10 kHz. Its passband gain was 6.04 dB, and the gain peaked 1.5 dB above the passband, with a −3 dB point at 7.12 kHz. With the measured resistors the model reproduces the measured gain to 0.35 dB RMS

= 1. Introduction & Theoretical Background

A filter passes some frequencies and attenuates others, and its behaviour is described by the transfer function $H(f) = V_"out" / V_"in"$, whose magnitude and phase are plotted as a Bode plot. Three quantities describe a low-pass filter: the cutoff frequency $f_c$, where the gain has fallen by 3 dB; the passband, where the signal is passed with little change; and the roll-off, the rate at which the gain falls beyond $f_c$, in dB per decade.

*First-order RC filter.* A resistor in series with a capacitor to ground has

$ H(f) = 1 / (1 + j f \/ f_c), quad f_c = 1 / (2 pi R C), $

which rolls off at $-20$ dB/decade and reaches $-45°$ phase at $f_c$ and $-90°$ at high frequency.

*Second-order Chebyshev filter.* A second-order section rolls off at $-40$ dB/decade. A Chebyshev Type I response trades a small ripple in the passband for a steeper transition than a Butterworth filter. It was built as an equal-component Sallen-Key circuit (Figure 1), for which

$ H(s) = (K omega_0^2) / (s^2 + (3 - K) omega_0 s + omega_0^2), quad omega_0 = 1 / (R C), quad K = 1 + R_f / R_g, quad Q = 1 / (3 - K). $

Unlike the passive RC filter, the passband gain is $K$, not 1. The design target was a 3 kHz passband edge with 1#sym.space.nobreak%  ripple. This needs $Q = 0.763$, hence $K = 1.689$ and a natural frequency $f_0 = 5.648$ kHz, which is above 3 kHz as is usual for a Chebyshev filter.

*Impulse method.* An ideal impulse contains all frequencies equally, so the Fourier transform of the output divided by that of the input gives the whole transfer function from a single capture, $H(f) = "FFT"(V_"out") \/ "FFT"(V_"in")$. A narrow pulse approximates this: a pulse of width $tau_p$ has a flat spectrum up to about $1\/(2 tau_p)$. A sine sweep instead measures one frequency at a time.

*Goals.* (i) Measure the Bode plot of a first-order RC low-pass filter from its response to a short pulse, and check the result against theory. (ii) Build and measure the second-order Chebyshev low-pass filter with a sine sweep, and find its passband gain, ripple, cutoff and roll-off. (iii) Compare both with the theoretical models and account for any differences.

= 2. Experimental Setup & Procedure

== 2.1 Apparatus & Materials

Both filters were built on a breadboard (Figure 1) and driven by a Keysight EDU33212A function generator (high-impedance load setting). The input and output voltages were recorded with a Keysight EDUX1052A oscilloscope, and both instruments were controlled over USB with SCPI commands. The Sallen-Key filter used a TL084 op-amp on a ±12 V supply.

#figure(
  image("figures/circuits.svg", width: 100%),
  caption: [Circuits studied. (a) First-order RC low-pass filter. (b) Second-order equal-component Sallen-Key low-pass filter.],
)

#figure(
  table(
    columns: (auto, 1fr, auto),
    align: (left, left, left),
    stroke: (x: none, y: 0.5pt + luma(200)),
    inset: (x: 6pt, y: 5pt),
    table.header[*Filter*][*Components*][*Theory*],
    [First-order RC], [R = 10 kΩ, C = 1 nF ], [$f_c = 15.92$ kHz],
    [Chebyshev, design], [$R_1 = R_2 = 2.818$ kΩ, $C_1 = C_2 = 10$ nF, $R_f = 6.893$ kΩ, $R_g = 10$ kΩ], [$K = 1.689$, $f_0 = 5.648$ kHz],
    [Chebyshev, built], [$R_1, R_2$ = 2.72 and 2.77 kΩ , $C_1 = C_2 = 10$ nF, $R_f$ = 6.75 kΩ, $R_g$ = 6.78 kΩ], [$K = 2.00$, $f_0 = 5.8$ kHz],
  ),
  caption: [Component values. The resistors were measured with a multimeter; the nearest standard values to the design are 2.8 kΩ and 6.8 kΩ.],
)

== 2.2 Experimental Procedure

*First-order filter (impulse method).* The generator produced a 4 V pulse (0 to +4 V) that was 2 µs wide with 10 ns edges, repeating at 100 Hz. The input (CH1) and output (CH2) were captured together as 7679 samples at 65 ns intervals, giving a 0.5 ms record that holds one complete pulse and the decay of the response. The scope averaged 16 acquisitions to reduce noise.

*Second-order Chebyshev filter (sine sweep).* A 1 V peak-to-peak sine wave was applied at 28 frequencies from 100 Hz to 100 kHz, in steps of 1 to 9 per decade (100, 200, ..., 900 Hz, 1, 2, ..., 9 kHz, and so on). At each frequency the generator ran for 5 s to settle, and the timebase was set to show about five cycles. One waveform was then captured from each channel.

*Analysis.* For the first-order data the baseline was removed using the end of the record, and $H(f)$ was computed from the FFT of the two channels. Only bins where the input spectrum exceeded 5 % of its peak, up to 300 kHz, were kept, which leaves about 150 points. The model $H = G\/(1 + j f\/f_c)$ was fitted to the gain in dB by least squares, and $f_c$ is the fitted value. For the sweep, a sine of the known frequency was fitted to each waveform by least squares to find its amplitude and phase. The gain is the ratio of the output to the input amplitude, so it does not depend on the vertical scale or the probe setting. The data showed that the two scope channels had been connected the opposite way round to their labels in the software, so the channels were exchanged in the analysis.

= 3. Results & Data Analysis

== 3.1 First-order RC filter (impulse response)

Figure 2 shows one capture. The output rises while the 2 µs input pulse is high and then decays exponentially. Its peak is 0.70 V, close to the 0.73 V expected from $4 "V" times (1 - e^(-t_p \/ R C))$ for $R C = 10$ µs. The response has died away well within the 0.5 ms record, so the whole response is contained in the FFT window.

#figure(
  image("figures/lp_time.png", width: 46%),
  caption: [Input pulse and filter output (multiplied by 5 for visibility), run 3.],
)

Figure 3 shows the transfer function obtained from the FFT. The pulse is short enough that its spectrum is flat over the range used (up to 300 kHz), so the whole curve comes from one capture. The three runs agree, and the first-order model fits runs 2 and 3 to 0.09 dB RMS (Table 2). The cutoff is $f_c = 15.6$ kHz, 2.2 % below the calculated 15.92 kHz. The gain falls at $-19.4$ dB/decade between 50 and 300 kHz, close to the expected $-20$, and the phase passes $-45°$ near 15 kHz and tends to $-90°$.

#figure(
  image("figures/lp_bode.png", width: 88%),
  caption: [Bode plot of the first-order filter from the FFT of three pulse captures, with the fitted model and the calculated response.],
)

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: center,
    stroke: (x: none, y: 0.5pt + luma(200)),
    inset: (x: 6pt, y: 5pt),
    table.header[*Run*][*$f_c$ (kHz)*][*Passband gain (dB)*][*Magnitude RMS error (dB)*][*Phase RMS error (°)*][*Roll-off (dB/decade)*],
    [1], [15.3], [−0.13], [0.71], [5.5], [−19.4],
    [2], [15.5], [−0.27], [0.09], [1.7], [−19.4],
    [3], [15.6], [−0.29], [0.09], [1.6], [−19.4],
  ),
  caption: [First-order fit for each capture. Run 1 is noisier because its input used only 25 ADC levels. The calculated values are $f_c = 15.92$ kHz, 0 dB and $-20$ dB/decade.],
)

The frequency resolution of the FFT is 2 kHz, set by the 0.5 ms record, so only about seven points lie below $f_c$. The fit uses about 150 points up to 300 kHz, which is why $f_c$ is still well determined.

== 3.2 Second-order Chebyshev filter (sine sweep)

Figure 4 shows the measured gain and phase from 100 Hz to 10 kHz. Points above 10 kHz are not shown: there the output amplitude was too small compared with the scope noise at the vertical scale used, so the fitted amplitudes are not reliable. The measured gain is 6.04 dB at low frequency, rises to a maximum of 7.6 dB at 4 kHz, and then falls. The phase passes $-90°$ near 5.5 kHz and reaches $-151°$ at 10 kHz.

#figure(
  image("figures/cheb_bode.png", width: 62%),
  caption: [Measured Bode plot of the Chebyshev filter against the calculated response of the design and of the circuit as built.],
)

The design curve (dotted) does not describe the data, because the gain resistor that was built was 6.78 kΩ instead of the designed 10 kΩ. With the measured resistors, $K = 1 + 6.75 \/ 6.78 = 2.00$ (+6.0 dB) and $Q = 1 \/ (3 - K) = 1.0$, so the passband gain and the height of the peak both follow. The built circuit then matches the measured gain to 0.35 dB RMS using the nominal 10 nF capacitors. The measured $-3$ dB point is lower than this curve predicts, and the data are fitted better, to 0.20 dB RMS, by $C = 10.4$ nF, 3.5 % above nominal.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, center, center, center, center),
    stroke: (x: none, y: 0.5pt + luma(200)),
    inset: (x: 6pt, y: 5pt),
    table.header[][*Measured*][*Built, 10 nF*][*Built, 10.4 nF*][*Design*],
    [Passband gain (dB)], [6.04], [6.00], [6.00], [4.55],
    [Peaking above passband (dB)], [1.5], [1.17], [1.17], [0.09],
    [Frequency of the peak (kHz)], [4.0], [4.04], [3.91], [2.12],
    [$-3$ dB frequency (kHz)], [7.12], [7.35], [7.13], [6.07],
    [Slope, 7 to 10 kHz (dB/decade)], [−43], [−39], [−40], [−34],
    [RMS gain error vs measured (dB)], [], [0.35], [0.20], [2.40],
    [RMS phase error vs measured (°)], [], [5.9], [4.3], [8.0],
  ),
  caption: [Key quantities of the Chebyshev filter. The $-3$ dB frequency is where the gain is 3 dB below the low-frequency value. The measured peak frequency has a 1 kHz resolution because of the sweep steps.],
)

*Roll-off.* The measured slope steepens from about $-20$ dB/decade between 5 and 6 kHz to $-46$ dB/decade between 9 and 10 kHz, and the average from 7 to 10 kHz is $-43$ dB/decade. The model approaches the expected $-40$ dB/decade, which is the final slope of a second-order filter. The asymptote cannot be reached with data that stop at 10 kHz, and this shows only that the slope is already close to $-40$ dB/decade.

*Phase.* Up to 3 kHz the measured phase agrees with the model to within 0.2°. Above 4 kHz it lags the model by an amount that grows to about 10° at 10 kHz (Table 3).

= 4. Error & Uncertainty Analysis

Table 4 lists the uncertainties that matter and what each one does to the results. The resistor uncertainty is taken as 1 %, because the accuracy of the multimeter was not recorded; the capacitors were not measured, so their tolerance is an assumed 5 %.

#figure(
  table(
    columns: (auto, auto, 1fr),
    align: (left, left, left),
    stroke: (x: none, y: 0.5pt + luma(200)),
    inset: (x: 6pt, y: 5pt),
    table.header[*Source*][*Size*][*Effect*],
    [Resistors R#sub[f], R#sub[g]], [1 %], [$K = 2.00 plus.minus 0.014$, so the passband gain is $plus.minus 0.06$ dB and $Q$ is $plus.minus 1.4$ %],
    [Capacitors, Chebyshev], [5 % (assumed)], [$f_0 prop 1\/C$, so the $-3$ dB point is $plus.minus 0.36$ kHz],
    [R and C, first-order], [1 %, 5 % (assumed)], [$f_c prop 1\/(R C)$, so $f_c$ is $plus.minus 5.1$ % ($plus.minus 0.8$ kHz)],
    [Three pulse captures], [15.3 to 15.6 kHz], [Spread of the fitted $f_c$ is $plus.minus 0.2$ kHz],
    [Sine sweep scatter], [0.20 dB RMS], [Gain residual of the best fit, taken as the gain uncertainty (about 2 %)],
    [FFT resolution], [2 kHz], [Few points below $f_c$; $f_c$ is set by the fit of about 150 points],
  ),
  caption: [Main sources of uncertainty.],
)

*Comparison with theory.* The first-order $f_c$ (mean of runs 2 and 3, 15.57 kHz) is 2.2 % below the calculated value, which is inside the 5.1 % tolerance of the components. For the Chebyshev filter built with the measured resistors, the passband gain differs from theory by $+0.04$ dB (0.4 %), and the $-3$ dB frequency is 3.1 % below the 7.35 kHz calculated for 10 nF capacitors. This is inside the assumed 5 % capacitor tolerance and has the sign expected if the capacitors are slightly larger than nominal. Against the design values the passband gain is wrong by $+1.49$ dB (19 %), far outside any uncertainty in Table 4, so it is a real change in the circuit and not a measurement error.

*Fit quality.* The first-order fit residual is 0.09 dB RMS for runs 2 and 3 and 0.71 dB for run 1, whose input used only 25 ADC levels. The $C = 10.4$ nF of the Chebyshev fit absorbs every other small error in the model, so it is not a measurement of the capacitor.


= 5. Discussion & Conclusion

*First-order filter.* The RC filter behaves as an ideal single pole: the cutoff is 15.6 kHz against 15.92 kHz calculated, the slope is $-19.4$ dB/decade, and the phase goes from 0° to $-90°$. The pulse method gave the whole curve up to 300 kHz from one capture, but its resolution is only 2 kHz, which is poor for the low-frequency part of a response. The sine sweep took about 2.5 minutes for 28 points and can place them anywhere from 100 Hz upwards, so the two methods complement each other.

*Chebyshev filter.* The circuit that was measured is not the one that was designed. The gain resistor was 6.78 kΩ, close to the nominal 6.8 kΩ, and not the 10 kΩ of the design. This raised $K$ from 1.69 to 2.00 and $Q$ from 0.76 to 1.0, because $Q = 1\/(3 - K)$ is very sensitive near $K = 3$: an error of 0.3 in $K$ changed $Q$ by 30 %. The consequences are:
- the passband gain is 6.0 dB and not 4.55 dB;
- the peaking is 1.2 dB (1.5 dB measured), close to a Chebyshev filter with 1 dB ripple ($Q approx 0.96$), and not the 0.09 dB of a 1 % ripple design;
- the ripple band ends at 5.7 kHz and not at 3 kHz.

The filter is still a second-order low-pass filter with a steep Chebyshev-type transition, but it does not meet the 1 % ripple specification. A 10 kΩ gain resistor with the 6.8 kΩ feedback resistor ($K = 1.68$) would meet it, and measuring every component before testing would have caught the error.

*Conclusion.* Both filters were measured and compared with theory. The first-order filter agrees with $f_c = 1\/(2 pi R C)$ to 2.2 %. The Chebyshev filter agrees with the Sallen-Key model using its measured resistors to 0.35 dB RMS, which showed that its departure from the design is due to one resistor. The phase lag (about 10° at 10 kHz) and the response above 10 kHz remain open; a repeat with the correct gain resistor, measured capacitors and a larger input amplitude would address them.
