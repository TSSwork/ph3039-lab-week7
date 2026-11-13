import pyvisa
import numpy as np


class KeysightInstruments:

    def __init__(self):
        self.rm = pyvisa.ResourceManager("@py")
        self.generator = None
        self.scope = None

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------

    def connect(self):
        print("\nSearching for Keysight instruments...")

        for resource in self.rm.list_resources():
            if not resource.startswith("USB"):
                continue

            inst = self.rm.open_resource(resource)
            inst.timeout = 15000
            inst.write_termination = "\n"
            inst.read_termination = "\n"

            identity = inst.query("*IDN?").strip()
            print(f"{resource}\n  {identity}")

            if "EDU33212A" in identity:
                self.generator = inst
            elif "EDUX1052A" in identity:
                self.scope = inst
            else:
                inst.close()

        if self.generator is None or self.scope is None:
            raise RuntimeError("Could not identify both instruments.")

        self.generator.timeout = 15000
        self.scope.timeout = 30000

        print("\nBoth instruments connected.")

    # --------------------------------------------------
    # PULSE GENERATOR
    # --------------------------------------------------

    def configure_pulse_generator(
        self,
        frequency=5000,
        amplitude=3.0,
        offset=0.0,
        pulse_width=40e-9,
        leading_edge=10e-9,
        trailing_edge=10e-9,
    ):
        g = self.generator

        if g is None:
            raise RuntimeError("Generator is not connected.")

        print("\nConfiguring EDU33212A pulse output...")

        g.write("OUTP1 OFF")
        g.write("*CLS")

        g.write("SOUR1:FUNC PULS")
        g.write(f"SOUR1:FREQ {frequency}")
        g.write("SOUR1:VOLT:UNIT VPP")
        g.write(f"SOUR1:VOLT {amplitude}")
        g.write(f"SOUR1:VOLT:OFFS {offset}")
        g.write("OUTP1:LOAD INF")

        g.write(f"SOUR1:FUNC:PULS:WIDT {pulse_width}")
        g.write(
            f"SOUR1:FUNC:PULS:TRANsition:LEADing {leading_edge}"
        )
        g.write(
            f"SOUR1:FUNC:PULS:TRANsition:TRAILing {trailing_edge}"
        )

        print("\nGenerator settings:")
        print("Frequency:", g.query("SOUR1:FREQ?").strip(), "Hz")
        print("Amplitude:", g.query("SOUR1:VOLT?").strip(), "Vpp")
        print("Offset:", g.query("SOUR1:VOLT:OFFS?").strip(), "V")
        print("Pulse width:", g.query("SOUR1:FUNC:PULS:WIDT?").strip(), "s")
        print(
            "Leading edge:",
            g.query("SOUR1:FUNC:PULS:TRANsition:LEADing?").strip(),
            "s"
        )
        print(
            "Trailing edge:",
            g.query("SOUR1:FUNC:PULS:TRANsition:TRAILing?").strip(),
            "s"
        )

        error = g.query("SYST:ERR?").strip()
        print("\nGenerator error:", error)

        if not error.startswith("+0"):
            raise RuntimeError(f"Generator configuration failed: {error}")

        g.write("OUTP1 ON")
        print("\nPulse output enabled.")

    # --------------------------------------------------
    # SINE GENERATOR
    # --------------------------------------------------

    def configure_generator(self, frequency, amplitude=1.0):
        g = self.generator

        g.write("OUTP1 OFF")
        g.write("SOUR1:FUNC SIN")
        g.write(f"SOUR1:FREQ {frequency}")
        g.write("SOUR1:VOLT:UNIT VPP")
        g.write(f"SOUR1:VOLT {amplitude}")
        g.write("SOUR1:VOLT:OFFS 0")
        g.write("OUTP1:LOAD INF")

        error = g.query("SYST:ERR?").strip()
        if not error.startswith("+0"):
            raise RuntimeError(f"Generator error: {error}")

        g.write("OUTP1 ON")

    # --------------------------------------------------
    # OSCILLOSCOPE CONFIGURATION
    # --------------------------------------------------

    def configure_scope(self):
        s = self.scope

        if s is None:
            raise RuntimeError("Oscilloscope is not connected.")

        s.write("*CLS")
        s.write(":STOP")

        s.write(":CHAN1:DISP ON")
        s.write(":CHAN2:DISP ON")

        # CH1 = Vout, CH2 = Vin
        # Both probes are physically 10x.
        s.write(":CHAN1:PROB 10")
        s.write(":CHAN2:PROB 10")

        s.write(":CHAN1:COUP DC")
        s.write(":CHAN2:COUP DC")

        s.write(":TRIG:MODE EDGE")
        s.write(":TRIG:EDGE:SOUR CHAN2")
        s.write(":TRIG:EDGE:SLOP POS")
        s.write(":TRIG:SWE AUTO")

        s.write(":WAV:FORM BYTE")
        s.write(":WAV:POIN:MODE RAW")

        print("\nOscilloscope configured.")

    # --------------------------------------------------
    # WAVEFORM ACQUISITION
    # --------------------------------------------------

    def acquire_channel(self, channel):
        s = self.scope

        s.write(f":WAV:SOUR CHAN{channel}")

        preamble = [
            float(x)
            for x in s.query(":WAV:PRE?").strip().split(",")
        ]

        # EDUX1052A returns ten fields.
        if len(preamble) != 10:
            raise RuntimeError(
                f"Unexpected waveform preamble: {preamble}"
            )

        points = int(preamble[2])

        # Correct ten-field preamble positions.
        x_increment = preamble[4]
        x_origin = preamble[5]
        x_reference = preamble[6]

        y_increment = preamble[7]
        y_origin = preamble[8]
        y_reference = preamble[9]

        raw = np.asarray(
            s.query_binary_values(
                ":WAV:DATA?",
                datatype="B",
                container=np.array,
                header_fmt="ieee",
            ),
            dtype=float
        )

        voltage = (
            (raw - y_reference) * y_increment + y_origin
        )

        time_axis = (
            x_origin
            + (np.arange(len(raw)) - x_reference) * x_increment
        )

        if points and len(raw) != points:
            print(
                f"Warning: expected {points} points, "
                f"received {len(raw)}"
            )

        return time_axis, voltage

    # --------------------------------------------------
    # CAPTURE STORED WAVEFORMS
    # --------------------------------------------------

    def capture(self):
        if self.scope is None:
            raise RuntimeError("Oscilloscope is not connected.")

        # Read the already-stored acquisition.
        # Do not trigger another acquisition here.
        time_out, output = self.acquire_channel(1)
        time_in, input_signal = self.acquire_channel(2)

        if len(time_out) != len(time_in):
            raise RuntimeError("Channel waveform lengths differ.")

        return time_in, input_signal, output

    # --------------------------------------------------
    # CLOSE CONNECTIONS
    # --------------------------------------------------

    def close(self):
        print("\nClosing instrument connections...")

        if self.generator is not None:
            try:
                self.generator.write("OUTP1 OFF")
                print("Generator output disabled.")
            except Exception as e:
                print("Generator shutdown warning:", e)

            try:
                self.generator.close()
            except Exception:
                pass

        if self.scope is not None:
            try:
                self.scope.close()
            except Exception:
                pass

        try:
            self.rm.close()
        except Exception:
            pass

        print("Connections closed.")
