import pyvisa
from RsInstrument import RsInstrument
import time


class InstrumentNotConnectedException(Exception):
    """Exception to indicate that an instrument operation was attempted while disconnected."""
    pass


class InstrumentProxy:
    def __init__(self, instrument):
        self.instrument = instrument
        self.is_connected = instrument is not None

    def __getattr__(self, item):
        """
        This magic method is called whenever an attribute of this proxy object is accessed.
        It checks if the instrument is connected and returns a callable that either forwards
        the call to the actual instrument or does nothing.
        """
        if self.is_connected:
            attr = getattr(self.instrument, item)
            if callable(attr):
                return attr
            else:
                return attr
        else:
            return self._do_nothing

    def _do_nothing(self):
        """A method that does nothing. Used for ignoring calls to disconnected instruments."""
        raise InstrumentNotConnectedException("Attempted operation on a disconnected instrument.")
        pass


def create_instrument(address, instrument_type="VISA", id=False, reset=False):
    rm = pyvisa.ResourceManager()
    instrument = None

    try:
        if instrument_type.upper() == "VISA":
            instrument = rm.open_resource(address)
            print(f"Connected to VISA instrument at {address}")
        elif instrument_type.upper() == "RS":
            instrument = RsInstrument(address, id_query=id, reset=reset)
            print(f"Connected to Rohde-Schwarz instrument at {address}")
        else:
            raise ValueError("Unsupported instrument type. Use 'VISA' or 'RS'.")
    except Exception as e:
        print(f"Failed to connect to instrument at {address}: {str(e)}")
        instrument = None  # Ensure instrument is None to indicate a failed connection

    return InstrumentProxy(instrument)


def bias_voltage(voltage="10"):
    """
    Sets the bias pull-in voltage for the signal generator, adjusting for the amplifier's effect.

    :param voltage: The desired voltage level as a string, which will be adjusted for the amplifier's gain.
                    The final voltage set on the signal generator is the user_input/20 due to the amplifier.
    :return: The actual voltage value set on the signal generator, adjusted back for the amplifier.
    """
    try:
        # Convert input voltage to the voltage for the signal generator
        voltage_at_sig_gen = float(voltage) / 20
        if voltage_at_sig_gen == 0:
            print("0 volts not accepted as input high voltage")
            voltage_at_sig_gen = 0.1
        else:
            print(f"Voltage at Signal generator output port: {voltage_at_sig_gen} V")

        # Set the signal generator's voltage
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write(f"SOURce:VOLTage:LOW 0")
        sig_gen.write(f"SOURce:VOLTage:HIGH {voltage_at_sig_gen}")

        # Query the set voltage and calculate the probe voltage
        probe_voltage = sig_gen.query("SOURce:VOLTage?")
        print(f"probe_voltage is {float(probe_voltage)}:")

        set_voltage = float(probe_voltage) * 20
        print(f"set voltage is = {set_voltage}")

        return f"{set_voltage} V"
    except InstrumentNotConnectedException as e:
        print(f"Instrument connection error: {str(e)}")
    except ValueError as e:
        print(f"Error converting voltage value: {str(e)}")
    except pyvisa.errors.VisaIOError as e:
        print(f"Communication error with the instrument: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def bias_pullin(voltage="10"):
    """
    Sets the bias pull-in voltage for the signal generator, adjusting for the amplifier's effect.

    :param voltage: The desired voltage level as a string, which will be adjusted for the amplifier's gain.
                    The final voltage set on the signal generator is the user_input/20 due to the amplifier.
    :return: The actual voltage value set on the signal generator, adjusted back for the amplifier.
    """
    try:
        # Adjust the input voltage to account for the amplifier's gain
        voltage_at_sig_gen = float(voltage) / 20
        print(voltage_at_sig_gen)

        # Configure the signal generator for the pull-in test
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write(f"SOURce:VOLTage:LOW -{voltage_at_sig_gen}")
        sig_gen.write(f"SOURce:VOLTage:HIGH {voltage_at_sig_gen}")

        # Query the signal generator to confirm the voltage setting
        probe_voltage = sig_gen.query("SOURce:VOLTage?")
        print(f"probe_voltage is {float(probe_voltage)}:")

        # Calculate the effective voltage considering the amplifier's gain
        set_voltage = float(probe_voltage) * 20
        print(f"set voltage is = {set_voltage} V")

        return f"{set_voltage} V"
    except InstrumentNotConnectedException as e:
        print(f"Instrument connection error: {str(e)}")
    except ValueError as e:
        print(f"Error converting voltage value: {str(e)}")
    except pyvisa.errors.VisaIOError as e:
        print(f"Communication error with the instrument: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def ramp_width(width="1000"):
    """
    Sets the ramp width for the signal generator used in the pull-down voltage test.

    :param width: The desired ramp width in microseconds as a string. This value determines the frequency of the ramp
    signal generated.
    :return: None, but prints out the frequency generated and any errors encountered during configuration.
    """
    try:
        # Calculate the frequency based on the desired ramp width
        frequence_gen = 1 / (4 * float(width) * 10 ** (-6))
        print(f"Frequency to be generated: {frequence_gen} Hz")

        # Configure the signal generator for a ramp function with the calculated frequency
        sig_gen.write('SOURce1:FUNCtion:RAMP:SYMMetry 50')  # Selecting ramp function
        sig_gen.write(f'FREQuency {frequence_gen}')
        sig_gen.write('OUTPut 1')  # Turn on the output

        # Check for errors after configuration
        error_log = sig_gen.query('SYSTem:ERRor?')
        error_code, error_message = error_log.split(',', 1)
        print(f"Error Code: {error_code}\nError Message: {error_message}")

        # Retry setting frequency if an error is detected
        if int(error_code) != 0:
            sig_gen.write(f'FREQuency {frequence_gen}')
            print(f"Retried setting frequency to {frequence_gen} Hz")

        time.sleep(1)
    except ValueError as e:
        print(f"Error converting ramp width value: {str(e)}")
    except pyvisa.errors.VisaIOError as e:
        print(f"Communication error with the signal generator: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


zva = create_instrument(address="TCPIP0::ZNA67-101810::inst0::INSTR", instrument_type="RS")
sig_gen = create_instrument(address='TCPIP0::A-33521B-00526::inst0::INSTR', instrument_type="VISA")
osc = create_instrument(address='TCPIP0::DPO5054-C011738::inst0::INSTR', instrument_type="VISA")
rf_gen = create_instrument(address='TCPIP0::rssmb100a179766::inst0::INSTR', instrument_type="RS")
powermeter = create_instrument(address='TCPIP0::192.168.0.83::inst0::INSTR', instrument_type="VISA")
