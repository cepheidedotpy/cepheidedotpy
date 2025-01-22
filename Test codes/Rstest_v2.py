import numpy as np
import time

import matplotlib
import matplotlib.artist
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.axes._axes as axis
import csv
import os
import pyvisa
from pyvisa import constants
import socket

from matplotlib.ticker import ScalarFormatter

matplotlib.ticker.ScalarFormatter(useOffset=True, useMathText=True)

import RsInstrument as rs
from RsInstrument import *

# os.system('cls')

# path = r'C:\Users\I5bis\Desktop\Python DIR\Measurement Dir'
path = r'E:\Codes\GUI Summit 11K'

cwd = os.chdir('{}'.format(path))

instr_list = RsInstrument.list_resources('?*', 'ni')
rm = pyvisa.ResourceManager()

# pc_file_dir = r"\\L319368\Users\I5bis\Desktop\Python DIR\Measurement Dir"
# zva_file_dir = r"C:\Rohde&Schwarz\Nwa\Calibration\RecallSets"
PC_File_Dir = r"E:\Codes\GUI Summit 11K"
ZVA_File_Dir = r"E:\Codes\GUI Summit 11K"

def handle_event(ressource, event, user_handle):
    ressouce.called = True
    print(f"Handled event {event.event_type} on {ressource} \n")
    pass

def bias_voltage(voltage): # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20] because of the amplifier
    voltage_at_sig_gen = float(voltage)/20
    print(voltage_at_sig_gen)
    sig_gen.write("SOURce:VOLTage:OFFSET 0")
    sig_gen.write("SOURce:VOLTage:LOW 0")
    sig_gen.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = sig_gen.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(sig_gen.query("SOURce:VOLTage?"))*20
    print(set_voltage)
    return(set_voltage)

def bias_pullin(voltage): # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20] because of the amplifier
    voltage_at_sig_gen = float(voltage)/20
    print(voltage_at_sig_gen)
    sig_gen.write("SOURce:VOLTage:OFFSET 0")
    sig_gen.write("SOURce:VOLTage:LOW -{}".format(voltage_at_sig_gen))
    sig_gen.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = sig_gen.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(sig_gen.query("SOURce:VOLTage?"))*20
    print(set_voltage)
    return(set_voltage)

