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

matplotlib.ticker.ScalarFormatter(useOffset=True, useMathText=True)

# import RsInstrument as rs

# This code is dated to 15/02/24

os.system('cls')

path = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'

os.chdir('{}'.format(path))
# Opening resource manager
rm = pyvisa.ResourceManager()

sig_gen = sig_gen_init()
osc = osc_init()


# zva = zva_init()
# powermeter = powermeter_init()
# rf_gen = rf_gen_init()


def sig_gen_opc_control(function):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = sig_gen.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper


@sig_gen_opc_control
def bias_voltage(voltage='10'):
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
    sig_gen.write("SOURce:VOLTage:OFFSET 0")
    sig_gen.write("SOURce:VOLTage:LOW 0")
    sig_gen.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = sig_gen.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(sig_gen.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage


@sig_gen_opc_control
def bias_pullin(voltage):
    # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20]
    # because of the amplifier
    voltage_at_sig_gen = float(voltage) / 20
    print(voltage_at_sig_gen)
    sig_gen.write("SOURce:VOLTage:OFFSET 0")
    sig_gen.write("SOURce:VOLTage:LOW -{}".format(voltage_at_sig_gen))
    sig_gen.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = sig_gen.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(sig_gen.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage


@sig_gen_opc_control
def ramp_width(width=100):  # Set ramp length (µs) in pull down voltage test
    frequency_gen = 1 / (4 * float(width * 10 ** (-6)))
    print(f"Ramp frequency = {frequency_gen / 1e3} kHz")
    try:
        sig_gen.write('SOURce1:FUNCtion:RAMP:SYMMetry 50')  # selecting pulse function
        sig_gen.write('FREQuency {}'.format(frequency_gen))
        sig_gen.write('OUTPut 1')  # Turn on output
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            sig_gen.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except pyvisa.VisaIOError:
        print('Signal Generator VisaIOError')


def set_f_start(f_start=1):  # Set start frequency function
    # f_converted = f_start+'E'+'9'
    f_converted = f_start * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STAR {}".format(f_converted, type='E'))
    print("F_start is set to {} GHz \n".format(f_start))


def set_fstop(fstop=10):  # Set stop frequency function
    # f_converted = f_stop+'E'+'9' # string
    f_converted = fstop * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STOP {}".format(f_converted, type='E'))
    print("Fstop is set to {} GHz \n".format(fstop))


def number_of_points(points=501):  # Set Number of points function
    zva.write_str_with_opc("SWEep:POINts {}".format(points))
    print("Number of points set to {} points \n".format(points))


def set_pulse_width(width=10):  # Set the pulse width as a function of the VNA sweep time in S parameter measurement
    try:
        width_converted = width  # float
        print("Pulse width: {} s".format(width_converted, type='E', precision=2), end='\n')
        sig_gen.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(width_converted, type='E'))
        pri = sig_gen.query("SOURce1:FUNCtion:PULSe:PERiod?").split('\n')[0]
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


def sig_gen_set_output_log():  # Get error log of the signal generator
    a = r"Bias voltage set to {} V".format(float(sig_gen.query("SOURce:VOLTage?")) * 20)
    b = r"Pulse width is set to {} s".format(float(sig_gen.query("SOURce1:FUNCtion:PULSe:WIDTh?")))
    c = r"prf set to {} Hz".format(1 / float(sig_gen.query("SOURce1:FUNCtion:PULSe:PERiod?")))
    return a + '\n' + b + '\n' + c


def set_prf(prf):  # Set pulse repetition frequency
    pri = 1 / prf
    width = sig_gen.query("SOURce1:FUNCtion:PULSe:WIDTh?").split('\n')[0]
    print(f"Pulse width = {width} s")
    if float(width) > pri:
        print("Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri))
        error_log = "Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri)
    else:
        sig_gen.write("SOURce1:FUNCtion:PULSe:PERiod {}".format(pri))
        error_log = f"Pulse width set to {width}"
    return error_log


def set_zva(start=1, stop=10, points=501):  # Configure the ZVA with all the input parameters entered in the GUI
    set_f_start(start)
    print("Fstart is set to {} GHz \n".format(float(zva.query("FREQ:STARt?")) / (10 ** 9)))
    set_fstop(stop)
    print("Fstop is set to {} GHz \n".format(float(zva.query("FREQ:STOP?")) / (10 ** 9)))
    number_of_points(points)
    print("Number of points set to {} points \n".format(zva.query("SWEep:POINts?")))


def sig_gen_set_output_ramp_log():  # Set the ramp parameters in pull down voltage test
    a = r"Ramp voltage is set to {} V".format(
        float(sig_gen.query("SOURce:VOLTage?")) * (20 / 2))  # Gain amplifier = 20, Vcc/2
    b = r"Ramp duration is set to {} µs".format(10 ** 6 * 1 / (4 * float(sig_gen.query("FREQuency?"))))
    return a + '\n' + b


def zva_set_output_log():  # Get error log of the ZVA
    a = r"Fstart is set to {} GHz".format(float(zva.query("FREQ:STARt?")) / (10 ** 9))
    b = r"Fstop is set to {} GHz".format(float(zva.query("FREQ:STOP?")) / (10 ** 9))
    c = r"Number of points set to {} points".format(zva.query("SWEep:POINts?"))
    return a + '\n' + b + '\n' + c


def trigger_measurement_zva():  # Trigger the ZVA using the signal generator
    # zva.write_str_with_opc('*TRG')
    zva.write_str_with_opc('TRIGger:SOURce EXTernal')
    sig_gen.write('TRIG')
    sig_gen.query('*OPC?')
    time.sleep(2)
    print("Signal generator sent Trigger pulse \n")


def comprep_zva():  # Preparation of the communication
    zva.visa_timeout = 5000
    zva.opc_timeout = 5000
    zva.instrument_status_checking = True
    zva.clear_status()
    print("Comms are ready")


def close_zva():  # Close ZVA VISA Session
    # Close VISA Session
    zva.close()
    print("ZVA session closed \n")


def close_sig_gen():  # Close signal generator VISA Session
    sig_gen.close()
    print("Signal generator session closed \n")


def close_osc():  # Close oscilloscope VISA Session
    osc.close()
    print("Oscilloscope session closed \n")


def close_rf_gen():  # Close rf generator VISA Session
    rf_gen.close()
    print("RF generator session closed \n")


def close_powermeter():  # Close powermeter VISA Session
    powermeter.close()
    print("Powermeter session closed \n")


def close_all_ressources():  # Close all ressources VISA Session
    # print(instr_list)
    # if instr_list == ():
    #     pass
    # else:
    #     close_zva()
    #     close_sig_gen()
    #     close_osc()
    #     close_rf_gen()
    #     close_powermeter()
    print("All ressources have been closed \n")


def saves3p(filename):
    # directory = r"C:\Rohde&Schwarz\Nwa\Traces"
    directory = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'
    try:  # Setting directory to directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s3p' , LOGPhase, 1,2,3".format(filename))
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
    finally:
        zva.visa_timeout = 1000


def saves2p(filename):
    # Directory = r"C:\Rohde&Schwarz\Nwa\Traces"
    directory = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'
    try:  # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s2p' , LOGPhase, 1,2".format(filename))
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


def saves1p(filename):
    # Directory = r"C:\Rohde&Schwarz\Nwa\Traces"
    directory = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'
    try:  # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe 'Trc1', '{}.s1p'".format(filename))
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


def file_get(filename, zva_file_dir=dir_and_var_declaration.ZVA_File_Dir,
             pc_file_dir=dir_and_var_declaration.PC_File_Dir,
             extension='s2p'):
    print(r"ZVA File directory: {}\{}".format(zva_file_dir, filename), end='\n')
    print(r"PC File Directory: {}\{}".format(pc_file_dir, filename), end='\n')
    if extension == 's3p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}\{}.s3p".format(zva_file_dir, filename),
                                                r"{}\{}.s3p".format(pc_file_dir, filename), append_to_pc_file=False)
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
                                                r"{}\{}.s2p".format(pc_file_dir, filename), append_to_pc_file=False)
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
                                                r"{}\{}.s1p".format(pc_file_dir, filename), append_to_pc_file=False)
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


