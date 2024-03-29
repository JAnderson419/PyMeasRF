# -*- coding: utf-8 -*-
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

import visa
from context import pymeasrf
import pymeasrf.AgilentPNAXUtils as pnaUtils
    
def main():
    '''
    Carry out PNA S-parameter measurements with varying DC biases.
    
    This code currently connects with three Keithley 2400 Source-Measure Units
    (SMUs), which are used to apply DC biases to the device under test (DUT).
    Voltages can be specified in two ways:
        1. A manually-defined list of numbers 
            ex) [1.0,1.1,1.2]
        2. A numpy array created via a function like linspace
            ex) np.linspace(0,2,11) - voltages from 0 to 2, 11pts, linear space
    
    Measurements are carried out using a Keysight PNA (N5225a). Several
    measurement parameters can be changed by the end user including:
        -ifBandwidth: IF (receiver) bandwidth. Allowable values include:
            1,          2,    3,    5,    7,
            10,   15,   20,   30,   50,   70,
            100,  150,  200,  300,  500,  700,
            1k,   1.5k, 2k,   3k,   5k,   7k,
            10k,  15k,  20k,  30k,  50k,  70k,
            100k,       200k, 280k, 360k, 600k
        -centerFreq & spanFreq: frequency range of measurement. Max: 50 GHz
        -nPoints: number of points in measurement (1 to 32,001)
    '''

    ############################# User specified test Parameters ###################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ports = '1,3,4' # string containing comma separated port numbers to be used

    testname = 'Test2' # name snp files will be saved as current file name format is as follows:
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    savedir = 'C:\\Documents\\pyvisa' # Directory where snp files will be saved on PNA
    ############################# END User specified test Parameters ###############################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    pnaTestParms = {
#                    'ifBandwidth' : '50', # Hz, see above for options
#                    'startFreq' : 30E9, #Hz # use only if code does cal
#                    'stopFreq' : 33E9, #Hz # use only if code does cal
#                    'nPoints' : 201,
#                    'avgMode' : 'SWEEP', # POINT or SWEEP
#                    'nAvg' : 1
                    }
#    pnaTestParms=None
    localsavedir = 'C:\\Test' # Does nothing currently
    
    pna = pnaUtils.AgilentPNAx('TCPIP0::192.168.1.1::inst0::INSTR')

    pna.pnaInitSetup()
    try:
      pna.sMeas(ports, savedir, localsavedir, testname, pnaTestParms)
    except visa.VisaIOError as e:
        print(e.args)
        pna.outputOff()  

         
    pna.disconnect()   
    exit
    
if __name__ == "__main__":
    main()