def ramp_width(width): # Set ramp length (µs) in pull down voltage test
    frequence_gen = 1/(4*float(width*10**(-6)))
    print(frequence_gen)
    try:
        sig_gen.write('SOURce1:FUNCtion:RAMP:SYMMetry 50') # selecting pulse function
        sig_gen.write('FREQuency {}'.format(frequence_gen))
        # signal_Generator.write("SOURce:VOLTage:OFFSET 0")
        # signal_Generator.write("SOURce:VOLTage:LOW -1")
        # signal_Generator.write("SOURce:VOLTage:HIGH 1")
        # signal_Generator.write('SOURce:BURSt:NCYCles MINimum') # set burst cycles to 0
        sig_gen.write('OUTPut 1') # turn on output
        # signal_Generator.write('OUTPut:SYNC:MODE NORMal')
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            sig_gen.write('FREQuency {}'.format(frequence_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')

def set_fstart(fstart=1): # Set start frequency function
    # fconverted = f_start+'E'+'9'
    fconverted = fstart*10**9 # float
    zva.write_str_with_opc("FREQ:STAR {}".format(fconverted, type='E'))
    print("Fstart is set to {} GHz \n".format(fstart))

def set_fstop(fstop=10): # Set stop frequency function
    # fconverted = f_stop+'E'+'9' # string
    fconverted = fstop*10**9 # float
    zva.write_str_with_opc("FREQ:STOP {}".format(fconverted, type='E'))
    print("Fstop is set to {} GHz \n".format(fstop))

def Number_of_points(points=501): # Set Number of points function
    zva.write_str_with_opc("SWEep:POINts {}".format(points))
    print("Number of points set to {} points \n".format(points))

def set_pulse_width(width): # Set the pulse width as a function of the VNA sweep time in S parameter measurement
    try:
        width_converted = width # float
        print("Pulse width: {} s".format(width_converted, type='E', precision=2), end='\n')
        sig_gen.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(width_converted, type='E'))
        PRI = sig_gen.query("SOURce1:FUNCtion:PULSe:PERiod?").split('\n')[0]
        # print(f"PRI={PRI} s")
        PRF = 1/float(PRI)
        print(f"prf={PRF} Hz\nPRI={PRI} s")
        sweep_time = zva.query_str_with_opc("SWEep:TIME?")
        print(f"Sweep time={sweep_time} s")
        if (float(sweep_time) > width_converted):
            print("Pulse width is too small for a complete sweep measurement", end='\n')
            PRF_req = 1/float(sweep_time)
            print("Minimum pulse length is: {}\nRequired prf={} Hz".format(sweep_time, PRF_req), end='\n')
    finally:
        print_error_log()

def sig_gen_set_output_log(): # Get error log of the signal generator
    a = r"Bias voltage set to {} V".format(float(sig_gen.query("SOURce:VOLTage?"))*20)
    b = r"Pulse width is set to {} s".format(float(sig_gen.query("SOURce1:FUNCtion:PULSe:WIDTh?")))
    c = r"prf set to {} Hz".format(1/float(sig_gen.query("SOURce1:FUNCtion:PULSe:PERiod?")))
    return(a + '\n' + b + '\n' + c)

def set_PRF(PRF): # Set pulse repetition frequency
    PRI = 1/PRF
    width = sig_gen.query("SOURce1:FUNCtion:PULSe:WIDTh?").split('\n')[0]
    print(f"Pulse width = {width} s")
    if float(width) > PRI:
        print("Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(PRI))
        error_log = "Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(PRI)
    else:
        sig_gen.write("SOURce1:FUNCtion:PULSe:PERiod {}".format(PRI))
        error_log = f"Pulse width set to {width}"
    return(error_log)

def set_zva(start=1, stop=10, points=501): # Configure the ZVA with all the input parameters entered in the GUI
    set_fstart(start)
    print("Fstart is set to {} GHz \n".format(float(zva.query("FREQ:STARt?"))/(10**9)))
    set_fstop(stop)
    print("Fstop is set to {} GHz \n".format(float(zva.query("FREQ:STOP?"))/(10**9)))
    Number_of_points(points)
    print("Number of points set to {} points \n".format(zva.query("SWEep:POINts?")))

def sig_gen_set_output_ramp_log(): # Set the ramp parameters in pull down voltage test
    a = r"Ramp voltage is set to {} V".format(float(sig_gen.query("SOURce:VOLTage?"))*(20/2))# Gain amplifier = 20, Vcc/2
    b = r"Ramp duration is set to {} µs".format(10**6*1/(4*float(sig_gen.query("FREQuency?"))))
    return(a + '\n' + b)

def zva_set_output_log(): # Get error log of the ZVA
    a = r"Fstart is set to {} GHz".format(float(zva.query("FREQ:STARt?"))/(10**9))
    b = r"Fstop is set to {} GHz".format(float(zva.query("FREQ:STOP?"))/(10**9))
    c = r"Number of points set to {} points".format(zva.query("SWEep:POINts?"))
    return(a + '\n' + b + '\n' + c)

def trigger_measurement_zva(): # Trigger the ZVA using the signal generator
    zva.write_str_with_opc('*TRG')
    zva.write_str_with_opc('TRIGger:SOURce EXTernal')
    sig_gen.write('TRIG')
    sig_gen.query('*OPC?')
    print("Signal generator sent Trigger pulse \n")

def comprep_zva(): # Preparation of the communication
    zva.visa_timeout = 5000
    zva.opc_timeout = 5000
    zva.instrument_status_checking = True
    zva.clear_status()
    print("Comms are ready")

def close_zva(): # Close ZVA VISA Session
# Close VISA Session
    zva.close()
    print("ZVA session closed \n")

def close_sig_gen(): # Close signal generator VISA Session
    sig_gen.close()
    print("Signal generator session closed \n")

def close_osc(): # Close oscilloscope VISA Session
    osc.close()
    print("Oscilloscope session closed \n")

def close_rf_gen(): # Close rf generator VISA Session
    rf_gen.close()
    print("RF generator session closed \n")

def close_powermeter(): # Close powermeter VISA Session
    powermeter.close()
    print("Powermeter session closed \n")

def close_all_ressources(): # Close all ressources VISA Session
    close_zva()
    close_sig_gen()
    close_osc()
    close_rf_gen()
    close_powermeter()
    print("All ressources have been closed \n")

def saves3p(filename):
    Directory = r"C:\Rohde&Schwarz\Nwa\Traces"
    try: # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(Directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s3p' , LOGPhase, 1,2,3".format(filename))
        print(r"s3p file saved in ZVA at {}".format(Directory), end='\n')
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
        zva.visa_timeout = 5000

def saves2p(filename):
    Directory = r"C:\Rohde&Schwarz\Nwa\Traces"
    try: # Setting directory to Directory variable then performing a file save without external trigger
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(Directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s2p' , LOGPhase, 1,2".format(filename))
        print(r"sp file saved in ZVA at {}".format(Directory), end='\n')
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
        zva.visa_timeout = 5000

def file_get(filename, ZVA_File_Dir, PC_File_Dir, extension = 's2p'):
    print("ZVA File directory: {}\{} \n".format(ZVA_File_Dir, filename))
    print("PC File Directory: {}\{} \n".format(PC_File_Dir, filename))

    if extension == 's3p':
        try:
            zva.read_file_from_instrument_to_pc("{}\{}.s3p".format(ZVA_File_Dir, filename), "{}\{}.s3p".format(PC_File_Dir, filename), append_to_pc_file=False)
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
            zva.visa_timeout = 5000
    if extension == 's2p':
        try:
            zva.read_file_from_instrument_to_pc("{}\{}.s2p".format(ZVA_File_Dir, filename), "{}\{}.s2p".format(PC_File_Dir, filename), append_to_pc_file=False)
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
            zva.visa_timeout = 5000

def setup_zva_with_rst(ip):
    zva = RsInstrument('{}'.format(ip), id_query=True, reset=True)
    zva.opc_query_after_write = True
    zva.write_str_with_opc("MMEMory:LOAD 'CalSetAN_15112022.zvx'")
    zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    print('ZVA Reset complete!', end='\n')

def setup_sig_gen_ramp_with_rst(ip):
    sig_gen = rm.open_resource('{}'.format(ip))
    sig_gen.write('MMEM:LOAD:STAT "RAMP.sta"') # Load STATE_4
    error_log = sig_gen.query('SYSTem:ERRor?')
    print('Signal generator Reset complete!', end='\n')

def configuration_sig_gen(frequence_gen=150, amplitude=1 , pulse_width=0.001333):
    try:
        sig_gen.write('*RST')
        # print('Reset status A33500B: {}\n'.format(signal_Generator.query('*OPC?')))
        # LOADING MEM state 4
        sig_gen.write('MMEM:LOAD:STAT "STATE_4.sta"') # Load STATE_4
        sig_gen.write('FREQuency {}'.format(1)) # set a default frequency before programming to avoid errors
        sig_gen.write('SOURce1:FUNCtion PULSe') # selecting pulse function
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write("SOURce:VOLTage:LOW 0")
        sig_gen.write("SOURce:VOLTage:HIGH 2.5")
        sig_gen.write('SOURce:BURSt:NCYCles MINimum') # set burst cycles to 0
        sig_gen.write('OUTPut 1') # turn on output
        sig_gen.write('OUTPut:SYNC:MODE NORMal')
        sig_gen.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequence_gen = 1/(10*pulse_width)
            print(error, error_log, sep='\n', end='\n')
            sig_gen.write('FREQuency {}'.format(frequence_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')

def configuration_sig_gen_pullin(ramp_length = 50, amplitude=1): #50µs ramp_length
    ramp_frequency = 1/(4*ramp_length*10**(-6))
    ramp_period = (4*ramp_length*10**(-6))
    print(ramp_period)
    try:
        sig_gen.write('MMEM:LOAD:STAT "STATE_4.sta"') # Load STATE_4
        sig_gen.write('FREQuency {}'.format(1))
        sig_gen.write('SOURce1:FUNCtion RAMP') # selecting pulse function
        sig_gen.write('FUNCtion:RAMP:SYMMetry 50')
        sig_gen.write("SOURce:VOLTage:OFFSET 0")
        sig_gen.write("SOURce:VOLTage:LOW -{}".format(amplitude))
        sig_gen.write("SOURce:VOLTage:HIGH {}".format(amplitude))
        sig_gen.write('SOURce:BURSt:NCYCles MINimum') # set burst cycles to 0
        sig_gen.write('OUTPut 1') # turn on output
        sig_gen.write('OUTPut:SYNC:MODE NORMal')
        sig_gen.write('FREQuency {}'.format(ramp_frequency))
        error_log = sig_gen.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        osc.write('HORizontal:MODE:SCAle {}'.format(ramp_period/5))
        if int(error) != 0:
            frequence_gen = 1/(10*pulse_width)
            print(error, error_log, sep='\n', end='\n')
            sig_gen.write('FREQuency {}'.format(ramp_frequency))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')
    return(ramp_period)

def configuration_pullin(ramp_length = 50, amplitude=1, rf_frequency=10):
    configuration_sig_gen_pullin(ramp_length = 50, amplitude=1)
    setup_rf_synth(frequency=rf_frequency, power=-10, power_lim=-6)

def triggered_data_acquisition(filename=r'default', ZVA_File_Dir=r"C:\Rohde&Schwarz\Nwa\Traces", PC_File_Dir=r"X:\Affaire\Mesure\Mesures Labo RF", file_format='s2p'):
    try:
        sweep_time = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        print("Sweep time is set to {} \n".format(sweep_time), end='\n')
        sig_gen.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(sweep_time))
        trigger_measurement_zva()
        time.sleep(1)
        if file_format == 's3p':
            saves3p(filename)
            file_get(filename, ZVA_File_Dir, PC_File_Dir, extension='s3p')
        elif file_format == 's2p':
            saves2p(filename)
            file_get(filename, ZVA_File_Dir, PC_File_Dir)
        print_error_log()
    except:
        sweep_time = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        sig_gen.write('FREQuency {}'.format(1/(2*float(sweep_time))))
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
    return(a + '\n' + b)

def setup_osc():
    osc.write("*RST")
    osc.write('RECALL:SETUP "C:/Users/Tek_Local_Admin/Desktop/fiab/setup-pullin-AN.set"')
    acquisition_length = osc.query("HORizontal:ACQLENGTH?")
    record_length = osc.query("HORizontal:MODE:RECOrdlength?")
    x_unit = osc.query("HORizontal:MAIn:UNIts:STRing?")
    x_scale = osc.query("HORizontal:MODE:SCAle?")
    trigger_ref = int(osc.query('HORizontal:MAIn:DELay:POSition?'))
    ch2_y_scale = osc.query("CH2:SCAle?") # Scale of channel 2
    ch4_y_scale = osc.query("CH4:SCAle?") # Scale of channel 4
    setup_info = dict([('x_unit', x_unit), ('x_scale', x_scale), ('ch2_y_scale', ch2_y_scale), ('ch4_y_scale', ch4_y_scale), ('acquisition_length', acquisition_length), ('trig_ref', trig_ref)])
    return(setup_info)

def setup_rf_synth(frequency=10, power=-10, power_lim=-6): #GHz, 6 dBm is max linear input for a non distorted pulse
    rf_gen.write('SOUR:POW:LIM:AMPL -1'.format(power_lim))
    rf_gen.write('OUTP ON')
    rf_gen.write('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_gen.write('SOUR:FREQ {} GHz; LEV {}'.format(frequency,power))
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
        y_offset= osc.query_ascii_values('WFMOutpre:YOFf?')
        channel_info = dict([('y_offset', y_offset),('x_scale', x_scale), ('y_scale', y_scale),
        ('x_divisions', x_divisions), ('sweep_duration', sweep_duration), ('acquisition_length', acquisition_length)])
        print("get_channel_info function ended")
    except:
        print("Unable to Get channel info")
    return(channel_info)

def get_curve(channel=4):
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?")) # get number of samples
        print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))

        trigger_ref = float(osc.query('HORizontal:MAIn:DELay:POSition?'))/100 # get trigger position in percentage of samples (default is 10%)
        ref_index = trigger_ref*acquisition_length # get the 1st index of the ramp using trigger ref position and acquisition length because ramp starts at trigger
        ramp_frequency = float(sig_gen.query('FREQuency?')) # adapt the length of the ramp with frequency

        # Determine the length of the triangle and the number of samples in the triangle
        ramp_length = 1/(4*ramp_frequency)
        ramp_period = 1/(ramp_frequency)
        print("ramp periode is = {}".format(ramp_period), end='\n')
        rf_gen.write("SOURce:PULM:WIDTh {}".format(ramp_period*2))
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        number_of_samples = sample_rate*ramp_period # Number of samples in the triangles
        print("number of samples in the triangle is {}".format(number_of_samples))
        print("ref_index is {}".format(ref_index))
        # data_truncated is the truncated data. This data  is cropped from ref index to 1500 samples after the end of the triangle
        data_truncated = np.zeros((acquisition_length,2))[int(ref_index):int(ref_index)+int(number_of_samples)+1500] # 1500 samples added to make sure the triangle is complete
        data = data_truncated
        # data = np.zeros((acquisition_length,2))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        # curve = np.array(osc.query('CURV?').split(','), dtype=float)
        curve = np.array(osc.query('CURV?').split(','), dtype=float)[int(ref_index):int(ref_index)+int(number_of_samples)+1500]
        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        time_base = info['sweep_duration']/acquisition_length
        print(time_base)
        time = np.arange(0,info['sweep_duration'],time_base)[int(ref_index):int(ref_index)+int(number_of_samples)+1500]
        print("duration of sweep = {} s\n".format(info['sweep_duration']))
        data[:,0] = (curve-y_offset)*y_scale
        data[:,1] = time[:]
        print("get_curve function ended")
    except:
        print("Unable to acquire Data")
    return(data)

def measure_pull_down_voltage(filename=r'default'):
    try:
        sig_gen.write('TRIG')
        curve_det = get_curve(channel=4)
        curve_bias = get_curve(channel=2)
        t = curve_det[:,1]
        rf_detector = curve_det[:,0]
        v_bias = curve_bias[:,0]
        file_array = np.vstack((v_bias, rf_detector, t))
        print(file_array[:,0], end='\n')
        np.savetxt('{}.txt'.format(filename), file_array, delimiter=',', newline='\n', header= '#V_bias(V),rf_detector (V), time (s)')
    except:
        print("Unable to acquire Data")

def power_test_sequence(start=-30, stop=-20, step=1, sleep_duration=1):
    power_input_amp = list(np.arange(int(start),int(stop),float(step)))

    power_input_dut_avg = []
    power_output_dut_avg = []

    rf_gen.write('OUTP OFF')
    rf_gen.write('SOUR:POW:LEVEL:IMM:AMPL -60')
    rf_gen.write('OUTP ON')
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')

    for i in range(len(key_list)):
        rf_gen.write('SOUR:POW:LEVEL:IMM:AMPL {}'.format(power_input_amp[i]))
        time.sleep(sleep_duration)
        sig_gen.write('TRIG')
        power_input_dut_avg.append(float(powermeter.query('FETC2?')))
        power_output_dut_avg.append(float(powermeter.query('FETC1?')))

    rf_gen.write('OUTP OFF')
    print("Sweep ended")
    return(power_input_dut_avg, power_output_dut_avg)

def setup_power_test_sequence(pulse_width = 100, delay = 30): #in us
# Configuration signal_Generator
    sig_gen.write('*RST')
    sig_gen.write("MMEM:LOAD:STATe '100_us_PULSE.sta'") # 100_us_PULSE.sta
# Configuration rf_Generator
    rf_gen.write('*RST')
    rf_gen.write("*RCL 4") # 100_us_PULSE.sta
# Configuration powermeter
    powermeter.write('*RST')
    powermeter.write('*RCL 1')
    rf_gen.write("SOURCe1:PULM:WIDTh {}".format(float(pulse_width)*10**(-6)))
    rf_gen.write("SOURCe1:PULM:DELay {}".format(float(delay)*10**(-6)))

    delay_pulse_rf_gen = float(rf_gen.query("SOURCe1:PULM:DELay?"))
    width_pulse_rf_gen = float(rf_gen.query("SOURCe1:PULM:WIDTh?"))

    print(delay_pulse_rf_gen)
    print(width_pulse_rf_gen)

def Connect():
    # zva = RsInstrument('TCPIP0::192.168.0.63::inst0::INSTR', id_query=False, reset=False)
    sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
    # signal_Generator = rm.open_resource('TCPIP0:192.168.0.168::inst0::INSTR')
    osc = rm.open_resource('TCPIP0::169.254.242.241::inst0::INSTR')
    rf_gen = RsInstrument('TCPIP0::192.168.0.5::inst0::INSTR')
    powermeter = rm.open_resource('TCPIP0::192.168.0.30::inst0::INSTR')

def send_trig():
    sig_gen.write('TRIG')
    sig_gen.query('*OPC?')
    pass

def get_curve_cycling(channel=4):  # Acquire waveform data of set channel, functions returns an array  with the time base and values at the specified channel
    try:
        osc.write('Data:Source CH{}'.format(channel))
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))# get number of samples
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query('HORizontal:MAIn:DELay:POSition?')) / 100 
        # get trigger position in percentage of samples (default is 10%)
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
    return (data)

