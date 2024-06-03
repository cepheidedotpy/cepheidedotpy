from RsInstrument import *
import pyvisa
from RsInstrument import RsInstrument

# These are the file names of the different configurations of the ZVA67
zva_s1p_config = 's1p_setup.znxml'
zva_s2p_config = 's2p_setup.znxml'
zva_s3p_config = 's3p_setup.znxml'

# PC File Path on our PC
pc_file_s1p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s1p_config)
pc_file_s2p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s2p_config)
pc_file_s3p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s3p_config)

# This is the placeholder file used in the instrument to copy the configuration of the ZVA from the PC
instrument_file = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\placeholder.znxml'
PC_File_Dir = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'
ZVA_File_Dir = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'

rm = pyvisa.ResourceManager()

signal_generator_ip = r'TCPIP0::A-33521B-00526::inst0::INSTR'
zva_ip = r'TCPIP0::ZNA67-101810::inst0::INSTR'
rf_generator_ip = r'TCPIP0::rssmb100a179766::inst0::INSTR'
powermeter_ip = r'TCPIP0::192.168.0.83::inst0::INSTR'
oscilloscope_ip = r'TCPIP0::DPO5054-C011738::inst0::INSTR'


def zva_init(tcpip_address: str = r'TCPIP0::ZNA67-101810::inst0::INSTR') -> RsInstrument | None:
    _id = r'Vector Network Analyser'
    error = False
    zva = None
    try:
        zva = RsInstrument(tcpip_address, id_query=False, reset=False)
    except TimeoutException as e:
        error = True
        print(e.args[0])
        print('Timeout Error in ZVA')
    except StatusException as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    except ResourceError as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    except RsInstrException as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("VNA Connected")
        return zva


def sig_gen_init(tcpip_address: str = r'TCPIP0::A-33521B-00526::inst0::INSTR') -> pyvisa.Resource | None:
    _id = "Signal Generator"
    error = False
    sig_gen = None
    try:
        sig_gen = rm.open_resource(tcpip_address)
    except pyvisa.VisaIOError as e:
        error = True
        print(e.args[0])
        print(f'Error {e} occurred in signal generator')
    except pyvisa.VisaTypeError as e:
        error = True
        print(e.args[0])
        print(f'Error {e} occurred occurred in signal generator')
    except ResourceError as e:
        error = True
        print(e.args[0])
        print('Resource Error in signal generator')
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred occurred in signal generator')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Signal generator Connected")
        return sig_gen


def osc_init(tcpip_address: str = r'TCPIP0::DPO5054-C011738::inst0::INSTR') -> pyvisa.Resource | None:
    _id = "Oscilloscope"
    error = False
    osc = None
    try:
        osc = rm.open_resource(tcpip_address)
    except pyvisa.VisaIOError as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    except pyvisa.VisaTypeError as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Oscilloscope Connected")
        return osc


def rf_gen_init(tcpip_address: str = r'TCPIP0::rssmb100a179766::inst0::INSTR') -> RsInstrument | None:
    _id = "RF Generator"
    error = False
    rf_gen = None
    try:
        rf_gen = RsInstrument(tcpip_address, id_query=False, reset=False)
    except TimeoutException as e:
        error = True
        print(e.args[0])
        print('Timeout Error in RF generator')
    except StatusException as e:
        error = True
        print(e.args[0])
        print('Status Error in RF generator')
    except ResourceError as e:
        error = True
        print(e.args[0])
        print('Resource Error in RF generator')
    except RsInstrException as e:
        error = True
        print(e.args[0])
        print('Exception Error  in RF generator')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("RF generator Connected")
        return rf_gen


def powermeter_init(tcpip_address=r'TCPIP0::192.168.0.83::inst0::INSTR'):
    _id = "Powermeter"
    error = False
    powermeter = None
    try:
        powermeter = rm.open_resource(tcpip_address)
    except pyvisa.VisaIOError as e:
        error = True
        print(f'Error {e} occurred')
    except pyvisa.VisaTypeError as e:
        error = True
        print(f'Error {e} occurred')
    except ResourceError as e:
        error = True
        print(e.args[0])
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Powermeter Connected")
        return powermeter

# zva_init()
# sig_gen_init()
# osc_init()
# powermeter_init()
# rf_gen_init()
