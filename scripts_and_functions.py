import numpy as np
import pandas as pd
import time
import dir_and_var_declaration
import matplotlib.pyplot as plt
import matplotlib.artist
import matplotlib.ticker as ticker
import os
import pyvisa
import RsInstrument
from RsInstrument import *
from dir_and_var_declaration import zva_init, sig_gen_init, osc_init, rf_gen_init, powermeter_init
from functools import wraps
from scipy.signal import savgol_filter, get_window, convolve
from matplotlib.ticker import FuncFormatter

matplotlib.ticker.ScalarFormatter(useOffset=True, useMathText=True)

# This code is dated to 15/02/24
"""
Developer : T0188303 - A.N.
"""
os.system('cls')

path = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'

# global zva, signal_Generator, osc, rf_Generator
os.chdir('{}'.format(path))
# Opening resource manager
rm = pyvisa.ResourceManager()
signal_Generator: pyvisa.Resource = sig_gen_init()
osc: pyvisa.Resource = osc_init()
zva: RsInstrument = zva_init(zva="ZVA50")
powermeter: pyvisa.Resource = powermeter_init()
rf_Generator: RsInstrument = rf_gen_init(rf_gen_type='smb')


# VNA parameter definition
# dir_and_var_declaration.zva_directories(zva)

def timing_wrapper(func):
    """
    A decorator that times the execution of the given function and
    displays the result in days, hours, minutes, and seconds.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the function
        end_time = time.time()  # Record the end time

        # Calculate elapsed time in seconds
        elapsed_time = end_time - start_time

        # Convert to days, hours, minutes, seconds
        days = int(elapsed_time // (24 * 3600))
        hours = int((elapsed_time % (24 * 3600)) // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = elapsed_time % 60

        # Display the result in a formatted string
        print(f"Execution time for {func.__name__}: "
              f"{days}d {hours}h {minutes}m {seconds:.2f}s")
        return result

    return wrapper


def sig_gen_opc_control(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = signal_Generator.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper


def powermeter_opc_control(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = powermeter.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper


@sig_gen_opc_control
def bias_voltage(voltage: str = '10') -> float:
    """
     Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20]
     because of the voltage amplifier
    :param voltage: voltage value
    :return: Set voltage at the amplifier output
    """
    # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage =
    # user_input/20] because of the amplifier
    voltage_at_sig_gen = float(voltage) / 20
    print(voltage_at_sig_gen)
    signal_Generator.write("SOURce:VOLTage:OFFSET 0")
    signal_Generator.write("SOURce:VOLTage:LOW 0")
    signal_Generator.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = signal_Generator.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(signal_Generator.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage


@sig_gen_opc_control
def bias_pull_in_voltage(voltage: str = 1) -> float:
    # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20]
    # because of the amplifier
    voltage_at_sig_gen = float(voltage) / 20
    print(voltage_at_sig_gen)
    signal_Generator.write("SOURce:VOLTage:OFFSET 0")
    signal_Generator.write("SOURce:VOLTage:LOW -{}".format(voltage_at_sig_gen))
    signal_Generator.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = signal_Generator.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(signal_Generator.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage


@sig_gen_opc_control
def ramp_width(width: float = 100) -> None:  # Set ramp length (µs) in pull down voltage test
    frequency_gen = 1 / (4 * float(width * 10 ** (-6)))
    print(f"Ramp frequency = {frequency_gen / 1e3} kHz")
    try:
        signal_Generator.write('SOURce1:FUNCtion:RAMP:SYMMetry 50')  # selecting pulse function
        signal_Generator.write('FREQuency {}'.format(frequency_gen))
        signal_Generator.write('OUTPut 1')  # Turn on output
        error_log = signal_Generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            signal_Generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except pyvisa.VisaIOError:
        print('Signal Generator VisaIOError')


def set_f_start(f_start: float = 1) -> None:  # Set start frequency function
    # f_converted = f_start+'E'+'9'
    f_converted = f_start * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STAR {}".format(f_converted, type='E'))
    print("F_start is set to {} GHz \n".format(f_start))


def set_fstop(fstop: float = 10) -> None:  # Set stop frequency function
    # f_converted = f_stop+'E'+'9' # string
    f_converted = fstop * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STOP {}".format(f_converted, type='E'))
    print("Fstop is set to {} GHz \n".format(fstop))


def number_of_points(points: float = 501) -> None:  # Set Number of points function
    zva.write_str_with_opc("SWEep:POINts {}".format(points))
    print("Number of points set to {} points \n".format(points))


def set_pulse_width(
        width: float = 10) -> None:  # Set the pulse width as a function of the VNA sweep time in S parameter
    # measurement
    try:
        width_converted = width  # float
        print("Pulse width: {} s".format(width_converted, type='E', precision=2), end='\n')
        signal_Generator.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(width_converted, type='E'))
        pri = signal_Generator.query("SOURce1:FUNCtion:PULSe:PERiod?").split('\n')[0]
        # print(f"pri={pri} s")
        prf = 1 / float(pri)
        print(f"prf={prf} Hz\npri={pri} s")
        sweep_time = zva.query_str_with_opc("SWEep:TIME?")
        print(f"Sweep time={sweep_time} s")
        if float(sweep_time) > width_converted:
            print("Pulse width is too small for a complete sweep measurement", end='\n')
            prf_req = 1 / float(sweep_time)
            print("Minimum pulse length is: {}\nRequired prf={} Hz".format(sweep_time, prf_req), end='\n')
    finally:
        print_error_log()


def sig_gen_set_output_log() -> str:  # Get error log of the signal generator
    a = r"Bias voltage set to {} V".format(float(signal_Generator.query("SOURce:VOLTage?")) * 20)
    b = r"Pulse width is set to {} s".format(float(signal_Generator.query("SOURce1:FUNCtion:PULSe:WIDTh?")))
    c = r"prf set to {} Hz".format(1 / float(signal_Generator.query("SOURce1:FUNCtion:PULSe:PERiod?")))
    return a + '\n' + b + '\n' + c


@sig_gen_opc_control
def set_prf(prf: float = 1e3) -> str:  # Set pulse repetition frequency
    pri = 1 / prf
    width = signal_Generator.query("SOURce1:FUNCtion:PULSe:WIDTh?").split('\n')[0]
    print(f"Pulse width = {width} s")
    if float(width) > pri:
        print("Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri))
        error_log = "Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri)
    else:
        signal_Generator.write("SOURce1:FUNCtion:PULSe:PERiod {}".format(pri))
        error_log = f"Pulse width set to {width}"
    return error_log


def set_zva(start: float = 1, stop: float = 10, points: float = 501) -> None:
    # Configure the ZVA with all the input parameters entered the GUI
    set_f_start(start)
    print("Fstart is set to {} GHz \n".format(float(zva.query("FREQ:STARt?")) / (10 ** 9)))
    set_fstop(stop)
    print("Fstop is set to {} GHz \n".format(float(zva.query("FREQ:STOP?")) / (10 ** 9)))
    number_of_points(points)
    print("Number of points set to {} points \n".format(zva.query("SWEep:POINts?")))


def sig_gen_set_output_ramp_log() -> str:  # Set the ramp parameters in pull down voltage test
    a = r"Ramp voltage is set to {} V".format(
        float(signal_Generator.query("SOURce:VOLTage?")) * (20 / 2))  # Gain amplifier = 20, Vcc/2
    b = r"Ramp duration is set to {} µs".format(10 ** 6 * 1 / (4 * float(signal_Generator.query("FREQuency?"))))
    return f"{a}'\n'{b}"


def zva_set_output_log() -> str:  # Get error log of the ZVA
    a = r"Fstart is set to {} GHz".format(float(zva.query("FREQ:STARt?")) / (10 ** 9))
    b = r"Fstop is set to {} GHz".format(float(zva.query("FREQ:STOP?")) / (10 ** 9))
    c = r"Number of points set to {} points".format(zva.query("SWEep:POINts?"))
    return f"{a}'\n'{b}'\n'{c}"


def trigger_measurement_zva():  # Trigger the ZVA using the signal generator
    zva.write_str_with_opc('TRIGger:SOURce EXTernal')
    signal_Generator.write('TRIG')
    signal_Generator.query('*OPC?')
    # time.sleep(2)
    print("Signal generator sent Trigger pulse \n")


@powermeter_opc_control
def powermeter_config_power_bias() -> None:
    powermeter.write('*RST')
    powermeter.write(f'{dir_and_var_declaration.power_bias_test_setup_powermeter}')


def comprep_zva():  # Preparation of the communication
    zva.visa_timeout = 5000
    zva.opc_timeout = 5000
    zva.instrument_status_checking = True
    zva.clear_status()
    print("Comms are ready")


def close_resource(resource: RsInstrument | pyvisa.Resource) -> None:
    if resource == RsInstrument:
        print(f"Closing {resource.__str__}")
    elif resource == pyvisa.Resource:
        print(f"Closing {resource.__repr__}")
    resource.close()


def close_zva() -> None:
    # Close VISA Session
    zva.close()
    print("ZVA session closed \n")


def close_sig_gen() -> None:
    # Close signal generator VISA Session
    signal_Generator.close()
    print("Signal generator session closed \n")


def close_osc() -> None:
    # Close oscilloscope VISA Session
    osc.close()
    print("Oscilloscope session closed \n")


def close_rf_gen() -> None:  # Close rf generator VISA Session
    rf_Generator.close()
    print("RF generator session closed \n")


def close_powermeter() -> None:  # Close powermeter VISA Session
    powermeter.close()
    print("Powermeter session closed \n")


def close_all_resources() -> None:  # Close all resources VISA Session
    instrument_list: list[RsInstrument | pyvisa.Resource | None] = [signal_Generator, zva, osc, rf_Generator,
                                                                    powermeter]
    for instrument in instrument_list:
        if instrument is not None:
            instrument.close()
            print(f"{instrument} closed")


def saves3p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    print(directory)
    try:  # Setting directory to directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s3p' , LOGPhase, 1,2,3".format(filename))
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s3p'".format(filename))
        print(r"s3p file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('Status Error \n')
        zva.visa_timeout = 1000


def saves2p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    try:  # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory), timeout=1000)
        time.sleep(1)
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORTs 1, '{}.s2p', LOGPhase, 1,2".format(filename))
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s2p'".format(filename))
        print(r"sp file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('RsInstrException Error \n')
    finally:
        zva.visa_timeout = 1000


def saves1p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    try:  # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        # time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe 'Trc1', '{}.s1p'".format(filename))
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s1p'".format(filename))
        print(r"sp file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('Status Error \n')
    finally:
        zva.visa_timeout = 1000


def file_get(filename: str, zva_file_dir: str = dir_and_var_declaration.ZVA_File_Dir_ZVA67,
             pc_file_dir: str = dir_and_var_declaration.PC_File_Dir,
             extension: str = 's2p') -> None:
    zva_file_dir = dir_and_var_declaration.zva_parameters["zva_traces"]
    if extension == 's3p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}\{}.s3p".format(zva_file_dir, filename),
                                                r"{}\{}.s3p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            zva.visa_timeout = 1000
    if extension == 's2p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}\{}.s2p".format(zva_file_dir, filename),
                                                r"{}\{}.s2p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            zva.visa_timeout = 1000
    if extension == 's1p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}\{}.s1p".format(zva_file_dir, filename),
                                                r"{}\{}.s1p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            zva.visa_timeout = 1000


def setup_zva_with_rst(ip: str) -> None:
    # Resetting the ZNA67 or ZVA50
    zva = RsInstrument('{}'.format(ip), id_query=True, reset=True)
    zva.opc_query_after_write = True
    zva.write_str_with_opc(
        r"MMEMory:LOAD:STATe 1, '{}'".format(dir_and_var_declaration.zva_parameters["instrument_file"]))
    zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    print('ZVA Reset complete!', end='\n')


def setup_signal_Generator_ramp_with_rst(ip: str) -> None:
    sig_gen = rm.open_resource('{}'.format(ip))
    sig_gen.write('MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.pullin_setup_sig_gen))  # Load STATE_4
    error_log = sig_gen.query('SYSTem:ERRor?')
    print('Signal generator Reset complete!', end='\n')


def configuration_sig_gen(frequency_gen: float = 150, amplitude: float = 1, pulse_width: float = 0.001333) -> None:
    try:
        signal_Generator.write('*RST')
        signal_Generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.pullin_setup_sig_gen))  # Load STATE_4
        signal_Generator.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        signal_Generator.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        signal_Generator.write("SOURce:VOLTage:OFFSET 0")
        signal_Generator.write("SOURce:VOLTage:LOW 0")
        signal_Generator.write("SOURce:VOLTage:HIGH 2.5")
        signal_Generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        signal_Generator.write('OUTPut 1')  # turn on output
        signal_Generator.write('OUTPut:SYNC:MODE NORMal')
        signal_Generator.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = signal_Generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequency_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            signal_Generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')


def configuration_sig_gen_power() -> None:
    signal_Generator.write('*RST')
    signal_Generator.write('MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.power_test_setup_sig_gen))


def configuration_sig_gen_snp(frequency_gen: float = 150, amplitude: float = 1, pulse_width: float = 0.001333) -> None:
    try:
        signal_Generator.write('*RST')
        signal_Generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.snp_meas_setup_sig_gen))  # Load STATE_4
        signal_Generator.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        signal_Generator.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        signal_Generator.write("SOURce:VOLTage:OFFSET 0")
        signal_Generator.write("SOURce:VOLTage:LOW 0")
        signal_Generator.write("SOURce:VOLTage:HIGH 2.5")
        signal_Generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        signal_Generator.write('OUTPut 1')  # turn on output
        signal_Generator.write('OUTPut:SYNC:MODE NORMal')
        signal_Generator.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = signal_Generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequency_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            signal_Generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')


def configuration_sig_gen_pull_in(ramp_length: float = 50, amplitude: float = 1) -> float:  # 50µs ramp_length
    ramp_frequency = 1 / (4 * ramp_length * 10 ** (-6))
    ramp_period = (4 * ramp_length * 10 ** (-6))
    try:
        signal_Generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.pullin_setup_sig_gen))  # Load STATE_4
        signal_Generator.write('FREQuency {}'.format(1))
        signal_Generator.write('SOURce1:FUNCtion RAMP')  # selecting pulse function
        signal_Generator.write('FUNCtion:RAMP:SYMMetry 50')
        signal_Generator.write("SOURce:VOLTage:OFFSET 0")
        signal_Generator.write("SOURce:VOLTage:LOW -{}".format(amplitude))
        signal_Generator.write("SOURce:VOLTage:HIGH {}".format(amplitude))
        signal_Generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        signal_Generator.write('OUTPut 1')  # turn on output
        signal_Generator.write('OUTPut:SYNC:MODE NORMal')
        signal_Generator.write('FREQuency {}'.format(ramp_frequency))
        error_log = signal_Generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        osc.write('HORizontal:MODE:SCAle {}'.format(ramp_period / 5))
        if int(error) != 0:
            print(error, error_log, sep='\n', end='\n')
            signal_Generator.write('FREQuency {}'.format(ramp_frequency))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')
    return ramp_period


def configuration_pull_in(ramp_length: float = 50, amplitude: float = 1, rf_frequency: float = 10):
    configuration_sig_gen_pull_in(ramp_length=50, amplitude=1)
    setup_rf_synth(frequency=rf_frequency, power=-10, power_lim=-6)


def triggered_data_acquisition(filename: str = r'default',
                               zva_file_dir: str = r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                               pc_file_dir: str = r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P",
                               file_format: str = 's2p') -> None:
    try:
        sweep_time: str = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        print("Sweep time is set to {} s\n".format(sweep_time), end='\n')
        trigger_measurement_zva()
        time.sleep(1)
        if file_format == 's3p':
            saves3p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s3p')
        elif file_format == 's2p':
            saves2p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s2p')
        elif file_format == 's1p':
            saves1p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s1p')
        print_error_log()
    except:
        sweep_time = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        signal_Generator.write('SOURce1:FREQuency {}'.format(1 / (10 * float(sweep_time))))
        print('An error occured in triggered_data_acquisition PROCESS \n')
        print('prf may be incompatible \n')
        print_error_log()


def print_error_log():
    error_log_sig_gen = ""
    error_log_sig_zva = ""
    error_string_sig_gen = ""
    error_string_zva = ""

    # Check if 'signal_Generator' is defined
    if 'signal_Generator' in globals():
        try:
            error_log_sig_gen = signal_Generator.query('SYSTem:ERRor?')
            error_string_sig_gen = error_log_sig_gen.split(",")[1]
            print('SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen, end='\n')
        except Exception as e:
            print(f"Failed to query SIGNAL GENERATOR: {str(e)}")

    # Check if 'zva' is defined
    if 'zva' in globals():
        try:
            error_log_sig_zva = zva.query_str('SYSTem:ERRor?')
            error_string_zva = error_log_sig_zva.split(",")[1]
            print('ZVA ERROR LOG:\n' + error_string_zva, end='\n')
        except Exception as e:
            print(f"Failed to query ZVA: {str(e)}")

    # Combine the error logs
    a = 'SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen
    b = 'ZVA ERROR LOG:\n' + error_string_zva
    return a + '\n' + b


def setup_osc_cycling():
    osc.write("*RST")
    osc.write('RECALL:SETUP "{}"'.format(dir_and_var_declaration.cycling_setup_oscilloscope))
    acquisition_length = osc.query("HORizontal:ACQLENGTH?")
    record_length = osc.query("HORizontal:MODE:RECOrdlength?")
    x_unit = osc.query("HORizontal:MAIn:UNIts:STRing?")
    x_scale = osc.query("HORizontal:MODE:SCAle?")
    trigger_ref = int(osc.query('HORizontal:MAIn:DELay:POSition?'))
    ch2_y_scale = osc.query("CH2:SCAle?")  # Scale of channel 2
    ch4_y_scale = osc.query("CH4:SCAle?")  # Scale of channel 4
    setup_info = dict(
        [('x_unit', x_unit), ('x_scale', x_scale), ('ch2_y_scale', ch2_y_scale), ('ch4_y_scale', ch4_y_scale),
         ('acquisition_length', acquisition_length)])
    # ('acquisition_length', acquisition_length), ('trig_ref', trig_ref)])
    return (setup_info)


def setup_rf_synth(frequency: float = 10, power: float = -10,
                   power_lim: float = -6):  # GHz, 6 dBm is max linear input for a non distorted pulse
    rf_Generator.write('SOUR:POW:LIM:AMPL -1'.format(power_lim))
    rf_Generator.write('OUTP ON')
    rf_Generator.write('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_Generator.write('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write('OUTP ON')


def get_channel_info(channel: int = 4) -> dict:
    try:
        osc.write('Data:Source CH{}'.format(channel))
        osc.write('Data:ENCdg ASCII')
        x_scale = osc.query('HORizontal:MODE:SCAle?')
        x_divisions = osc.query('HORizontal:DIVisions?')
        acquisition_length = osc.query("HORizontal:ACQLENGTH?")

        # print("acquisition_length = {} samples\n".format(acquisition_length))

        sweep_duration = float(x_scale) * float(x_divisions)
        # print("sweep duration = {} s\n".format(sweep_duration))
        y_scale = osc.query_ascii_values('WFMOutpre:Ymult?')
        y_offset = osc.query_ascii_values('WFMOutpre:YOFf?')
        channel_info = dict([('y_offset', y_offset), ('x_scale', x_scale), ('y_scale', y_scale),
                             ('x_divisions', x_divisions), ('sweep_duration', sweep_duration),
                             ('acquisition_length', acquisition_length)])
        # print("get_channel_info function ended")
    except:
        print("Unable to Get channel info")
    return channel_info


def get_curve(channel=4):
    print(f"Acquiring curver {channel}")
    curve_data = np.empty(shape=1)
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        ref_index = trigger_ref * acquisition_length  # get the 1st index of the ramp using trigger ref position and
        # acquisition length because ramp starts at trigger
        ramp_frequency = float(signal_Generator.query('FREQuency?'))  # adapt the length of the ramp with frequency

        # Determine the length of the triangle and the number of samples in the triangle
        ramp_length = 1 / (4 * ramp_frequency)
        ramp_period = 1 / (ramp_frequency)
        # print("ramp periode is = {}".format(ramp_period), end='\n')
        # rf_Generator.write("SOURce:PULM:WIDTh {}".format(ramp_period * 2))
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        number_of_samples = sample_rate * ramp_period  # Number of samples in the triangles
        # print("number of samples in the triangle is {}".format(number_of_samples))
        # print("ref_index is {}".format(ref_index))
        # data_truncated is the truncated data. This data  is cropped from ref index to 1500 samples after the end of
        # the triangle
        data_truncated = np.zeros((acquisition_length, 2))[int(ref_index):int(ref_index) + int(
            number_of_samples) + 1500]  # 1500 samples added to make sure the triangle is complete
        curve_data = data_truncated
        # data = np.zeros((acquisition_length,2))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        # curve = np.array(osc.query('CURV?').split(','), dtype=float)
        curve = np.array(osc.query('CURV?').split(','), dtype=float)[
                int(ref_index):int(ref_index) + int(number_of_samples) + 1500]
        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        time_base = info['sweep_duration'] / acquisition_length
        # print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)[
               int(ref_index):int(ref_index) + int(number_of_samples) + 1500]
        # print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        # print("get_curve function ended")
    except:
        print("Unable to acquire Data")
    return curve_data


def get_curve_fft(channel: int = 4):
    print(f"Acquiring curver {channel}")
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        curve_data = np.empty(shape=acquisition_length)
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        # curve = np.array(osc.query('CURV?').split(','), dtype=float)
        curve = np.array(osc.query('CURV?').split(','), dtype=float)

        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        data_truncated = np.zeros((acquisition_length, 2))
        curve_data = data_truncated
        time_base = info['sweep_duration'] / acquisition_length
        # print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)
        # print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        # print(curve[:, 0])
        # print(curve[:, 1])
        # print("get_curve function ended")
    except:
        print("Unable to acquire Data")
    return curve_data


def measure_pull_down_voltage(filename=r'default'):
    curve_det = get_curve(channel=4)
    curve_bias = get_curve(channel=2)
    t = curve_det[:, 1]
    rf_detector = curve_det[:, 0]
    v_bias = curve_bias[:, 0]
    file_array = np.vstack((v_bias, rf_detector, t))
    # print(file_array[:, 0], end='\n')
    np.savetxt('{}.txt'.format(filename), file_array, delimiter=',', newline='\n',
               header='#V_bias(V),rf_detector (V), time (s)')
    # except:
    #     print("Unable to acquire Data")


def power_test_sequence_v2(
        app,
        new_data_event,
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        app: Reference to the main application instance to update the plot.
        :param new_data_event: Event to signal new data is available.
        :param filename (str): The name of the file to save results. Defaults to 'test'.
        :param start (float): The starting power level in dBm. Defaults to -30.0.
        :param stop (float): The stopping power level in dBm. Defaults to -20.0.
        :param step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        :param sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        :param offset_a1: (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        :param offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')
    signal_Generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    rf_Generator.write('OUTPut 1')

    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')

    app.is_power_sweeping = True
    for power_level in power_input_amp:
        if not app.is_power_sweeping:
            break
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_Generator.write('TRIG')
        time.sleep(sleep_duration)
        # power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')), ndigits=2))
        # power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')), ndigits=2))
        app.new_data_event_power_sweep.set()
        # Update the dataframe with the new measurements
        app.file_power_sweep = pd.DataFrame({
            'Power Input DUT Avg (dBm)': power_input_dut_avg[1:],
            'Power Output DUT Avg (dBm)': power_output_dut_avg[1:]
        })
        # new_data_event.set()  # Signal that new data is available

    # Turn off the signal generator and RF generator outputs
    signal_Generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")
    # Save the DataFrame to a CSV file
    app.file_power_sweep.to_csv(f'{filename}.csv', index=False)
    app.is_power_sweeping = False
    return power_input_dut_avg, power_output_dut_avg


def power_test_sequence(
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        filename (str): The name of the file to save results. Defaults to 'test'.
        start (float): The starting power level in dBm. Defaults to -30.0.
        stop (float): The stopping power level in dBm. Defaults to -20.0.
        step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        offset_a1 (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude -29')
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')
    signal_Generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    rf_Generator.write('OUTPut 1')

    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')

    # Sweep through the power levels and record measurements
    for power_level in power_input_amp:
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_Generator.write('TRIG')
        time.sleep(sleep_duration)
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))

    # Turn off the signal generator and RF generator outputs
    power_input_dut_avg.pop(0)
    power_output_dut_avg.pop(0)
    signal_Generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")

    # Save results to file
    file_array = np.vstack((power_input_dut_avg, power_output_dut_avg))
    np.savetxt(f'{filename}.txt', file_array, delimiter=',', newline='\n',
               header='#P_in_DUT(dBm), P_out_DUT(dBm)')

    return power_input_dut_avg, power_output_dut_avg


def power_test_smf(
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        filename (str): The name of the file to save results. Defaults to 'test'.
        start (float): The starting power level in dBm. Defaults to -30.0.
        stop (float): The stopping power level in dBm. Defaults to -20.0.
        step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        offset_a1 (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')

    signal_Generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')
    rf_Generator.write('OUTPut 1')
    # Sweep through the power levels and record measurements
    for power_level in power_input_amp:
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_Generator.write('TRIG')
        time.sleep(sleep_duration)
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))

    # Turn off the signal generator and RF generator outputs
    power_input_dut_avg.pop(0)
    power_output_dut_avg.pop(0)
    signal_Generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")

    # Save results to file
    file_array = np.vstack((power_input_dut_avg, power_output_dut_avg))
    # os.chdir(path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data")
    np.savetxt(f'{filename}.txt', file_array, delimiter=',', newline='\n',
               header='#P_in_DUT(dBm), P_out_DUT(dBm)')

    return power_input_dut_avg, power_output_dut_avg


def setup_power_test_sequence(pulse_width=100, delay=30):  # in us
    # Configuration signal_Generator
    signal_Generator.write('*RST')
    signal_Generator.write(
        "MMEM:LOAD:STATe '{}'".format(dir_and_var_declaration.power_test_setup_sig_gen))  # 100_us_PULSE.sta
    # Configuration rf_Generator
    rf_Generator.write('*RST')
    rf_Generator.write(
        "MMEMory:LOAD:STATe 4, '{}'".format(dir_and_var_declaration.power_test_setup_rf_gen))  # 100_us_PULSE.sta
    rf_Generator.write("*RCL 4")  # 100_us_PULSE.sta
    # Configuration powermeter
    powermeter.write('*RST')
    powermeter.write(f'{dir_and_var_declaration.power_test_setup_powermeter}')
    # rf_Generator.write("SOURCe1:PULM:WIDTh {}".format(float(pulse_width) * 10 ** (-6)))
    # rf_Generator.write("SOURCe1:PULM:DELay {}".format(float(delay) * 10 ** (-6)))

    # delay_pulse_rf_gen = float(rf_Generator.query("SOURCe1:PULM:DELay?"))
    # width_pulse_rf_gen = float(rf_Generator.query("SOURCe1:PULM:WIDTh?"))

    # print(delay_pulse_rf_gen)
    # print(width_pulse_rf_gen)


def get_powermeter_channels(offset_a1: float = 0, offset_b1: float = 0) -> tuple[float, float, float]:
    """
    Queries the power meter values for channels A1 and B1, applies the given offsets, and returns the results.

    Args:
        offset_a1 (float): The offset to apply to the power value of channel A1. Defaults to 0.0.
        offset_b1 (float): The offset to apply to the power value of channel B1. Defaults to 0.0.

    Returns:
        tuple: A tuple containing the power values for channel A1 and channel B1, respectively, after applying the offsets.
    """
    # Initialize the power meter for continuous measurements
    powermeter.write('INIT:CONT:ALL 1')
    # Query power value for channel A1 and apply offset
    power_value_a1 = round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=3)
    # Query power value for channel B1 and apply offset
    power_value_b1 = round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=3)
    power_value_b2 = round(float(powermeter.query('FETC4?')) + offset_b1, ndigits=3)
    powermeter.write('INIT:CONT:ALL 0')
    # Print the queried power values
    # print(f"Power value for channel A1: {power_value_a1}")
    # print(f"Power value for channel B1: {power_value_b1}")
    return power_value_a1, power_value_b1, power_value_b2


# @powermeter_opc_control
def set_channel_attenuation(atts: dict[str, float]) -> None:
    """
    Sets the attenuation for specified channels on the power meter.

    Args:
        atts (dict[int, float]): A dictionary where keys are sensor numbers (1-2)
                                 and values are the attenuation values to set.
    """
    powermeter.write('SENSe1:CORRection:GAIN2:STATe 1')
    powermeter.write('SENSe2:CORRection:GAIN2:STATe 1')

    for channel, attenuation in atts.items():
        if channel == "A":
            sensor = 1
        elif channel == "B":
            sensor = 2
        command = f'SENSe{sensor}:CORRection:GAIN2:MAGNitude {attenuation}'
        print(command)
        powermeter.write(command)

        print(f"Set attenuation for channel {channel} to {attenuation} dB")


def connect():
    machines = ['ZNA67-101810', 'A-33521B-00526', 'DPO5054-C011738', 'rssmb100a179766', '192.168.0.30']
    machine_names = ['zva', 'signal_Generator', 'osc', 'rf_Generator', 'powermeter']
    # machine_dict = {zip(machine_names, machines)} for machine, machine_name in zip(machines, machine_names): try:
    # if machine_name == 'zva': machine_dict[machine_name]=RsInstrument(f'TCPIP0::{machine}::inst0::INSTR',
    # id_query=True, reset=False) else: machine_dict[machine_name]=rm.open_resource(f'TCPIP0::{
    # machine}::inst0::INSTR') except pyvisa.errors.VisaIOError: print(f"Machine {machine_name} ({machine}) is
    # offline. Skipping...")

    zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
    sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
    osc = rm.open_resource('TCPIP0::DPO5054-C011738::inst0::INSTR')
    rf_gen = RsInstrument('TCPIP0::rssmb100a179766::inst0::INSTR')
    powermeter = rm.open_resource('TCPIP0::A-N1912A-00589::inst0::INSTR')
    return zva, sig_gen, osc, rf_gen, powermeter


def send_trig():
    signal_Generator.write('TRIG')
    signal_Generator.query('*OPC?')
    return print('trigger sent')


def get_curve_cycling(channel: int = 4) -> np.array(float):
    """
    Acquire waveform data of set channel,
    functions returns an array  with the time base and values at the specified channel
    :param channel: Oscilloscope channel
    :return: Data array shape (N, 2) with N the number of samples in the channel

    """
    data = np.zeros(1)
    try:
        osc.write('Data:Source CH{}'.format(channel))
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        curve = np.array(osc.query('CURVE?').split(','), dtype=float)
        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        time_base = info['sweep_duration'] / acquisition_length
        time = np.arange(0, info['sweep_duration'], time_base)
        # print(time_base)
        data = np.zeros((acquisition_length, 2))
        data[:, 0] = (curve - y_offset) * y_scale
        data[:, 1] = time
        # print("get_curve function ended")
    except:
        print("Unable to acquire Data : Error in get_curve_cycling function")
    return data


def switching_time():
    sw_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    return sw_time


def extract_data(rf_detector_channel, v_bias_channel, ramp_start=0.20383, ramp_stop=0.20437, ramp_start_minus=0.2046,
                 ramp_stop_minus=0.20519, delay=0.2, conversion_coeff=0.047):
    """
    Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
    Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
    cycling sequence
    :param rf_detector_channel: Detector channel array
    :param v_bias_channel: Bias channel array
    :param ramp_start: Starting time of the positive ramp
    :param ramp_stop: End time of the positive ramp
    :param ramp_start_minus: Starting time of the negative ramp
    :param ramp_stop_minus: End time of the negative ramp
    :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
    :param conversion_coeff: Conversion coefficient from power to voltage of the detector
    :return: Dataframe containing all the Mems characteristics
    """

    delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
    switching_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    release_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
    amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
    relative_amplitude = amplitude_t0 - float(osc.query('MEASUrement:MEAS4:VALue?'))

    # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
    # Assign the different curves to variables
    t = rf_detector_channel[:, 1] + delay
    rf_detector_curve = rf_detector_channel[:, 0]
    v_bias_curve = v_bias_channel[:, 0]

    trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))
    # Define a ramp voltage curve to calculate pull in and pull out curve.
    # This is done by time gating using ramp_start and ramp_stop

    t0_ramp = np.where(t > ramp_start)[0][0] + trigger_offset
    t0_plus_rampwidth = list(np.where(t < ramp_stop))[0][-1] + trigger_offset

    # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
    # This is done by time gating using ramp_start_minus and ramp_stop_minus
    t0_ramp_minus = list(np.where(t > ramp_start_minus))[0][0] + trigger_offset
    t0_plus_rampwidth_minus = list(np.where(t < ramp_stop_minus))[0][-1] + trigger_offset

    # We then calculate the index corresponding to the Max voltage of our ramp
    max_positive_bias_index = np.argmax(v_bias_curve)
    min_negative_bias_index = np.argmin(v_bias_curve)

    # From the time gating we extract the ramp voltage curve ascent and descent
    ramp_voltage_curve = v_bias_curve[t0_ramp:t0_plus_rampwidth]
    negative_ramp_voltage_curve = v_bias_curve[t0_ramp_minus:t0_plus_rampwidth_minus]

    # Then comes the definition of an ascent and descent portion of the curves
    ramp_voltage_ascent = v_bias_curve[t0_ramp:max_positive_bias_index]
    ramp_voltage_descent = v_bias_curve[max_positive_bias_index:t0_plus_rampwidth]

    # Same is done for the negative portion of the curve
    ramp_voltage_descent_minus = v_bias_curve[t0_ramp_minus:min_negative_bias_index]
    ramp_voltage_ascent_minus = v_bias_curve[min_negative_bias_index:t0_plus_rampwidth_minus]

    # plt.figure(ramp_voltage_curve, label='ramp_voltage_curve')
    # plt.figure(negative_ramp_voltage_curve, label='negative_ramp_voltage_curve')
    # plt.figure(ramp_voltage_ascent, label='ramp_voltage_ascent')
    # plt.figure(ramp_voltage_descent, label='ramp_voltage_descent')
    # plt.figure(ramp_voltage_descent_minus, label='ramp_voltage_descent_minus')
    # plt.figure(ramp_voltage_ascent_minus, label='ramp_voltage_ascent_minus')
    # plt.legend()
    # plt.show()

    # Calculating the normalization value for the isolation
    normalized_isolation_plus = np.max(3 * rf_detector_curve[t0_ramp: t0_plus_rampwidth] / conversion_coeff)
    normalized_isolation_minus = np.max(
        3 * rf_detector_curve[t0_ramp_minus: t0_plus_rampwidth_minus] / conversion_coeff)

    # iso_ascent is the ascent portion of the rf_detector waveform for positive ramp
    iso_ascent = 3 * rf_detector_curve[
                     t0_ramp: max_positive_bias_index] / conversion_coeff - normalized_isolation_plus
    iso_max_ascent = np.min(iso_ascent)

    # iso_descent is the descent portion of the rf_detector waveform for positive ramp
    iso_descent = 3 * rf_detector_curve[
                      max_positive_bias_index:t0_plus_rampwidth] / conversion_coeff - normalized_isolation_plus
    iso_min_descent = np.min(iso_descent)

    # iso_descent_minus is the descent portion of the rf_detector waveform for negative ramp
    iso_descent_minus = 3 * rf_detector_curve[
                            t0_ramp_minus: min_negative_bias_index] / conversion_coeff - normalized_isolation_minus
    iso_max_descent_minus = np.min(iso_descent_minus)

    # iso_ascent_minus is the ascent portion of the rf_detector waveform for negative ramp
    iso_ascent_minus = (3 * rf_detector_curve[
                            min_negative_bias_index: t0_plus_rampwidth_minus] / conversion_coeff
                        - normalized_isolation_minus)
    iso_min_ascent_minus = np.min(iso_ascent_minus)

    # ==============================================================================
    # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
    # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
    # Positive Pull-in
    pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
    Vpullin_plus = round(ramp_voltage_ascent[pullin_index_pos], ndigits=2)
    # Negative Pull-in
    pullin_index_neg = int(np.where(iso_descent_minus <= 0.9 * iso_max_descent_minus)[0][0])
    Vpullin_minus = round(ramp_voltage_descent_minus[pullin_index_neg], ndigits=2)

    tenpercent_iso_plus = round(0.1 * iso_min_descent, ndigits=2)
    ninetypercent_iso_plus = round(0.9 * iso_max_ascent, ndigits=2)
    _100percent_iso_plus = round(iso_min_descent, ndigits=2)

    pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
    vpullout_plus = round(ramp_voltage_descent[pullout_index_pos], ndigits=2)

    pullout_index_neg = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent_minus)[0][0])
    vpullout_minus = round(ramp_voltage_ascent_minus[pullout_index_neg], ndigits=2)

    tenpercent_iso_neg = round(0.1 * iso_min_descent, ndigits=2)
    ninetypercent_iso_neg = round(0.9 * iso_max_descent_minus, ndigits=2)

    dict_ = {'vpullin_plus': [Vpullin_plus], 'vpullin_minus': [Vpullin_minus], 'vpullout_plus': [vpullout_plus],
             'vpullout_minus': [vpullout_minus], 'iso_ascent': [ninetypercent_iso_plus],
             'iso_descent_minus': [ninetypercent_iso_neg], 'switching_time': [switching_time],
             'amplitude_variation': [relative_amplitude], 'release_time': [release_time]}
    try:
        mems_characteristics = pd.DataFrame(data=dict_)
    except:
        print('Dataframe creation Error')
    print(mems_characteristics)

    return mems_characteristics


def format_duration(seconds):
    # Ensure the input is a float or integer
    if not isinstance(seconds, (float, int)):
        raise ValueError("Input should be a float or an integer representing seconds.")

    # Calculate the days, hours, minutes, and seconds
    minutes, sec = divmod(seconds, 60)
    hours, min = divmod(minutes, 60)
    days, hrs = divmod(hours, 24)

    # Format the result as d:hh:mm:ss
    formatted_time = f"{int(days):02}d {int(hrs):02}h {int(min):02}m {sec:05.2f}s"

    return formatted_time


def detect_sticking_events(df, thresholds):
    """
    Detect sticking events based on thresholds and append a 'sticking events' column to the dataframe.

    :param df: The dataframe containing the test data.
    :param thresholds: Dictionary with column names as keys and threshold values as values.
    :return: DataFrame with the 'sticking events' column appended.
    """
    sticking_events = []

    for i in range(len(df)):
        event_detected = False
        for col, threshold in thresholds.items():
            if df.at[i, col] > threshold or df.at[i, col] < 0:
                event_detected = True
                break
        sticking_events.append(1 if event_detected else 0)

    df['sticking events'] = sticking_events
    return df


def clear_screen(delay=1.0):
    """
    Clears the screen after an optional delay.
    Args:
        delay (float): Time in seconds to wait before clearing the screen.
    """
    time.sleep(delay)  # Pause for the specified delay
    os.system('cls' if os.name == 'nt' else 'clear')


@timing_wrapper
def cycling_sequence(app, new_data_event, number_of_cycles: float = 1e9, number_of_pulses_in_wf: float = 1000,
                     filename: str = "test",
                     wf_duration: float = 0.205, events: float = 100, header: str = "",
                     df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling",
                     conversion_coeff: float = 0.046):
    """
    Cycling test sequence outputs MEMS characteristics during the tested duration.

    :param conversion_coeff: Conversion coefficient from DC to RF
    :param app: Reference to the Tkinter application instance to update the plot.
    :param new_data_event: Event to signal new data is available.
    :param df_path: File path.
    :param number_of_cycles: Total number of cycles in sequence duration.
    :param number_of_pulses_in_wf: Number of pulses in waveform.
    :param filename: Test sequence output filename.
    :param wf_duration: Total duration of the waveform in the sequence.
    :param events: Number of trigger events before oscilloscope performs an acquisition.
    :param header: Header string to be written at the top of the CSV file.
    :return: File containing a dataframe.
    """
    number_of_triggers_before_acq = events  # Number of B trigger events in A -> B sequence
    number_of_triggered_acquisitions = int(number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq))
    # cycles = pd.Series(
    #     np.arange(start=0, stop=number_of_cycles, step=number_of_pulses_in_wf * number_of_triggers_before_acq),
    #     name="cycles")

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_Generator.write("OUTput 1")
    remaining_count = number_of_cycles
    app.is_cycling = True
    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Write header and DataFrame to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count: float = number_of_cycles - (
                    new_value - starting_number_of_acq) * number_of_pulses_in_wf * events
            if count == new_value:
                # print("Waiting for trigger...", end='\n')
                # time.sleep(1)
                new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

            else:
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)
                data = extract_data_v3(rf_detector_channel=ch_4_detector, v_bias_channel=ch_2_bias,
                                       conversion_coeff=conversion_coeff)
                data["cycles"] = (count - starting_number_of_acq) * number_of_pulses_in_wf * events
                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                clear_screen(0.1)
        except KeyboardInterrupt:
            break
    # Define thresholds for detecting sticking events
    thresholds = {
        "amplitude_variation": 0.5,  # Example threshold, adjust as needed
        "switching_time": 50e-6,  # Example threshold, adjust as needed
        "release_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)
    signal_Generator.write("OUTput 0")

    # Write header and DataFrame to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    new_data_event.set()  # Signal that final data is available
    print("Test complete!")
    return app.file_df


def cycling_sequence_no_processing(app, new_data_event, number_of_cycles: float = 1e9,
                                   number_of_pulses_in_wf: float = 1000,
                                   filename: str = "test",
                                   wf_duration: float = 0.205, events: float = 100, header: str = "",
                                   df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling",
                                   conversion_coeff: float = 0.046):
    """
       Cycling test sequence outputs MEMS characteristics during the tested duration.

       :param conversion_coeff: Conversion coefficient from DC to RF
       :param app: Reference to the Tkinter application instance to update the plot.
       :param new_data_event: Event to signal new data is available.
       :param df_path: File path.
       :param number_of_cycles: Total number of cycles in sequence duration.
       :param number_of_pulses_in_wf: Number of pulses in waveform.
       :param filename: Test sequence output filename.
       :param wf_duration: Total duration of the waveform in the sequence.
       :param events: Number of trigger events before oscilloscope performs an acquisition.
       :param header: Header string to be written at the top of the CSV file.
       :return: File containing a dataframe.
       """
    number_of_triggers_before_acq = events  # Number of B trigger events in A -> B sequence
    number_of_triggered_acquisitions = int(number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq))
    cycles = pd.Series(
        np.arange(start=0, stop=number_of_cycles, step=number_of_pulses_in_wf * number_of_triggers_before_acq),
        name="cycles")

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_Generator.write("OUTput 1")
    # remaining_count = number_of_cycles
    app.is_cycling = True
    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Write header and DataFrame to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count: float = number_of_cycles - (
                    new_value - starting_number_of_acq) * number_of_pulses_in_wf * events
            if count == new_value:
                # print("Waiting for trigger...", end='\n')
                new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
                # os.system('cls')
            else:
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)
                data = extract_data_v3(rf_detector_channel=ch_4_detector, v_bias_channel=ch_2_bias,
                                       conversion_coeff=conversion_coeff)
                data["cycles"] = (count - starting_number_of_acq) * number_of_pulses_in_wf * events
                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                # os.system('cls')
        except KeyboardInterrupt:
            break
    # Define thresholds for detecting sticking events
    thresholds = {
        "amplitude_variation": -2,  # Example threshold, adjust as needed
        "switching_time": 50e-6,  # Example threshold, adjust as needed
        "release_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)
    signal_Generator.write("OUTput 0")

    # Write header and DataFrame to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    new_data_event.set()  # Signal that final data is available
    print("Test complete!")
    return app.file_df


def cycling_sequence_with_escape_interrupt(app, new_data_event,
                                           number_of_cycles: float = 1e9,
                                           number_of_pulses_in_wf: float = 1000,
                                           filename: str = "test",
                                           wf_duration: float = 0.205,
                                           events: float = 100,
                                           header: str = "",
                                           df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement "
                                                   r"Data\Mechanical cycling"):
    """
    Cycling test sequence outputs MEMS characteristics during the tested duration.

    This version allows an Escape key press to interrupt the sequence gracefully.

    :param app: Reference to the Tkinter application instance to update the plot (and check for stop).
    :param new_data_event: Event to signal new data is available.
    :param df_path: File path.
    :param number_of_cycles: Total number of cycles in sequence duration.
    :param number_of_pulses_in_wf: Number of pulses in waveform.
    :param filename: Test sequence output filename.
    :param wf_duration: Total duration of the waveform in the sequence.
    :param events: Number of trigger events before oscilloscope performs an acquisition.
    :param header: Header string to be written at the top of the CSV file.
    :return: Pandas DataFrame (final data).
    """
    number_of_triggers_before_acq = events
    number_of_triggered_acquisitions = int(
        number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq)
    )

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_Generator.write("OUTput 1")
    remaining_count = number_of_cycles
    app.is_cycling = True

    # -- Main measurement loop --
    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Periodically let Tkinter process events so the user can press Escape.
        # (If running in a separate thread, this is less necessary, but harmless.)
        app.update()

        # Check if the user requested to stop (Escape key pressed).
        if app.stop_requested:
            print("ESC key pressed: stopping the cycling sequence early.")
            break

        # Write the partial data to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count = number_of_cycles - (
                    new_value - starting_number_of_acq
            ) * number_of_pulses_in_wf * events

            if count == new_value:
                # The acquisition hasn't advanced; just re-query after a short wait.
                # You may want to use time.sleep or some other logic here.
                pass
            else:
                # Acquisition advanced, gather new data
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)

                data = extract_data_v3(
                    rf_detector_channel=ch_4_detector,
                    v_bias_channel=ch_2_bias
                )
                data["cycles"] = (
                        (count - starting_number_of_acq)
                        * number_of_pulses_in_wf
                        * events
                )

                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                clear_screen(0.1)

        except KeyboardInterrupt:
            # If the user presses Ctrl+C in the console, we also stop gracefully.
            print("KeyboardInterrupt detected: stopping cycling sequence.")
            break

    # --- After exiting the loop (either completed or interrupted) ---
    # Detect “sticking events” or other final processing
    thresholds = {
        "amplitude_variation": 0.5,  # Example threshold, adjust as needed
        "switching_time": 50e-6,  # Example threshold, adjust as needed
        "release_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)

    # Disable signal generator output
    signal_Generator.write("OUTput 0")

    # Final save of the data to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    app.stop_requested = False
    new_data_event.set()  # Signal that final data is available

    print("Test complete (either finished or interrupted)!")
    return app.file_df


def save_waveform(waveform_ch4: np.array(np.array(float)), waveform_ch2: np.array(float), filename: str) -> np.array(
    float):
    data = np.zeros(shape=2)
    info = get_channel_info(channel=4)
    data = np.vstack((waveform_ch4[:, 0], waveform_ch2[:, 0], waveform_ch4[:, 1]))
    np.savetxt('{}.txt'.format(filename), data, delimiter=',', newline='\n',
               header='#waveform_ch4, waveform_ch2, time (s)')
    return data


def save_waveform_v2(waveform_ch4: np.ndarray, waveform_ch2: np.ndarray, filename: str) -> np.ndarray:
    """
    Saves waveform data to a text file and returns the combined data.

    Args:
        waveform_ch4 (np.ndarray): 2D NumPy array containing channel 4 data (e.g., time and amplitude).
        waveform_ch2 (np.ndarray): 2D NumPy array containing channel 2 data (e.g., time and amplitude).
        filename (str): The base name of the output file (without extension).

    Returns:
        np.ndarray: Combined data array containing selected columns from the input arrays.
                    Shape: (3, n), where n is the number of rows in the input arrays.

    Raises:
        ValueError: If the input arrays do not have the expected shapes.
    """
    # Check if the input arrays are valid
    if waveform_ch4.shape[1] < 2 or waveform_ch2.shape[1] < 1:
        raise ValueError("Input arrays must have at least 2 columns for waveform_ch4 and 1 column for waveform_ch2.")

    # Combine the data into a single array
    data = np.vstack((waveform_ch4[:, 0], waveform_ch2[:, 0], waveform_ch4[:, 1]))

    # Save the combined data to a text file
    np.savetxt(
        f'{filename}.txt',  # File name
        data,  # Data to save
        delimiter=',',  # Column delimiter
        newline='\n',  # Row delimiter
        header='# waveform_ch4, waveform_ch2, time (s)'  # Header for the file
    )

    return data


def online_mode():
    try:
        # Main-------------------------------------------------------------------------------------------------------------------------
        RsInstrument.assert_minimum_version('1.5.0')

        os.chdir(r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data")

        print("Connected instrument list: \n")
        # for ressouce in list(ressources.values()):
        #     print(ressouce, end='\n')

        zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
        sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
        osc = rm.open_resource('TCPIP0::DPO5054-C011738::inst0::INSTR')
        rf_gen = RsInstrument('TCPIP0::rssmb100a179766::inst0::INSTR')
        powermeter = rm.open_resource('TCPIP0::192.168.0.83::inst0::INSTR')

        idn = zva.query_str('*IDN?')
        idn2 = sig_gen.query('*IDN?')
        idn3 = osc.query('*IDN?')
        idn4 = rf_gen.query('*IDN?')

        print(idn, end='\n')
        print(idn2, end='\n')
        print(idn3, end='\n')
        print(idn4, end='\n')
    except:
        print("Connection error")


def load_config(pc_file: str,
                inst_file: str):
    """
    Loads a configuration file from the PC to the instrument and activates it.

    Parameters:
    pc_file (str): The file path of the configuration file on the PC. Default is a specified file path.
    inst_file (str): The file path on the instrument where the configuration will be loaded. Default is a specified file path.
    """
    # Reset the ZVA instrument to its default state.
    model = zva.idn_string
    print(f"Active VNA Model: {model}")
    zva.reset()
    if model == r"Rohde&Schwarz,ZVA50-4Port,1145111052100151,3.60":
        # Transfer the configuration file from the PC to the instrument.
        zva.send_file_from_pc_to_instrument(pc_file, inst_file)
        print("_______", end='\n')
        print(pc_file, end='\n')
        print("_______", end='\n')
        # Load the transferred setup on the instrument.
        zva.write_str_with_opc(f'MMEM:LOAD:STAT 1, "{inst_file}"')
        # zva.write_str_with_opc(f'MMEMory:CDIRectory "{inst_file}"')

        # Print a confirmation message indicating the configuration file has been loaded.
        print(f"{pc_file} configuration loaded to:\n{inst_file}", end='\n')
    elif model == r"Rohde-Schwarz,ZNA67-4Port,1332450064101810,2.73":
        # Transfer the configuration file from the PC to the instrument.
        zva.send_file_from_pc_to_instrument(pc_file, inst_file)

        # Load the transferred setup on the instrument.
        zva.write_str_with_opc(f'MMEM:LOAD:STAT 1,"{inst_file}"')

        # Print a confirmation message indicating the configuration file has been loaded.
        print(f"{pc_file} configuration loaded to:\n{inst_file}", end='\n')
    else:
        print(f"Instrument model not recognized, can't load config", end='\n')


def calculate_actuation_and_release_voltages(v_bias, v_logamp, detector_coefficient=1, step=20):
    """
    Calculates pull-in and pull-out voltages, as well as isolations for both the positive
    and negative bias cycles of a MEMS device based on the second derivative of the log amp voltage.

    Parameters
    ----------
    v_bias : numpy.ndarray
        Numpy array of floats representing the bias voltage applied to the MEMS.

    v_logamp : numpy.ndarray
        Numpy array of floats representing the output of the logarithmic amplifier detector.

    detector_coefficient : float, optional (default=1)
        The coefficient that relates the detector's RF to voltage characteristic, converting the voltage to dB.

    Returns
    -------
    calculations : dict
        A dictionary containing the calculated pull-in and pull-out voltages for both positive and
        negative bias, along with the ascent and descent isolations.
        Structure:
        {
            'vpullin_plus': float,
            'vpullout_plus': float,
            'vpullin_minus': float,
            'vpullout_minus': float,
            'ninetypercent_iso_ascent': float,
            'ninetypercent_iso_descent': float
        }
        :param step:
    """
    # Set the parameters for the Savitzky-Golay filter
    window_length = 15  # Length of the filter window (must be odd)
    polyorder = 4  # Order of the polynomial to fit within each window

    # Compute the first finite difference over the step size
    # This approximates the first derivative of log amp voltage spaced `step` points apart
    v_logamp_t = v_logamp[:-step * 2]
    v_bias_t = v_bias[:-step * 2]
    diff_logamp = (v_logamp_t[step:] - v_logamp_t[:-step])

    # Compute the second finite difference, which approximates the second derivative
    diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

    # Smooth the original log amplifier voltage data using the Savitzky-Golay filter
    smoothed_v_logamp_pre = savgol_filter(v_logamp_t, window_length, polyorder)
    min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)
    smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp

    # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter
    smoothed_diff_logamp_2 = savgol_filter(diff_logamp_2, window_length, polyorder)

    # Extracting positive bias values (> 2V) and negative bias values (< -2V)
    positive_bias = np.extract((v_bias > 2), v_bias)
    negative_bias = np.extract((v_bias < -2), v_bias)

    # Finding the first index of positive bias in v_bias array
    first_index_pos = np.where(v_bias == positive_bias[0])[0]

    # Finding the first and last indexes of negative bias in v_bias array
    first_index_neg = np.where(v_bias == negative_bias[0])[0]
    last_index_neg = np.where(v_bias == negative_bias[-1])[0]

    # Finding the index of the maximum positive bias (top of the triangle waveform)
    max_positive_bias_index = np.argmax(positive_bias)

    # Finding the index of the minimum negative bias (bottom of the negative triangle waveform)
    min_negative_bias_index = np.argmin(negative_bias)

    # Normalizing the log amplifier voltage over the ascent (positive bias portion)
    normalize_iso = np.max(v_logamp[first_index_pos[0]: max_positive_bias_index] / detector_coefficient)

    # Calculate isolation during the positive ascent and descent by normalizing the log amp voltage
    iso_ascent = v_logamp[
                 first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / detector_coefficient - normalize_iso
    iso_descent = v_logamp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
        positive_bias)] / detector_coefficient - normalize_iso

    # =========================================================================
    # Positive Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the positive bias cycle
    max_smoothed_diff_logamp_2 = np.max(
        smoothed_diff_logamp_2[first_index_pos[0]:first_index_pos[0] + max_positive_bias_index])
    min_smoothed_diff_logamp_2 = np.min(
        smoothed_diff_logamp_2[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(positive_bias)])

    # Pull-in voltage: Find the index where the second derivative reaches its maximum
    try:
        pullin_index_pos = int(np.where(smoothed_diff_logamp_2[first_index_pos[0]:first_index_pos[
                                                                                      0] + max_positive_bias_index] >= max_smoothed_diff_logamp_2)[
                                   0][0])
        vpullin = positive_bias[pullin_index_pos]
        iso_ascent = v_logamp[pullin_index_pos]  # Isolation at pull-in
    except IndexError as e:
        print('Did not find an index for pull-in voltage using differentiation method')
        print({e.args})
        vpullin = 0  # Fallback value

    # Pull-out voltage: Find the index where the second derivative reaches its minimum
    try:
        pullout_index_pos = int(np.where(smoothed_diff_logamp_2[
                                         first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
                                             positive_bias)] == min_smoothed_diff_logamp_2)[0][0])
        vpullout = positive_bias[max_positive_bias_index + pullout_index_pos]
    except IndexError as e:
        print('Did not find an index for pull-out voltage using differentiation method')
        print({e.args})
        vpullout = 0  # Fallback value

    # =========================================================================
    # Negative Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the negative bias cycle
    max_smoothed_diff_logamp_2_neg = np.max(
        smoothed_diff_logamp_2[first_index_neg[0]:first_index_neg[0] + min_negative_bias_index])
    min_smoothed_diff_logamp_2_neg = np.min(smoothed_diff_logamp_2[
                                            min_negative_bias_index + min_negative_bias_index:first_index_neg[0] + len(
                                                negative_bias)])

    # Pull-in voltage (negative bias): Find the index where the second derivative reaches its maximum
    try:
        pullin_index_neg = int(
            np.where(smoothed_diff_logamp_2[
                     first_index_neg[0]:first_index_neg[
                                            0] + min_negative_bias_index] == max_smoothed_diff_logamp_2_neg)[0][0])
        vpullin_neg = negative_bias[pullin_index_neg]
        iso_descent = v_logamp[pullin_index_neg]  # Isolation at pull-in (negative cycle)
    except IndexError as e:
        print('Did not find an index for pull-in voltage (negative) using differentiation method')
        print({e.args})
        vpullin_neg = 0  # Fallback value

    # Pull-out voltage (negative bias): Find the index where the second derivative reaches its minimum
    try:
        pullout_index_neg = int(np.where(
            smoothed_diff_logamp_2[
            first_index_neg[0] + min_negative_bias_index:last_index_neg[0]] <= min_smoothed_diff_logamp_2_neg)[0][0])
        vpullout_neg = negative_bias[pullout_index_neg]
    except IndexError as e:
        print('Did not find an index for pull-out voltage (negative) using differentiation method')
        print({e.args})
        vpullout_neg = 0  # Fallback value

    # =========================================================================
    # Store the results in a dictionary for both positive and negative bias cycles
    # =========================================================================
    calculations = {
        'vpullin_plus': round(vpullin, 2),  # Pull-in voltage (positive)
        'vpullout_plus': round(vpullout, 2),  # Pull-out voltage (positive)
        'vpullin_minus': round(vpullin_neg, 2),  # Pull-in voltage (negative)
        'vpullout_minus': round(vpullout_neg, 2),  # Pull-out voltage (negative)
        'ninetypercent_iso_ascent': round(iso_ascent, 2),  # Isolation at 90% ascent (positive cycle)
        'ninetypercent_iso_descent': round(iso_descent, 2)  # Isolation at 90% descent (negative cycle)
    }
    return calculations


def extract_pull_down_voltage_and_iso(file, directory, detector_coefficient=1, step=20):
    """
    Extracts the pull-down voltage and second derivative of the log amplifier signal from a CSV file.

    This function reads a CSV file containing bias voltage, log amplifier voltage, and time data,
    smooths the log amplifier signal and its second derivative using the Savitzky-Golay filter,
    and returns the processed data.

    :param file: str
        The name of the CSV file containing the data.

    :param directory: str
        The directory where the data file is located.

    :param detector_coefficient: float, optional (default is 1)
        A coefficient that could be used for detector calibration or scaling (not used in current version).

    :param step: int, optional (default is 20)
        The step size used for finite difference calculations to approximate the first and second derivatives
        of the log amplifier voltage.

    :return: tuple
        A tuple containing the following elements:
        - v_bias (np.ndarray): The truncated bias voltage array after finite difference.
        - smoothed_v_logamp (np.ndarray): The smoothed log amplifier voltage array.
        - smoothed_diff_logamp_2 (np.ndarray): The smoothed second derivative of the log amplifier voltage.
        - time_step (float): The time step between consecutive measurements.
        - time (np.ndarray): The truncated time array corresponding to the truncated v_bias.
    """

    # Change the working directory to the specified directory
    os.chdir(path=directory)

    # Open the file and load the data into a NumPy array
    # Data is assumed to be in CSV format, with the first row containing headers, and columns:
    #   1st column: Bias voltage
    #   2nd column: Logarithmic amplifier voltage
    #   3rd column: Time data
    with open(file, newline=''):
        data = np.loadtxt(fname=file, delimiter=',', unpack=True, skiprows=1)

        # Set the parameters for the Savitzky-Golay filter
        window_length = 15  # Length of the filter window (must be odd)
        polyorder = 4  # Order of the polynomial to fit within each window

        # Extract columns from the data
        v_bias = data[:, 0].copy()  # Bias voltage (first column)
        v_logamp = data[:, 1].copy()  # Logarithmic amplifier voltage (second column)
        time = data[:, 2].copy()  # Time data (third column)

        # Compute the time step between consecutive measurements
        time_step = time[1] - time[0]

        # Compute the first finite difference over the step size
        # This approximates the first derivative of log amp voltage spaced `step` points apart
        diff_logamp = (v_logamp[step:] - v_logamp[:-step])

        # Compute the second finite difference, which approximates the second derivative
        diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

        # Smooth the original log amplifier voltage data using the Savitzky-Golay filter
        smoothed_v_logamp_pre = savgol_filter(v_logamp, window_length, polyorder)
        min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)
        smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp
        # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter
        smoothed_diff_logamp_2 = savgol_filter(diff_logamp_2, window_length, polyorder)

        # Print out the time step difference multiplied by the step size (for reference)
        print(f"difference timestep {time_step * step}")

    # Return the truncated bias voltage, smoothed log amp voltage, smoothed second derivative,
    # the time step between measurements, and the truncated time array.
    return v_bias[:-step * 2], smoothed_v_logamp[:-step * 2], smoothed_diff_logamp_2, time_step, time[:-step * 2]


def extract_data_v2(rf_detector_channel, v_bias_channel, ramp_start=0.20559, ramp_stop=0.206,
                    ramp_start_minus=0.20632,
                    ramp_stop_minus=0.20679, delay=0.2, conversion_coeff=1):
    """
    Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
    Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
    cycling sequence.
    :param rf_detector_channel: Detector channel array
    :param v_bias_channel: Bias channel array
    :param ramp_start: Starting time of the positive ramp (0.20383)
    :param ramp_stop: End time of the positive ramp (0.20437)
    :param ramp_start_minus: Starting time of the negative ramp (0.2046)
    :param ramp_stop_minus: End time of the negative ramp (0.20519)
    :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
    :param conversion_coeff: Conversion coefficient from power to voltage of the detector
    :return: DataFrame containing all the MEMS characteristics
    """
    # Initialize variables with zero values
    vpullin_plus, vpullin_minus, vpullout_plus, vpullout_minus = 0, 0, 0, 0
    iso_ascent_value, iso_descent_minus_value = 0, 0
    switching_time, relative_amplitude, release_time = 0, 0, 0

    try:
        # Ensure the input arrays are numpy arrays
        rf_detector_channel = np.array(rf_detector_channel)
        v_bias_channel = np.array(v_bias_channel)

        # Extracting values using oscilloscope commands
        delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
        switching_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
        release_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
        amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
        a1, b1 = get_powermeter_channels()
        # relative_amplitude = amplitude_t0 - float(osc.query('MEASUrement:MEAS4:VALue?'))
        relative_amplitude = b1 - a1

        # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
        t = rf_detector_channel[:, 1] + delay
        rf_detector_curve = rf_detector_channel[:, 0]
        v_bias_curve = v_bias_channel[:, 0]

        trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))

        # Define a ramp voltage curve to calculate pull in and pull out curve.
        if t.size == 0:
            raise ValueError("Time array 't' is empty.")

        t0_ramp_indices = np.where(t > ramp_start)[0]
        if t0_ramp_indices.size == 0:
            raise ValueError("No elements found in 't' greater than ramp_start.")
        t0_ramp = t0_ramp_indices[0] + trigger_offset

        t0_plus_rampwidth_indices = np.where(t < ramp_stop)[0]
        if t0_plus_rampwidth_indices.size == 0:
            raise ValueError("No elements found in 't' less than ramp_stop.")
        t0_plus_rampwidth = t0_plus_rampwidth_indices[-1] + trigger_offset

        # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
        t0_ramp_minus_indices = np.where(t > ramp_start_minus)[0]
        if t0_ramp_minus_indices.size == 0:
            raise ValueError("No elements found in 't' greater than ramp_start_minus.")
        t0_ramp_minus = t0_ramp_minus_indices[0] + trigger_offset

        t0_plus_rampwidth_minus_indices = np.where(t < ramp_stop_minus)[0]
        if t0_plus_rampwidth_minus_indices.size == 0:
            raise ValueError("No elements found in 't' less than ramp_stop_minus.")
        t0_plus_rampwidth_minus = t0_plus_rampwidth_minus_indices[-1] + trigger_offset

        # Calculate the index corresponding to the Max voltage of our ramp
        max_positive_bias_index = np.argmax(v_bias_curve)
        min_negative_bias_index = np.argmin(v_bias_curve)

        # Extract the ramp voltage curve ascent and descent
        ramp_voltage_ascent = v_bias_curve[t0_ramp:max_positive_bias_index]
        ramp_voltage_descent = v_bias_curve[max_positive_bias_index:t0_plus_rampwidth]
        ramp_voltage_descent_minus = v_bias_curve[t0_ramp_minus:min_negative_bias_index]
        ramp_voltage_ascent_minus = v_bias_curve[min_negative_bias_index:t0_plus_rampwidth_minus]

        # Calculate the normalization value for the isolation
        normalized_isolation_plus = np.max(3 * rf_detector_curve[t0_ramp:t0_plus_rampwidth] / conversion_coeff)
        normalized_isolation_minus = np.max(
            3 * rf_detector_curve[t0_ramp_minus:t0_plus_rampwidth_minus] / conversion_coeff)

        # Calculate iso_ascent and iso_descent
        iso_ascent = 3 * rf_detector_curve[
                         t0_ramp:max_positive_bias_index] / conversion_coeff - normalized_isolation_plus
        iso_descent = 3 * rf_detector_curve[
                          max_positive_bias_index:t0_plus_rampwidth] / conversion_coeff - normalized_isolation_plus
        iso_descent_minus = 3 * rf_detector_curve[
                                t0_ramp_minus:min_negative_bias_index] / conversion_coeff - normalized_isolation_minus
        iso_ascent_minus = 3 * rf_detector_curve[
                               min_negative_bias_index:t0_plus_rampwidth_minus] / conversion_coeff - normalized_isolation_minus

        # Calculation Vpull in and Vpull out
        pullin_index_pos = np.where(iso_ascent <= 0.9 * np.min(iso_ascent))[0]
        if pullin_index_pos.size == 0:
            raise ValueError("No elements found in iso_ascent satisfying the condition.")
        vpullin_plus = round(ramp_voltage_ascent[pullin_index_pos[0]], 2)

        pullin_index_neg = np.where(iso_descent_minus <= 0.9 * np.min(iso_descent_minus))[0]
        if pullin_index_neg.size == 0:
            raise ValueError("No elements found in iso_descent_minus satisfying the condition.")
        vpullin_minus = round(ramp_voltage_descent_minus[pullin_index_neg[0]], 2)

        pullout_index_pos = np.where(iso_descent >= 0.1 * np.min(iso_descent))[0]
        if pullout_index_pos.size == 0:
            raise ValueError("No elements found in iso_descent satisfying the condition.")
        vpullout_plus = round(ramp_voltage_descent[pullout_index_pos[0]], 2)

        pullout_index_neg = np.where(iso_ascent_minus >= 0.1 * np.min(iso_ascent_minus))[0]
        if pullout_index_neg.size == 0:
            raise ValueError("No elements found in iso_ascent_minus satisfying the condition.")
        vpullout_minus = round(ramp_voltage_ascent_minus[pullout_index_neg[0]], 2)

        iso_ascent_value = 0.9 * np.min(iso_ascent)
        iso_descent_minus_value = 0.9 * np.min(iso_descent_minus)

    except Exception as e:
        print(f"An error occurred: {e}")

    # Creating the dictionary for DataFrame
    data = {
        'vpullin_plus': [vpullin_plus], 'vpullin_minus': [vpullin_minus], 'vpullout_plus': [vpullout_plus],
        'vpullout_minus': [vpullout_minus], 'iso_ascent': [iso_ascent_value],
        'iso_descent_minus': [iso_descent_minus_value], 'switching_time': [switching_time],
        'amplitude_variation': [relative_amplitude], 'release_time': [release_time]
    }

    # Creating the DataFrame
    mems_characteristics = pd.DataFrame(data)

    return mems_characteristics


def extract_data_v3(rf_detector_channel, v_bias_channel, ramp_start=0.20559, ramp_stop=0.206,
                    ramp_start_minus=0.2064,
                    ramp_stop_minus=0.20682, delay=0.2):
    """
        Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
        Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
        cycling sequence.
        :param rf_detector_channel: Detector channel array
        :param v_bias_channel: Bias channel array
        :param ramp_start: Starting time of the positive ramp (0.20383)
        :param ramp_stop: End time of the positive ramp (0.20437)
        :param ramp_start_minus: Starting time of the negative ramp (0.2046)
        :param ramp_stop_minus: End time of the negative ramp (0.20519)
        :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
        :return: DataFrame containing all the MEMS characteristics
        """
    # Ensure the input arrays are numpy arrays
    rf_detector_channel = np.array(rf_detector_channel)
    v_bias_channel = np.array(v_bias_channel)

    # Extracting values using oscilloscope commands
    delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
    t_on_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    t_off_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
    amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
    a1, b1, b2 = get_powermeter_channels()

    relative_amplitude = b2 - a1
    isolation = b1 - a1
    sample_rate = osc.query("HORIZONTAL:MODE:SAMPLERATE?")
    duration = osc.query("HORizontal:ACQDURATION?")

    # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
    t = rf_detector_channel[:, 1] + delay
    rf_detector_curve = rf_detector_channel[:, 0]
    v_bias_curve = v_bias_channel[:, 0]

    trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))

    # Define a ramp voltage curve to calculate pull in and pull out curve.
    if t.size == 0:
        raise ValueError("Time array 't' is empty.")

    t0_ramp_indices = np.where(t > ramp_start)[0]
    if t0_ramp_indices.size == 0:
        raise ValueError("No elements found in 't' greater than ramp_start.")
    else:
        t0_ramp = t0_ramp_indices[0]

    t0_plus_rampwidth_indices = np.where(t < ramp_stop)[0]
    if t0_plus_rampwidth_indices.size == 0:
        raise ValueError("No elements found in 't' less than ramp_stop.")
    else:
        t0_plus_rampwidth = t0_plus_rampwidth_indices[-1]

    # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
    t0_ramp_minus_indices = np.where(t > ramp_start_minus)[0]
    if t0_ramp_minus_indices.size == 0:
        raise ValueError("No elements found in 't' greater than ramp_start_minus.")
    else:
        t0_ramp_minus = t0_ramp_minus_indices[0]

    t0_plus_rampwidth_minus_indices = np.where(t < ramp_stop_minus)[0]
    if t0_plus_rampwidth_minus_indices.size == 0:
        raise ValueError("No elements found in 't' less than ramp_stop_minus.")
    else:
        t0_plus_rampwidth_minus = t0_plus_rampwidth_minus_indices[-1]

    # Calculate the index corresponding to the Max voltage of our ramp
    max_positive_bias_index = np.argmax(v_bias_curve)
    min_negative_bias_index = np.argmin(v_bias_curve)

    step = 10
    # Set the parameters for the Savitzky-Golay filter
    window_length = 9  # Length of the filter window (must be odd)
    polyorder = 4  # Order of the polynomial to fit within each window
    detector_coefficient = 1

    # Compute the first finite difference over the step size
    # This approximates the first derivative of log amp voltage spaced `step` points apart
    v_logamp_t = rf_detector_curve[:-step * 2]
    v_bias_t = v_bias_curve[:-step * 2]
    diff_logamp = (v_logamp_t[step:] - v_logamp_t[:-step])

    # Compute the second finite difference, which approximates the second derivative
    diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

    # Smooth the original log amplifier voltage data using the Savitzky-Golay filter
    smoothed_v_logamp_pre = savgol_filter(v_logamp_t, window_length, polyorder)
    min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)
    smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp

    # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter
    smoothed_diff_logamp_2 = savgol_filter(diff_logamp_2, window_length, polyorder)

    positive_bias = v_bias_t[t0_ramp + trigger_offset: t0_plus_rampwidth + trigger_offset]
    negative_bias = v_bias_t[t0_ramp_minus + trigger_offset: t0_plus_rampwidth_minus + trigger_offset]

    # Finding the first index of positive bias in v_bias array
    first_index_pos = t0_ramp  # ========> Defined by the cursor on the oscilloscope
    # print(f'first_index_pos = {first_index_pos}')

    # Finding the last index of positive bias in v_bias array
    last_index_pos = t0_plus_rampwidth  # ========> Defined by the cursor on the oscilloscope
    # print(f'last_index_pos = {last_index_pos}')

    # Finding the first index of negative bias in v_bias array
    first_index_neg = t0_ramp_minus  # ========> Defined by the cursor on the oscilloscope
    # print(f'first_index_neg = {first_index_neg}')

    # Finding the last index of negative bias in v_bias array
    last_index_neg = t0_plus_rampwidth_minus  # ========> Defined by the cursor on the oscilloscope
    # print(f'last_index_neg = {last_index_neg}')

    # Finding the index of the maximum positive bias (top of the triangle waveform)
    max_positive_bias_index = np.argmax(v_bias_t[t0_ramp + trigger_offset: t0_plus_rampwidth + trigger_offset])
    # print(f'max_positive_bias_index = {max_positive_bias_index} \n')

    # Finding the index of the minimum negative bias (bottom of the negative triangle waveform)
    min_negative_bias_index = np.argmin(
        v_bias_t[t0_ramp_minus + trigger_offset: t0_plus_rampwidth_minus + trigger_offset])

    # =========================================================================
    # Positive Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the positive bias cycle
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage
    try:
        max_smoothed_diff_logamp_2 = int(np.argmax(smoothed_diff_logamp_2[
                                                   first_index_pos:last_index_pos]))
        # print(f'max_smoothed_diff_logamp_2 = {max_smoothed_diff_logamp_2} \n')
        # print("Max was found in positive ramp")

        pullin_index_pos = int(np.argmax(smoothed_diff_logamp_2[
                                         first_index_pos + trigger_offset:first_index_pos + max_positive_bias_index + trigger_offset]))
        vpullin = v_bias_t[first_index_pos + trigger_offset + pullin_index_pos]
    except:
        print("Max was not found")
        print('Did not find an index for pull-in voltage using differentiation method')
        vpullin = 0

    # Using the minimum index -> Input this index to the v bias array to determine pull-out voltage
    try:
        min_smoothed_diff_logamp_2 = int(np.argmin(smoothed_diff_logamp_2[
                                                   first_index_pos + trigger_offset + max_positive_bias_index:last_index_pos + trigger_offset]))
        # print(f'min_smoothed_diff_logamp_2 = {min_smoothed_diff_logamp_2} \n')
        # print('Min was found in negative ramp')
        pullout_index_pos = int(np.argmin(smoothed_diff_logamp_2[
                                          first_index_pos + trigger_offset + max_positive_bias_index:last_index_pos + trigger_offset]))
        vpullout = v_bias_t[first_index_pos + max_positive_bias_index + trigger_offset + pullout_index_pos]
        # print(f'vpullout = {vpullout}')
    except:
        print('Did not find an index for pull-out voltage using differentiation method')
        print('Min was not found in negative ramp')
        vpullout = 0  # Fallback value

    # =========================================================================
    # Negative Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the negative bias cycle
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage
    try:
        max_smoothed_diff_logamp_2_neg = np.argmax(
            smoothed_diff_logamp_2[
            first_index_neg + trigger_offset:first_index_neg + min_negative_bias_index + trigger_offset])
        # print(f'max_smoothed_diff_logamp_2_neg = {max_smoothed_diff_logamp_2_neg} \n')
        # print("Max was found in negative ramp")

        pullin_index_neg = int(
            np.argmin(smoothed_diff_logamp_2[
                      first_index_neg + trigger_offset:first_index_neg + min_negative_bias_index + trigger_offset]))
        vpullin_neg = v_bias_t[first_index_neg + trigger_offset + pullin_index_neg]

        # print(f'vpullin_neg = {vpullin_neg}')
        min_smoothed_diff_logamp_2 = int(np.argmin(smoothed_diff_logamp_2[
                                                   first_index_neg:last_index_neg]))

    except:
        print("Max was not found")
        print('Did not find an index for negative pull-in(-) voltage using differentiation method')
        vpullin_neg = 0  # Fallback value

    # Pull-out voltage (negative bias): Find the index where the second derivative reaches its minimum
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage

    try:
        min_smoothed_diff_logamp_2_neg = np.argmin(smoothed_diff_logamp_2[
                                                   first_index_neg + trigger_offset + min_negative_bias_index:last_index_neg + trigger_offset])
        # print(f'min_smoothed_diff_logamp_2_neg = {min_smoothed_diff_logamp_2_neg} \n')
        # print("Min was found in negative ramp")

        pullout_index_neg = int(np.argmin(smoothed_diff_logamp_2[
                                          first_index_neg + trigger_offset + min_negative_bias_index:last_index_neg + trigger_offset]))
        vpullout_neg = v_bias_t[first_index_neg + min_negative_bias_index + trigger_offset + pullout_index_neg]
        # print(f'vpullout_neg = {vpullout_neg}')

    except:
        print("Min was not found")
        print('Did not find an index for negative pull-out(-) voltage using differentiation method')
        vpullout_neg = 0  # Fallback value

    # Creating the dictionary for DataFrame
    data = {
        'vpullin_plus': [vpullin], 'vpullin_minus': [vpullin_neg], 'vpullout_plus': [vpullout],
        'vpullout_minus': [vpullout_neg], 't_on_time': [t_on_time],
        'amplitude_variation': [relative_amplitude], 't_off_time': [t_off_time], 'absolute_isolation': [isolation]
    }
    # Creating the DataFrame
    mems_characteristics = pd.DataFrame(data)

    return mems_characteristics


def signal_Generator_cycling_config():
    signal_Generator.write("*RST")
    time.sleep(1)
    signal_Generator.write('MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.cycling_setup_sig_gen))
    time.sleep(1)
    signal_Generator.write("*OPC?")
    print("Signal Generator cycling config")


def osc_cycling_config():
    osc.write(r'RECALL:SETUP "{}"'.format(dir_and_var_declaration.cycling_setup_oscilloscope))
    print("Oscilloscope cycling config")
    osc.write("*OPC?")


def osc_pullin_config():
    osc.write(r'RECALL:SETUP "{}"'.format(dir_and_var_declaration.pullin_setup_oscilloscope))
    print("Oscilloscope pullin config")
    osc.write("*OPC?")


def rf_gen_pull_in_setup():
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(r"MMEMory:LOAD:STATe 2, '{}'".format(dir_and_var_declaration.pullin_setup_rf_gen))
    rf_Generator.write_str_with_opc('OUTP ON')
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(10, 0))


def rf_gen_cycling_setup(frequency=10, power=-10,
                         power_lim=5):
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(r"MMEMory:LOAD:STATe 1, '{}'".format(dir_and_var_declaration.cycling_setup_rf_gen))
    rf_Generator.write_str_with_opc('SOUR:POW:LIM:AMPL {}'.format(power_lim))
    rf_Generator.write_str_with_opc('OUTP ON')
    rf_Generator.write_str_with_opc('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write_str_with_opc('OUTP ON')


def rf_gen_power_setup(frequency=9.3, power=-25,
                       power_lim=0):
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(
        r"MMEMory:LOAD:STATe 4, '{}'".format(dir_and_var_declaration.power_test_setup_rf_gen))
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write_str_with_opc('SOUR:POW:LIM:AMPL {}'.format(power_lim))


def set_osc_event_count(nth_trigger=10):
    osc.write("TRIGger:B:EVENTS:COUNt {}".format(nth_trigger))
    print("Trigger on {}th trigger".format(nth_trigger))


def rf_gen_power_lim():
    pass


def rf_gen_set_freq(frequency: float = 10) -> None:
    rf_Generator.write_str_with_opc(f'SOUR:FREQ {frequency} GHz')


def apply_threshold_filter(fft_result, magnitudes, threshold_percent):
    """
    Apply threshold-based noise filtering.

    Parameters:
    fft_result: numpy array
        Complex FFT result
    magnitudes: numpy array
        FFT magnitudes
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)

    Returns:
    numpy array: Filtered FFT result
    """
    threshold = np.max(magnitudes) * (threshold_percent / 100)
    filtered_fft = fft_result.copy()
    filtered_fft[magnitudes < threshold] = 0
    return filtered_fft


def plot_signal_fft(data, filter_type='none', threshold_percent=5, sg_window=51, sg_order=3, window_type='rectangular'):
    """
    Plot the original signal and its FFT with optional noise filtering, log y-scale, and windowing.

    Parameters:
    data: numpy array of shape (N, 2)
        data[:,0] contains voltage values in volts
        data[:,1] contains time values in seconds
    filter_type: str
        'none': No filtering
        'threshold': Simple threshold-based noise filtering
        'savgol': Savitzky-Golay filtering
        'both': Apply both filters
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)
    sg_window: int
        Window length for Savitzky-Golay filter (must be odd)
    sg_order: int
        Polynomial order for Savitzky-Golay filter
    window_type: str
        'rectangular', 'hamming', 'hann', 'blackman'
    """
    # Extract voltage and time data
    voltage = data[:, 0]
    time = data[:, 1]

    # Apply window function
    window = get_window(window_type, len(voltage))
    voltage_windowed = voltage * window

    # Apply Savitzky-Golay filter to time domain if requested
    if filter_type in ['savgol', 'both']:
        voltage_filtered = savgol_filter(voltage_windowed, sg_window, sg_order)
    else:
        voltage_filtered = voltage_windowed

    # Calculate sampling parameters
    sampling_period = time[1] - time[0]
    sampling_frequency = 1.0 / sampling_period
    n_samples = len(voltage)

    # Compute FFT
    fft_result = np.fft.fft(voltage_filtered)
    fft_freq = np.fft.fftfreq(n_samples, sampling_period)

    # Calculate magnitude spectrum
    magnitude = 2.0 * np.abs(fft_result) / n_samples

    # Apply threshold filter if requested
    if filter_type in ['threshold', 'both']:
        fft_result_filtered = apply_threshold_filter(fft_result, magnitude, threshold_percent)
        magnitude_filtered = 2.0 * np.abs(fft_result_filtered) / n_samples
    else:
        magnitude_filtered = magnitude

    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot original signal
    ax1.plot(time * 1000, voltage, 'b-', label='Original Signal')
    ax1.plot(time * 1000, voltage_windowed, 'g-', label='Windowed Signal')
    if filter_type in ['savgol', 'both']:
        ax1.plot(time * 1000, voltage_filtered, 'r-', label='Filtered Signal')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Time Domain Signal')
    ax1.grid(True)
    ax1.legend()

    # Plot full FFT magnitude spectrum
    positive_freq_mask = fft_freq >= 0
    ax2.semilogy(fft_freq[positive_freq_mask], magnitude[positive_freq_mask], 'b-', label='Original FFT')
    ax2.set_xscale('log')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (log scale)')
    ax2.set_title('Full Frequency Spectrum')
    ax2.grid(True)
    ax2.legend()

    # Plot filtered FFT magnitude spectrum
    if filter_type in ['threshold', 'both']:
        ax3.semilogy(fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask], 'r-',
                     label=f'Filtered FFT (threshold: {threshold_percent}%)')
    else:
        ax3.semilogy(fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask], 'r-',
                     label='Filtered FFT')
    ax3.set_xscale('log')
    # ax3.set(xlim=[1e3, 1e6])
    ax3.set(ylim=[1e-7, 1e-2])
    ax3.set(xlim=[1e3, 200000])
    ax3.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Magnitude (log scale)')
    ax3.set_title('Filtered Frequency Spectrum')
    ax3.grid(True)
    ax3.legend()

    # Make layout tight and display plot
    plt.tight_layout()
    plt.show()

    return fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask]


def plot_signal_fft_noise_removal(current_data, previous_data, filter_type='none', threshold_percent=5, sg_window=51,
                                  sg_order=3,
                                  window_type='rectangular'):
    """
    Plot the original signal and its FFT with optional noise filtering, log y-scale, windowing, and inter-acquisition convolution.

    Parameters:
    current_data: numpy array of shape (N, 2)
        current_data[:,0] contains voltage values in volts
        current_data[:,1] contains time values in seconds
    previous_data: numpy array of shape (N, 2)
        previous_data[:,0] contains previous voltage values in volts
        previous_data[:,1] contains previous time values in seconds
    filter_type: str
        'none': No filtering
        'threshold': Simple threshold-based noise filtering
        'savgol': Savitzky-Golay filtering
        'convolve': Inter-acquisition convolution-based filtering
        'both': Apply both threshold and convolution filters
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)
    sg_window: int
        Window length for Savitzky-Golay filter (must be odd)
    sg_order: int
        Polynomial order for Savitzky-Golay filter
    window_type: str
        'rectangular', 'hamming', 'hann', 'blackman'
    """
    # Extract voltage and time data
    current_voltage = current_data[:, 0]
    current_time = current_data[:, 1]
    previous_voltage = previous_data[:, 0]
    previous_time = previous_data[:, 1]

    # Apply window function
    current_window = get_window(window_type, len(current_voltage))
    current_voltage_windowed = current_voltage * current_window

    # Apply inter-acquisition convolution-based filtering if requested
    if filter_type in ['convolve', 'both']:
        current_voltage_filtered = convolve(current_voltage_windowed, previous_voltage, mode='same')
    elif filter_type in ['savgol']:
        current_voltage_filtered = savgol_filter(current_voltage_windowed, sg_window, sg_order)
    else:
        current_voltage_filtered = current_voltage_windowed

    # Calculate sampling parameters
    current_sampling_period = current_time[1] - current_time[0]
    current_sampling_frequency = 1.0 / current_sampling_period
    current_n_samples = len(current_voltage)

    # Compute FFT
    current_fft_result = np.fft.fft(current_voltage_filtered)
    current_fft_freq = np.fft.fftfreq(current_n_samples, current_sampling_period)

    # Calculate magnitude spectrum
    current_magnitude = 2.0 * np.abs(current_fft_result) / current_n_samples

    # Apply threshold filter if requested
    if filter_type in ['threshold', 'both']:
        current_fft_result_filtered = apply_threshold_filter(current_fft_result, current_magnitude, threshold_percent)
        current_magnitude_filtered = 2.0 * np.abs(current_fft_result_filtered) / current_n_samples
    else:
        current_magnitude_filtered = current_magnitude

    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot original signal
    ax1.plot(current_time * 1000, current_voltage, 'b-', label='Original Signal')
    ax1.plot(current_time * 1000, current_voltage_windowed, 'g-', label='Windowed Signal')
    ax1.plot(current_time * 1000, current_voltage_filtered, 'r-', label='Filtered Signal')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Time Domain Signal')
    ax1.grid(True)
    ax1.legend()

    # Plot full FFT magnitude spectrum
    positive_freq_mask = current_fft_freq >= 0
    ax2.semilogy(current_fft_freq[positive_freq_mask], current_magnitude[positive_freq_mask], 'b-',
                 label='Original FFT')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (log scale)')
    ax2.set_title('Full Frequency Spectrum')
    ax2.set_xscale('log')
    ax2.set(xlim=[1e4, 1.5e5])
    ax2.set(ylim=[1e-4, 1e-2])
    # ax2.set(xlim=[1e3, 200000])

    ax2.grid(True)
    ax2.legend()

    # Plot filtered FFT magnitude spectrum
    if filter_type in ['threshold', 'both']:
        ax3.plot(current_fft_freq[positive_freq_mask], 10 * np.log10(current_magnitude_filtered[positive_freq_mask]),
                 'r-',
                 label=f'Filtered FFT (threshold: {threshold_percent}%)')
    else:
        ax3.plot(current_fft_freq[positive_freq_mask], 10 * np.log10(current_magnitude_filtered[positive_freq_mask]),
                 'r-',
                 label='Filtered FFT')
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Magnitude (log scale)')
    ax3.set_title('Filtered Frequency Spectrum')
    ax3.grid(True)
    # ax3.set_xscale('log')
    # ax3.set(xlim=[1e3, 1e6])
    # ax3.set(ylim=[2e-4, 1e-2])
    ax3.set(ylim=[-40, -25])
    ax3.set(xlim=[1e3, 150000])
    ax3.legend()

    # Make layout tight and display plot
    plt.tight_layout()
    plt.show()

    return current_fft_freq[positive_freq_mask], current_magnitude_filtered[positive_freq_mask]


def move_oscilloscope_cursor(cursor_number: int = 1, cursor_type: str = 'X', position: str = '0.206') -> None:
    """
    Moves a specified cursor to a designated position on a Tektronix oscilloscope.

    Args:
        cursor_number (int): The cursor number (1 or 2) to be moved.
        cursor_type (str): The type of cursor to move ('X' for horizontal, 'Y' for vertical).
        position (float): The position to move the cursor to. This should be within the valid range for the cursor type.

    Raises:
        ValueError: If the cursor number is not 1 or 2, or if the cursor type is neither 'X' nor 'Y'.
        Exception: If there is an error in communication with the oscilloscope.

    Returns:
        None: This function does not return a value but moves the cursor on the oscilloscope.
    """
    # Validate cursor number and type
    if cursor_number not in [1, 2]:
        raise ValueError("Cursor number must be 1 or 2")
    if cursor_type.upper() not in ['X', 'Y']:
        raise ValueError("Cursor type must be 'X' for horizontal or 'Y' for vertical")

    try:
        # Construct and send the SCPI command to move the cursor
        command = f'CURSor:SCREEN:{cursor_type.upper()}POSITION{cursor_number} {position}'
        osc.write(command)
        print(f"Cursor {cursor_number} moved to position {position} on {cursor_type.upper()} axis.")
    except Exception as e:
        print(f"Failed to move cursor due to: {str(e)}")


def on_off_signal_generator_switch() -> int:
    """
    Toggles the on/off status of a signal generator and returns its original status.

    Queries the signal generator for its current on/off status, then toggles it.
    The status '1' indicates the generator is currently ON, and '0' indicates it is OFF.
    The function sends a command to toggle the state based on the current status
    and prints the action being taken to the console.

    Returns:
        int: The original on/off status of the signal generator before toggling (1 for ON, 0 for OFF).

    Raises:
        ValueError: If the signal generator returns an unknown status.
    """
    # Query the signal generator to get the current ON/OFF status.
    signal_generator_on_off_status = signal_Generator.query(r'OUTput1?')

    # Print the current status of the signal generator to the console.
    print(f"Current Signal Generator status: {signal_generator_on_off_status}")

    # Check the first character of the status returned by the query.
    if signal_generator_on_off_status[0] == '1':
        # The generator is currently ON, send a command to turn it OFF.
        signal_Generator.write("OUTput1 0")
        print("Turning OFF Signal Generator")
    elif signal_generator_on_off_status[0] == '0':
        # The generator is currently OFF, send a command to turn it ON.
        signal_Generator.write("OUTput1 1")
        print("Turning ON Signal Generator")
    else:
        # If the status is neither '1' nor '0', it's unknown and an error is raised.
        raise ValueError("Signal Generator ON/OFF status unknown")

    # Return the numeric version of the original status (1 or 0).
    return int(signal_generator_on_off_status)


def query_signal_generator() -> str:
    """Queries the current status of the signal generator."""
    return signal_Generator.query(r'OUTput1?')[0]


def toggle_signal_generator() -> None:
    """Toggles the signal generator's state based on the current status."""
    current_status = query_signal_generator()
    new_status = '0' if current_status[0] == '1' else '1'
    signal_Generator.write(f"OUTput1 {new_status}")
    print(f"Signal Generator turned {'ON' if new_status == '1' else 'OFF'}")


