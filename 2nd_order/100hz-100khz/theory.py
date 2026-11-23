"""Theoretical response of the 2nd-order Sallen-Key Chebyshev low-pass filter.

Equal-component Sallen-Key (R1 = R2 = R, C1 = C2 = C), non-inverting gain
K = 1 + Rf/Rg:

    H(s) = K w0^2 / (s^2 + (3 - K) w0 s + w0^2),   w0 = 1/(R C)

The passband gain is K (not 1), so the theory curve must include it.
"""

import numpy as np

C_FARADS = 10e-9
RG = 10e3

# Calculated (design) values from the README.
DESIGN = {"label": "Design (R=2.818k, Rf=6.893k)", "R": 2.818e3, "Rf": 6.893e3}

# Practical (implemented) values from the README.
PRACTICAL = {"label": "Implemented (R=2.8k, Rf=6.8k)", "R": 2.8e3, "Rf": 6.8e3}


def transfer_function(frequency, R, Rf, C=C_FARADS, Rg=RG):
    """Complex H(j 2 pi f) for the Sallen-Key circuit."""
    s = 1j * 2 * np.pi * np.asarray(frequency, dtype=float)
    K = 1 + Rf / Rg
    w0 = 1 / (R * C)
    return K * w0**2 / (s**2 + (3 - K) * w0 * s + w0**2)


def response(frequency, circuit=PRACTICAL):
    """Return (magnitude in dB, phase in degrees) for a circuit dict."""
    H = transfer_function(frequency, circuit["R"], circuit["Rf"])
    return 20 * np.log10(np.abs(H)), np.degrees(np.unwrap(np.angle(H)))