def switching_time():
    sw_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    return sw_time

def extract_data(rf_detector_channel, v_bias_channel, ramp_start=0.0253, ramp_stop=0.0261):
    # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
    # Assign the different curves to variables
    t = rf_detector_channel[:, 1]
    rf_detector_curve = rf_detector_channel[:, 0]
    v_bias_curve = v_bias_channel[:, 0]

    # Define a ramp voltage curve to calculate pull in and pull out curve. This is done by time gating using ramp_start and ramp_stop
    t0_ramp = list(np.where(t > ramp_start))[0][0]
    t0_plus_rampwidth = list(np.where(t < ramp_stop))[0][-1]

    # From the time gating we extract the ramp voltage curve ascent and descent
    ramp_voltage_curve = v_bias_curve[t0_ramp:t0_plus_rampwidth]

    # We then calculate the index corresponding to the Max voltage of our ramp
    max_positive_bias_index = np.argmax(ramp_voltage_curve)

    # Then comes the definition of an ascent and descent portion of the curves
    ramp_voltage_ascent = ramp_voltage_curve[:max_positive_bias_index]
    ramp_voltage_descent = ramp_voltage_curve[max_positive_bias_index:]

    # Calculating the normalization value for the isolation
    normalized_isolation = np.max(3 * rf_detector_curve[t0_ramp: t0_plus_rampwidth] / 0.040)

    iso_ascent = 3 * rf_detector_curve[
                     t0_ramp: np.argmax(v_bias_curve)] / 0.040 - normalized_isolation
    iso_max_ascent = np.min(iso_ascent)
    # print('isolation on ascent = {} dB'.format(iso_max_ascent))
    iso_descent = 3 * rf_detector_curve[np.argmax(v_bias_curve):t0_plus_rampwidth] / 0.040 - normalized_isolation
    iso_min_descent = np.min(iso_descent)
    # print('isolation on descent = {} dB'.format(iso_min_descent))

    #==============================================================================
    # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
    # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
    pullin_index_pos = int(np.where(iso_ascent <= 0.9*iso_max_ascent)[0][0])
    Vpullin = round(ramp_voltage_ascent[pullin_index_pos], ndigits=2)

    tenpercent_iso = round(0.1*iso_min_descent, ndigits=2)
    ninetypercent_iso = round(0.9*iso_max_ascent, ndigits=2)
    _100percent_iso = iso_min_descent
    pullout_index_pos = int(np.where(iso_descent >= 0.1*iso_min_descent)[0][0])
    # print(pullout_index_pos)
    Vpullout = round(ramp_voltage_descent[pullout_index_pos], ndigits=2)

    # return (iso_max_ascent, iso_min_descent, t0_ramp, t0_plus_rampwidth, ramp_voltage_ascent, ramp_voltage_descent, iso_ascent, iso_descent, Vpullin, Vpullout)
    mems_characteristics = dict([('iso_ascent',iso_ascent),('iso_descent',iso_descent),('Vpullin',Vpullin), ('Vpullout',Vpullout),
                                 ('ninetypercent_iso',ninetypercent_iso), ('tenpercent_iso', tenpercent_iso), ('_100percent_iso', _100percent_iso)])
    return mems_characteristics
    # pass

