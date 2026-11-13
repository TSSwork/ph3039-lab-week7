from instruments import KeysightInstruments

instruments = KeysightInstruments()

try:
    instruments.connect()

    instruments.configure_pulse_generator(
        frequency=5000,
        amplitude=3.0,
        offset=0.0,
        pulse_width=20e-9,
        leading_edge=8.4e-9,
        trailing_edge=8.4e-9,
    )

    input(
        "\nPulse is enabled. "
        "Check the generator and oscilloscope. "
        "Press ENTER to switch it off..."
    )

except Exception as e:
    print("\nERROR:", repr(e))

finally:
    instruments.close()