def load_pattern(
        filename: str = r'filtered_1000pulses_100us_pulse_dc20%_30Vtop_24Vhold_40V_triangle_filtered.arb') -> None:
    signal_Generator.write('*RST')
    signal_Generator.write(r'MMEMory:CDIRectory "USB:\PATTERNS\"')
    print(signal_Generator.query('SYSTem:ERRor?'))
    print("Directory switched")
    signal_Generator.write(fr'MMEMory:LOAD:DATA "USB:\PATTERNS\{filename}"')
    signal_Generator.write(fr'FUNC:ARB "USB:\PATTERNS\{filename}"')
    signal_Generator.write(r'FUNC ARB')

    # print(signal_Generator.query('SYSTem:ERRor?'))
    signal_Generator.write("OUTPut1 1")
    signal_Generator.write("VOLTage:OFFSET 0")


def test_1() -> None:
    try:
        signal_Generator.write("OUTput 1")
        os.chdir(path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling")
        time.sleep(5)
        ch4 = get_curve_cycling(channel=4)
        ch2 = get_curve_cycling(channel=2)
        # print(ch4[:, 1])
        # mems_characteristics = extract_data_v3(rf_detector_channel=ch4, v_bias_channel=ch2)
        # signal_Generator.write("OUTput 1")
        # print(mems_characteristics)
        # for keys, values in mems_characteristics.items():
        #     print(f'{keys} = {values} \n')
        signal_Generator.write("OUTput 0")
        # mems_characteristics.clear()

        wf = save_waveform(waveform_ch4=ch4, waveform_ch2=ch2, filename='test')
        ax = plt.subplot(111)

        ax.plot(wf[2], wf[0], label='1')
        ax.plot(wf[2], wf[1], label='1')
        plt.show()
    except:
        print("error")
        signal_Generator.write("OUTput 0")


if __name__ == "__main__":
    load_pattern()