def cycling_sequence(number_of_cycles = 200, number_of_pulses_in_wf=20, filename='test', wf_duration = 0.02):
    number_of_triggered_acquisitions = int(number_of_cycles/number_of_pulses_in_wf)
    cycles = list(np.arange(start=0, stop=number_of_cycles, step=20))
    test_duration = wf_duration*number_of_cycles/60/60
    print("Number of triggers to be used = {}".format(number_of_triggered_acquisitions))
    print("Estimated time {} h".format(test_duration))
    pullin = []
    pullout = []
    isolation = []
    sw_time = []

    for n in range(number_of_triggered_acquisitions):
        send_trig()
        # time.sleep(1)
        Ch_4_detector = get_curve_cycling(channel=4)
        print(osc.query('*OPC?'))

        Ch_2_bias = get_curve_cycling(channel=2)
        print(osc.query('*OPC?'))
        data = extract_data(rf_detector_channel=Ch_4_detector, v_bias_channel=Ch_2_bias)
        st = switching_time()
        print("pull in voltage :")
        print(pullin)
        print("pull out voltage :")
        print(pullout)
        print("isolation @pullin Voltage :")
        print(isolation)
        print("switching time voltage :")
        print(sw_time)

        pullin.append(data['Vpullin'])
        pullout.append(data['Vpullout'])
        isolation.append(data['_100percent_iso'])
        sw_time.append(st)

    cycling_data = list((cycles, pullin, pullout, isolation, sw_time))
    try:
        with open("{}.csv".format(filename), mode='x') as csvfile:
            # spamwriter = csv.writer(csvfile, delimiter = "\n", lineterminator = "\n")
            fieldnames = ['cycles', 'Vpull_in(V)', 'Vpullout (V)', 'Isolation (dB)', 'sw_time (s)']
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames, dialect='excel')
            writer.writeheader()
            writer.writerow({'cycles': cycles, 'Vpull_in(V)': cycling_data[0], 'Vpullout (V)' : cycling_data[1], 'Isolation (dB)' : cycling_data[2], 'sw_time (s)' : cycling_data[3]})
    except:
        with open("{}.csv".format(time.asctime().replace(' ','_').replace(':','-')), mode='x') as csvfile:
            # spamwriter = csv.writer(csvfile, delimiter = "\n", lineterminator = "\n")
            fieldnames = ['cycles', 'Vpull_in(V)', 'Vpullout (V)', 'Isolation (dB)', 'sw_time (s)']
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames, dialect='excel')
            writer.writeheader()
            writer.writerow({'cycles': cycles, 'Vpull_in(V)': cycling_data[0], 'Vpullout (V)' : cycling_data[1], 'Isolation (dB)' : cycling_data[2], 'sw_time (s)' : cycling_data[3]})

    return cycling_data
    # np.savetxt(fname='test.txt',X=cycling_data, delimiter='\n', newline='\n', header='RF MEMS Reference = test\nCycling_data',footer='END')
    # print('Cycle is Finished')

def  online_mode():
    try:
    # Main-------------------------------------------------------------------------------------------------------------------------
        RsInstrument.assert_minimum_version('1.5.0')

        os.chdir(r"C:\Users\I5bis\Desktop\Python DIR\Measurement Dir")

        print("Connected instrument list: \n")
    # for ressouce in list(ressources.values()):
    #     print(ressouce, end='\n')

        zva = RsInstrument('TCPIP0::192.168.0.63::inst0::INSTR', id_query=False, reset=False)
        sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
        osc = rm.open_resource('TCPIP0::169.254.242.241::inst0::INSTR')
        rf_gen = RsInstrument('TCPIP0::192.168.0.5::inst0::INSTR')
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

def display_figure():
    fig, ax =  plt.subplots(nrows=1, ncols=1)
    # Display -----------------------------------------------------------------------------------------------------------------------
    ax.plot(t, rf_detector, label='rf_detector')
    ax.plot(t, v_bias, label='v_bias')
    ax.plot(v_bias, rf_detector, label='rf_detector vs v_bias')

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,4))
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True)
    ax.set_title('Oscilloscope measurement')
    plt.legend()
    plt.show()