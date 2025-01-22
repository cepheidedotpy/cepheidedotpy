import numpy as np
import time
import matplotlib
import matplotlib.artist
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.axes._axes as axis

import os
import pyvisa
from pyvisa import constants
import socket

from matplotlib.ticker import ScalarFormatter

matplotlib.ticker.ScalarFormatter(useOffset=True, useMathText=True)

import RsInstrument as rs
from RsInstrument import *

os.system('cls')

path = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'
cwd = os.chdir('{}'.format(path))

instr_list = RsInstrument.list_resources('?*', 'ni')
rm = pyvisa.ResourceManager()

PC_File_Dir = r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data"
ZVA_File_Dir = r"C:\Rohde&Schwarz\Nwa\Calibration\RecallSets"

RsInstrument.assert_minimum_version('1.5.0')

zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
osc = rm.open_resource('TCPIP0::169.254.242.241::inst0::INSTR')
# rf_Generator = RsInstrument('TCPIP0::192.168.0.5::inst0::INSTR')
# powermeter = rm.open_resource('TCPIP0::192.168.0.83::inst0::INSTR')

idn = zva.query_str('*IDN?')
idn2 = sig_gen.query('*IDN?')
idn3 = osc.query('*IDN?')
# idn4 = rf_Generator.query('*IDN?')

print(idn, end='\n')
print(idn2, end='\n')
print(idn3, end='\n')
# print(idn4, end='\n')


def get_channel_info(channel=4):
    try:
        osc.write('Data:Source CH{}'.format(channel))
        osc.write('Data:ENCdg ASCII')
        x_scale = osc.query('HORizontal:MODE:SCAle?')
        x_divisions = osc.query('HORizontal:DIVisions?')
        acquisition_length = osc.query("HORizontal:ACQLENGTH?")

        print("acquisition_length = {} samples".format(acquisition_length))

        sweep_duration = float(x_scale) * float(x_divisions)
        print("sweep duration = {} s\n".format(sweep_duration))
        y_scale = osc.query_ascii_values('WFMOutpre:Ymult?')
        y_offset = osc.query_ascii_values('WFMOutpre:YOFf?')
        channel_info = dict([('y_offset', y_offset), ('x_scale', x_scale), ('y_scale', y_scale),
                             ('x_divisions', x_divisions), ('sweep_duration', sweep_duration),
                             ('acquisition_length', acquisition_length)])
        print("get_channel_info function ended")
    except:
        print("Unable to Get channel info")
        channel_info = {}
    return (channel_info)


def get_curve_cycling(channel=4):  # Acquire waveform data of set channel, functions returns an array  with the time base and values at the specified channel
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        curve = np.array(osc.query('CURV?').split(','), dtype=float)

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

    pullout_index_pos = int(np.where(iso_descent >= 0.1*iso_min_descent)[0][0])
    # print(pullout_index_pos)
    Vpullout = round(ramp_voltage_descent[pullout_index_pos], ndigits=2)

    # return (iso_max_ascent, iso_min_descent, t0_ramp, t0_plus_rampwidth, ramp_voltage_ascent, ramp_voltage_descent, iso_ascent, iso_descent, Vpullin, Vpullout)
    mems_characteristics = dict([('iso_ascent',iso_ascent),('iso_descent',iso_descent),('Vpullin',Vpullin), ('Vpullout',Vpullout),
                                 ('ninetypercent_iso',ninetypercent_iso), ('tenpercent_iso', tenpercent_iso), ('_100percent_iso', _100percent_iso)])
    return mems_characteristics
    # pass

#
# signal_Generator.write('TRIG')
# curve_det = get_curve_cycling(channel=4)
# curve_bias = get_curve_cycling(channel=2)
#
# mems_characteristics = extract_data(rf_detector_channel=curve_det, v_bias_channel=curve_bias, ramp_start=0.0253,
#                                 ramp_stop=0.026)
# sw_time = switching_time()
# print("Last pulse switching time = {} s".format(sw_time))
#
# fig_s3p, ax_s3p = plt.subplots(nrows=1, ncols=1)
#
# ax_s3p.figure(mems_characteristics['iso_ascent'], label = 'ascent')
# ax_s3p.figure(mems_characteristics['iso_descent'], label = 'descent')
#
# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0, 4))
# ax_s3p.xaxis.set_major_formatter(formatter)
# ax_s3p.grid(True)
# ax_s3p.set_title('Oscilloscope measurement')
# plt.legend()
# plt.show()
