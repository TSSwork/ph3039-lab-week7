"""Theoretical response of the 2nd-order Sallen-Key Chebyshev low-pass filter.

Sallen-Key with C1 (feedback) = C2 = C, source resistors R1 and R2, and a
non-inverting gain K = 1 + Rf/Rg:

    H(s) = K / (s^2 R1 R2 C^2 + s C (R1 + R2 + R1 (1 - K)) + 1)

For R1 = R2 = R this reduces to K w0^2 / (s^2 + (3 - K) w0 s + w0^2),
w0 = 1/(R C).  The passband gain is K (not 1), so the theory must include it.
"""

import numpy as np

C_FARADS = 10e-9
RG = 10e3

# Calculated (design) values: 3 kHz passband edge, 1 % Chebyshev ripple.
DESIGN = {"label": "Design (R=2.818k, Rf=6.893k, Rg=10k)",
          "R": 2.818e3, "Rf": 6.893e3, "Rg": 10e3}

# Components actually built, measured with a multimeter.  Which of the two
# source resistors is R1 was not recorded (the other order changes the
# result negligibly).  Rg is 6.78 kOhm, NOT the 10 kOhm of the design.
PRACTICAL = {"label": "Built (R1=2.72k, R2=2.77k, Rf=6.75k, Rg=6.78k)",
             "R": 2.72e3, "R2": 2.77e3, "Rf": 6.75e3, "Rg": 6.78e3}


def transfer_function(frequency, R, Rf, C=C_FARADS, Rg=RG, R2=None):
    """Complex H(j 2 pi f); R is R1, and R2 defaults to R."""
    R2 = R if R2 is None else R2
    s = 1j * 2 * np.pi * np.asarray(frequency, dtype=float)
    K = 1 + Rf / Rg
    return K / (s**2 * R * R2 * C**2 + s * C * (R + R2 + R * (1 - K)) + 1)


def response(frequency, circuit=PRACTICAL, C=C_FARADS):
    """Return (magnitude in dB, phase in degrees) for a circuit dict."""
    H = transfer_function(frequency, circuit["R"], circuit["Rf"], C=C,
                          Rg=circuit.get("Rg", RG), R2=circuit.get("R2"))
    return 20 * np.log10(np.abs(H)), np.degrees(np.unwrap(np.angle(H)))
