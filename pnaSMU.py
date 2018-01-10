# -*- coding: utf-8 -*-
"""
Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

import visa
import numpy as np
import time
import AgilentPNAXUtils as pnaUtils
import Keithley2400 as k2400

    
def sParmMeas(voltages, smus, pna, sPorts, savedir, localsavedir, testname, delay, pnaparms = None):
    '''
    PNA measurement with up to three SMU voltage sweeps
    
    TODO: Implement base class for measurements.
    
    Parameters:
    -----------
    voltages : list
        A list containing the three voltage values/sweeps for the SMUs
    smus : list
        A list of the connected SMUs
    pna
        The connected PNA
    sParms : list
        The S-parameters to be measured
    savedir : string
        The directory on the PNA in which to save snp files.
    testname : string
    pnaparms : dict
        A dictionary containing test parameters to set on the pna.
        
    Returns:
    ----------
    N/A
    
    '''
   
    # explicitly redefine smus as local vars for readability 
    gate = smus[0]
    drain = smus[1]
    drive = smus[2]
    for x in smus: x.setVoltage(0)
    
    for vg in voltages[0]:
        for vd in voltages[1]:
            for vdr in voltages[2]:
                gate.setVoltage(vg)
                drain.setVoltage(vd)
                drive.setVoltage(vdr)                

                print("SMU Voltages set to the following - Gate: " + str(vg) + " Drain: " + str(vd) + " Drive: " + str(vdr))
                print("Now Sleeping for {} sec to allow system to equilibriate".format(str(delay)))
                for i in range(delay):
                    time.sleep(1)
                    if i%10 == 0:
                        print(str(i) + "/" + str(delay))

                testname2 = '{}_Vg{}Vd{}Vdr{}'.format(testname,str(vg).replace('.','_'),str(vd).replace('.','_'),str(vdr).replace('.','_'))
                pna.sMeas(sPorts, savedir, localsavedir, testname2, pnaparms)
    for x in smus: x.outputOff

    
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
    Vdr = [1.0, 4.0] # V_DRIVE
    Vg = [2.0] # V_GATE
    Vd = [3.0] # V_DRAIN
    compliance = 0.100 #Amps IE 105uA = 0.000105 
    maxVoltage = 100 #Maximum expected voltage to be used 
    ports = '1,2' # string containing comma separated port numbers to be used
    delayTime = 20 #Time between setting SMU voltage and measurement in seconds


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
    voltages = [Vg,Vd,Vdr]
    
    pna = pnaUtils.AgilentPNAx('TCPIP0::192.168.1.1::inst0::INSTR')
    gate = k2400.Keithley2400('GPIB1::24::INSTR')
    drain = k2400.Keithley2400('GPIB1::25::INSTR')
    drive = k2400.Keithley2400('GPIB1::26::INSTR')
    
    smus = [gate,drain,drive]
    
    for x in smus: x.smuSetup(maxVoltage, compliance)
    pna.pnaInitSetup()
    try:
      sParmMeas(voltages, smus, pna, ports, savedir, localsavedir, testname, delayTime, pnaTestParms)
    except visa.VisaIOError as e:
        print(e.args)
        pna.outputOff   
        for x in smus:
          x.outputOff
         
    
    for x in smus: x.disconnect()
    pna.disconnect()
    
    exit
    
if __name__ == "__main__":
    main()