def setup_zva_with_rst(ip):
    # Resetting the ZNA67
    zva = RsInstrument('{}'.format(ip), id_query=True, reset=True)
    zva.opc_query_after_write = True
    zva.write_str_with_opc(r"MMEMory:LOAD:STATe 1, 'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\SPST.znxml'")
    zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    print('ZVA Reset complete!', end='\n')


def setup_sig_gen_ramp_with_rst(ip):
    sig_gen = rm.open_resource('{}'.format(ip))
    sig_gen.write('MMEM:LOAD:STAT "RAMP.sta"')  # Load STATE_4
    error_log = sig_gen.query('SYSTem:ERRor?')
    print('Signal generator Reset complete!', end='\n')


def configuration_sig_gen(frequence_gen=150, amplitude=1, pulse_width=0.001333):
    try:
        sig_gen.write('*RST')
        # print('Reset status A33500B: {}\n'.format(sig_gen.query('*OPC?')))
        # LOADING MEM state 4
        sig_gen.write('MMEM:LOAD:STAT "STATE_4.sta"')  # Load STATE_4
        sig_gen.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        sig_gen.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write("SOURce:VOLTage:LOW 0")
        sig_gen.write("SOURce:VOLTage:HIGH 2.5")
        sig_gen.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        sig_gen.write('OUTPut 1')  # turn on output
        sig_gen.write('OUTPut:SYNC:MODE NORMal')
        sig_gen.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequence_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            sig_gen.write('FREQuency {}'.format(frequence_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')


def configuration_sig_gen_snp(frequence_gen=150, amplitude=1, pulse_width=0.001333):
    try:
        sig_gen.write('*RST')
        # print('Reset status A33500B: {}\n'.format(sig_gen.query('*OPC?')))
        # LOADING MEM state 4
        sig_gen.write('MMEM:LOAD:STAT "STATE_pulse.sta"')  # Load STATE_4
        sig_gen.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        sig_gen.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write("SOURce:VOLTage:LOW 0")
        sig_gen.write("SOURce:VOLTage:HIGH 2.5")
        sig_gen.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        sig_gen.write('OUTPut 1')  # turn on output
        sig_gen.write('OUTPut:SYNC:MODE NORMal')
        sig_gen.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequence_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            sig_gen.write('FREQuency {}'.format(frequence_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')


def configuration_sig_gen_pullin(ramp_length=50, amplitude=1):  # 50µs ramp_length
    ramp_frequency = 1 / (4 * ramp_length * 10 ** (-6))
    ramp_period = (4 * ramp_length * 10 ** (-6))
    print(ramp_period)
    try:
        sig_gen.write('MMEM:LOAD:STAT "STATE_4.sta"')  # Load STATE_4
        sig_gen.write('FREQuency {}'.format(1))
        sig_gen.write('SOURce1:FUNCtion RAMP')  # selecting pulse function
        sig_gen.write('FUNCtion:RAMP:SYMMetry 50')
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write("SOURce:VOLTage:LOW -{}".format(amplitude))
        sig_gen.write("SOURce:VOLTage:HIGH {}".format(amplitude))
        sig_gen.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        sig_gen.write('OUTPut 1')  # turn on output
        sig_gen.write('OUTPut:SYNC:MODE NORMal')
        sig_gen.write('FREQuency {}'.format(ramp_frequency))
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        osc.write('HORizontal:MODE:SCAle {}'.format(ramp_period / 5))
        if int(error) != 0:
            # frequence_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            sig_gen.write('FREQuency {}'.format(ramp_frequency))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')
    return (ramp_period)


def configuration_pullin(ramp_length=50, amplitude=1, rf_frequency=10):
    configuration_sig_gen_pullin(ramp_length=50, amplitude=1)
    setup_rf_synth(frequency=rf_frequency, power=-10, power_lim=-6)


def triggered_data_acquisition(filename=r'default', zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                               pc_file_dir=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P",
                               file_format='s2p'):
    try:
        sweep_time: str = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        print("Sweep time is set to {} s\n".format(sweep_time), end='\n')
        # sig_gen.write("FUNC:PULSe:PER {}").format(float(10 * sweep_time))
        # sig_gen.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(float(sweep_time * 2)))
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
        sig_gen.write('SOURce1:FREQuency {}'.format(1 / (10 * float(sweep_time))))
        print('An error occured in triggered_data_acquisition PROCESS \n')
        print('prf may be incompatible \n')
        print_error_log()


def print_error_log():
    # Requête des erreurs
    error_log_sig_gen = sig_gen.query('SYSTem:ERRor?')
    error_log_sig_zva = zva.query_str('SYSTem:ERRor?')
    error_string_sig_gen = error_log_sig_gen.split(",")[1]
    error_string_zva = error_log_sig_zva.split(",")[1]
    print('SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen, end='\n')
    print('ZVA ERROR LOG:\n' + error_string_zva, end='\n')
    a = 'SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen
    b = 'ZVA ERROR LOG:\n' + error_string_zva
    return (a + '\n' + b)


def setup_osc():
    osc.write("*RST")
    osc.write('RECALL:SETUP "C:/Users/Tek_Local_Admin/Desktop/fiab/setup-pullin-AN.set"')
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


def setup_rf_synth(frequency=10, power=-10, power_lim=-6):  # GHz, 6 dBm is max linear input for a non distorted pulse
    rf_gen.write('SOUR:POW:LIM:AMPL -1'.format(power_lim))
    rf_gen.write('OUTP ON')
    rf_gen.write('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_gen.write('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_gen.write('OUTP ON')


def get_channel_info(channel=4):
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
        print("get_channel_info function ended")
    except:
        print("Unable to Get channel info")
    return channel_info


def get_curve(channel=4):
    print(f"Acquiring curver {channel}")
    curve_data = np.empty(shape=1)
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        ref_index = trigger_ref * acquisition_length  # get the 1st index of the ramp using trigger ref position and
        # acquisition length because ramp starts at trigger
        ramp_frequency = float(sig_gen.query('FREQuency?'))  # adapt the length of the ramp with frequency

        # Determine the length of the triangle and the number of samples in the triangle
        ramp_length = 1 / (4 * ramp_frequency)
        ramp_period = 1 / (ramp_frequency)
        print("ramp periode is = {}".format(ramp_period), end='\n')
        # rf_gen.write("SOURce:PULM:WIDTh {}".format(ramp_period * 2))
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        number_of_samples = sample_rate * ramp_period  # Number of samples in the triangles
        print("number of samples in the triangle is {}".format(number_of_samples))
        print("ref_index is {}".format(ref_index))
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
        print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)[
               int(ref_index):int(ref_index) + int(number_of_samples) + 1500]
        print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        print("get_curve function ended")
    except:
        print("Unable to acquire Data")
    return curve_data


def measure_pull_down_voltage(filename=r'default'):
    # try:
    sig_gen.write('TRIG')
    curve_det = get_curve(channel=4)
    curve_bias = get_curve(channel=2)
    t = curve_det[:, 1]
    rf_detector = curve_det[:, 0]
    v_bias = curve_bias[:, 0]
    file_array = np.vstack((v_bias, rf_detector, t))
    print(file_array[:, 0], end='\n')
    np.savetxt('{}.txt'.format(filename), file_array, delimiter=',', newline='\n',
               header='#V_bias(V),rf_detector (V), time (s)')
    # except:
    #     print("Unable to acquire Data")


def power_test_sequence(start=-30, stop=-20, step=1, sleep_duration=1):
    power_input_amp = list(np.arange(int(start), int(stop), float(step)))
    power_input_dut_avg = []
    power_output_dut_avg = []

    rf_gen.write('OUTP OFF')
    rf_gen.write('SOUR:POW:LEVEL:IMM:AMPL -60')
    rf_gen.write('OUTP ON')
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')

    for power_level in power_input_amp:
        rf_gen.write('SOUR:POW:LEVEL:IMM:AMPL {}'.format(power_level))
        time.sleep(sleep_duration)
        sig_gen.write('TRIG')
        power_input_dut_avg.append(float(powermeter.query('FETC2?')))
        power_output_dut_avg.append(float(powermeter.query('FETC1?')))

    rf_gen.write('OUTP OFF')
    print("Sweep ended")
    return power_input_dut_avg, power_output_dut_avg


def setup_power_test_sequence(pulse_width=100, delay=30):  # in us
    # Configuration sig_gen
    sig_gen.write('*RST')
    sig_gen.write("MMEM:LOAD:STATe '100_us_PULSE.sta'")  # 100_us_PULSE.sta
    # Configuration rf_gen
    rf_gen.write('*RST')
    rf_gen.write("*RCL 4")  # 100_us_PULSE.sta
    # Configuration powermeter
    powermeter.write('*RST')
    powermeter.write('*RCL 1')
    rf_gen.write("SOURCe1:PULM:WIDTh {}".format(float(pulse_width) * 10 ** (-6)))
    rf_gen.write("SOURCe1:PULM:DELay {}".format(float(delay) * 10 ** (-6)))

    delay_pulse_rf_gen = float(rf_gen.query("SOURCe1:PULM:DELay?"))
    width_pulse_rf_gen = float(rf_gen.query("SOURCe1:PULM:WIDTh?"))

    print(delay_pulse_rf_gen)
    print(width_pulse_rf_gen)


def connect():
    machines = ['ZNA67-101810', 'A-33521B-00526', 'DPO5054-C011738', 'rssmb100a179766', '192.168.0.30']
    machine_names = ['zva', 'sig_gen', 'osc', 'rf_gen', 'powermeter']
    # machine_dict = {zip(machine_names, machines)}
    # for machine, machine_name in zip(machines, machine_names):
    #     try:
    #         if machine_name == 'zva':
    #             machine_dict[machine_name]=RsInstrument(f'TCPIP0::{machine}::inst0::INSTR', id_query=True, reset=False)
    #         else:
    #             machine_dict[machine_name]=rm.open_resource(f'TCPIP0::{machine}::inst0::INSTR')
    #     except pyvisa.errors.VisaIOError:
    #         print(f"Machine {machine_name} ({machine}) is offline. Skipping...")

    zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
    sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
    osc = rm.open_resource('TCPIP0::DPO5054-C011738::inst0::INSTR')
    rf_gen = RsInstrument('TCPIP0::rssmb100a179766::inst0::INSTR')
    powermeter = rm.open_resource('TCPIP0::A-N1912A-00589::inst0::INSTR')
    return zva, sig_gen, osc, rf_gen, powermeter


def send_trig():
    sig_gen.write('TRIG')
    sig_gen.query('*OPC?')
    return print('trigger sent')


def get_curve_cycling(channel=4):
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
        print(time_base)
        data = np.zeros((acquisition_length, 2))
        data[:, 0] = (curve - y_offset) * y_scale
        data[:, 1] = time
        print("get_curve function ended")
    except:
        print("Unable to acquire Data")
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
    :param delay: Input delay of the oscilloscope to position at the end of the cycling wavefrm
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

    # plt.plot(ramp_voltage_curve, label='ramp_voltage_curve')
    # plt.plot(negative_ramp_voltage_curve, label='negative_ramp_voltage_curve')
    # plt.plot(ramp_voltage_ascent, label='ramp_voltage_ascent')
    # plt.plot(ramp_voltage_descent, label='ramp_voltage_descent')
    # plt.plot(ramp_voltage_descent_minus, label='ramp_voltage_descent_minus')
    # plt.plot(ramp_voltage_ascent_minus, label='ramp_voltage_ascent_minus')
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


def cycling_sequence(number_of_cycles=1e9, number_of_pulses_in_wf=1000, filename='test', wf_duration=0.205, events=100,
                     df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling"):
    """
    Cycling test sequence outputs MEMS characteristics during the tested duration, results are
    :param df_path: File path
    :param number_of_cycles: Total number of cycles in sequence duration
    :param number_of_pulses_in_wf: Number of pulses in waveform
    :param filename: Test sequence output filename
    :param wf_duration: Total duration of the waveform in the sequence
    :param events: Number of trigger events before oscilloscope performs an acquisition
    :return: File containing a dataframe
    """
    number_of_triggers_before_acq = events  # number of  B trigger events in A -> B sequence
    number_of_triggered_acquisitions = int(number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq))
    cycles = pd.Series(
        np.arange(start=0, stop=number_of_cycles, step=number_of_pulses_in_wf * number_of_triggers_before_acq),
        name="cycles")

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
    print(f"Number of triggers required :{number_of_triggered_acquisitions}")
    print("Starting number of triggers = {}\n".format(starting_number_of_acq))
    print("Number of remaining cycles = {}\n".format(number_of_cycles))
    print(f"Estimated test duration: {format_duration(test_duration)}")

    file_df = pd.DataFrame(columns=["vpullin_plus", "vpullin_minus", "Vpullout_plus", "Vpullout_minus",
                                    "iso_ascent", "iso_descent_minus", "switching_time",
                                    "amplitude_variation", "release_time"])
    for column in file_df.columns:
        file_df[column] = 0

    count = starting_number_of_acq

    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
        remaining_count = number_of_cycles - (new_value - starting_number_of_acq) * number_of_pulses_in_wf * events
        print(f"Remaining cycle count = {remaining_count}")
        if count == new_value:
            time.sleep(1)
            print("Waiting for trigger...", end='\n')
        else:
            count = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            ch_4_detector = get_curve_cycling(channel=4)
            ch_2_bias = get_curve_cycling(channel=2)
            data = extract_data(rf_detector_channel=ch_4_detector, v_bias_channel=ch_2_bias)
            file_df = pd.concat([file_df, data], join="outer")
            print(file_df)
            file_df["cycle count"] = cycles
    file_df.to_csv(path_or_buf=f"{df_path}'\'{filename}.csv")
    print("Test complete!")


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


def load_config(pc_file=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\s1p_setup.znxml',
                inst_file=r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\placeholder.znxml'):
    zva.reset()
    # Transfer the file to the instrument
    zva.send_file_from_pc_to_instrument(pc_file, inst_file)
    # Load the transferred setup
    zva.write_str_with_opc(f'MMEM:LOAD:STAT 1,"{inst_file}"')
    print(f"{pc_file} configuration loaded to:\n{inst_file}", end='\n')


def calculate_pullin_out_voltage_measurement(v_bias,
                                             v_log_amp):  # same function as in display implemented in measurement

    # Acquiring the indexes that correspond to both positive and negative bias triangles
    # the indexes are extracted by slicing voltages (for positive bias) > 2V and <-2 V (for negative bias)
    positive_bias = np.extract((v_bias > 2), v_bias)
    negative_bias = np.extract((v_bias < -2), v_bias)

    # Position of the first positive bias index along v_bias array
    first_index_pos = np.where(v_bias == positive_bias[0])[0]

    # Position of the first negative bias index along v_bias array
    first_index_neg = np.where(v_bias == negative_bias[0])[0]
    # Position of the last negative bias index along v_bias array
    last_index_neg = np.where(v_bias == negative_bias[-1])[0]
    # Calculating the max and min indexes in both casses
    max_positive_bias_index = np.argmax(positive_bias)
    min_positive_bias_index = 0
    max_negative_bias_index = 0
    min_negative_bias_index = np.argmin(negative_bias)

    # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
    positive_ascent = positive_bias[0:max_positive_bias_index]
    positive_descent = positive_bias[max_positive_bias_index:len(positive_bias)]

    # Calculating normalized isolation factor
    normalize_iso = np.max(3 * v_log_amp[first_index_pos[0]:max_positive_bias_index] / 0.040)

    iso_ascent = 3 * v_log_amp[
                     first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / 0.040 - normalize_iso
    iso_max_ascent = np.min(iso_ascent)

    iso_descent = 3 * v_log_amp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
        positive_bias)] / 0.040 - normalize_iso
    iso_min_descent = np.min(iso_descent)
    # ==============================================================================
    # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
    # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
    pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
    Vpullin = round(positive_bias[pullin_index_pos], ndigits=2)

    tenpercent_iso = round(0.1 * iso_min_descent, ndigits=2)
    ninetypercent_iso = round(0.9 * iso_max_ascent, ndigits=2)

    pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
    Vpullout = round(positive_bias[max_positive_bias_index + pullout_index_pos], ndigits=2)

    # ==============================================================================
    # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
    negative_descent = negative_bias[0:min_negative_bias_index]
    negative_ascent = negative_bias[min_negative_bias_index:len(negative_bias)]

    # Calculating normalized isolation factor
    normalized_iso_minus = np.max(3 * v_log_amp[first_index_neg[0]:first_index_neg[
                                                                       0] + min_negative_bias_index] / 0.040)  # This is extracted from the detector V/dB characteristics

    iso_descent_minus = 3 * v_log_amp[first_index_neg[0]:first_index_neg[
                                                             0] + min_negative_bias_index] / 0.040 - normalized_iso_minus
    iso_min_descent_minus = np.min(iso_descent_minus)

    iso_ascent_minus = 3 * v_log_amp[first_index_neg[0] + min_negative_bias_index:last_index_neg[
        0]] / 0.040 - normalized_iso_minus
    iso_min_ascent = np.min(iso_ascent_minus)

    # Calculation Vpull in negative as isolation passing below 90% max isolation in dB mark (downwards)
    # Calculation Vpull out negative as isolation passing above 10% off isolation in dB mark (upwards)
    pullin_index_minus = int(np.where(iso_descent_minus <= 0.9 * iso_min_descent)[0][0])
    Vpullin_minus = round(negative_bias[pullin_index_minus], ndigits=2)

    tenpercent_iso_ascent = round(0.1 * iso_min_ascent, ndigits=2)
    ninetypercent_iso_descent = round(0.9 * iso_min_descent, ndigits=2)

    pullout_index_minus = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent)[0][0])
    Vpullout_minus = round(negative_bias[min_negative_bias_index + pullout_index_minus], ndigits=2)
    # print(f"""Vpullin = {Vpullin} | Isolation measured = {}\nVpullout = {Vpullout} | Isolation measured = {} \nVpullin_minus = {} |
    # Isolation measured = {}\nVpullout_minus = {} | Isolation measured = {} \n'.format(Vpullin, ninetypercent_iso,
    # Vpullout, tenpercent_iso, Vpullin_minus, ninetypercent_iso_descent, Vpullout_minus, tenpercent_iso_ascent"""))


def plot_function(list_x, list_y):
    for x, y in zip(list_x, list_y):
        plt.plot(x, y, label=f'{y}')
        plt.legend()
        plt.show()


def extract_data_v2(rf_detector_channel, v_bias_channel, ramp_start=0.20383, ramp_stop=0.20437, ramp_start_minus=0.2046,
                    ramp_stop_minus=0.20519, delay=0.2, conversion_coeff=0.047):
    """
    Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
    Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
    cycling sequence.
    :param rf_detector_channel: Detector channel array
    :param v_bias_channel: Bias channel array
    :param ramp_start: Starting time of the positive ramp
    :param ramp_stop: End time of the positive ramp
    :param ramp_start_minus: Starting time of the negative ramp
    :param ramp_stop_minus: End time of the negative ramp
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
        relative_amplitude = amplitude_t0 - float(osc.query('MEASUrement:MEAS4:VALue?'))

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


def sig_gen_cycling_config():
    sig_gen.write("*RST")
    time.sleep(1)
    sig_gen.write('MMEM:LOAD:STAT "CYCLE_2kHz.sta"')
    time.sleep(1)
    sig_gen.write("*OPC?")
    print("Signal Generator cycling config")

def osc_cycling_config():
    osc.write('RECALL:SETUP "C:/Users/Tek_Local_Admin/Desktop/fiab/setup-cycling-AN3.set"')
    print("Oscilloscope cycling config")
    sig_gen.write("*OPC?")

# sig_gen.write('OUTPut 1')

# sig_gen_cycling_config()

# starting_number_of_acquisitions = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
# counter = starting_number_of_acquisitions
# while counter == starting_number_of_acquisitions:
#     counter = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
#     time.sleep(1)
#
# ch_2 = get_curve_cycling(2)
# ch_4 = get_curve_cycling(4)
#
# df = extract_data_v2(rf_detector_channel=ch_4, v_bias_channel=ch_2)
#
# sig_gen.write('OUTPut 0')
#
# for column, value in zip(df.columns, df.values[0]):
#     print(f"{column} = {value}")

# try:
#     cycling_sequence(number_of_cycles=1e6)
# except:
#     print("Cycling sequence error", end='\n')
#     osc.close()
#     sig_gen.write('OUTPut 0')
# sig_gen.write('OUTPut 0')
# zva = zva_init()
# print(format_duration(3600*24))
# powermeter = powermeter_init()
# rf_gen = rf_gen_init()
