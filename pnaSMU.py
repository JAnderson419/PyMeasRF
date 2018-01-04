# -*- coding: utf-8 -*-
"""
Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

import visa
import numpy as np
import shutil
import time

def connect():
    '''
    Connect to the three SMUs and PNA. 
    
    Parameters:
    -----------
    N/A
    
    Returns:
    ----------
    smus : list
        A list of the connected SMUs
    pna
        The connected PNA
    '''
    rm = visa.ResourceManager()
    
    # VisaIOError VI_ERROR_RSRC_NFOUND
    try:
      pna = rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')
      gate = rm.open_resource('GPIB1::24::INSTR')
      drain = rm.open_resource('GPIB1::25::INSTR')
      drive = rm.open_resource('GPIB1::26::INSTR')
    except visa.VisaIOError as e:
      print(e.args)
      exit
    
#    for x in [pna,gate,drain,drive]:
#      print(x.query("*IDN?")) # err -410
#      x.query('*OPC?')
    
    return ([gate,drain,drive],pna)
    
def smuSetup(smu, voltRange = 21, comp = 0.000105):
    '''
    A function for all general smu setup.
    System configures the compliance to the default
    Parameters:
    -----------
    smu
        The SMU to be set up.
    comp : float
        The current compliance to be set.
    
    Returns:
    ----------
    N/A
    '''
   # smu.write(':DISPlay:ENABle 1; CNDisplay')
    
    if comp: # set compliance if given. Default for 2400 is 105uA, 21V
        smu.write(':SENSe:VOLTage:RANGe ' + str(voltRange))
        smu.write(':SENSe:CURRent:PROTection:LEVel ' + str(comp))


def pnaInitSetup(pna):
#    pna.write("SYST:FPReset") # reset, delete measurements, traces, & windows
#    pna.write('*CLS')
#    pna.query('*OPC?')
    pna.write('CALCulate:PARameter:DELete:ALL')
    pna.write('SENSe1:SWEep:MODE HOLD')
    pna.write('DISPlay:ENABLE ON') # set to OFF to speed up measurement
    pna.write("DISPlay:WINDow1:TRACe1:DELete")
    
    
def pnaSetup(pna, ifBandwidth = None,startFreq = None, stopFreq = None,
             centFreq = None, spanFreq = None, nPoints = None, 
             avgMode = None, nAvg = None):
    '''
    PNA measurement setup. Unpacks a dict of setup 
    
    Parameters:
    -----------
    TODO: rewrite this section

    Returns:
    ----------
    N/A
    '''
    #set up channel here: power, cal, if bandwidth, # pts, sweep settings, avg, trigger

    if nPoints: pna.write('SENSe1:SWEep:POINts '+str(nPoints))
    pna.write('SENSe1:SWEep:GENeration ANALog')
    pna.write('SENSe1:SWEep:TIME:AUTO ON')
    # Frequencies shouldn't be changed outside callibrated range
    if startFreq and stopFreq: 
      pna.write('SENSe1:FREQuency:STARt {}'.format(startFreq)) 
      pna.write('SENSe1:FREQuency:STOP {}'.format(stopFreq))
    if centFreq and spanFreq: 
      pna.write('SENSe1:FREQuency:CENTer {}'.format(centFreq))
      pna.write('SENSe1:FREQuency:SPAN {}'.format(spanFreq))
    ###
    if avgMode: pna.write('SENSe1:AVERage:MODE {}'.format(avgMode))
    if nAvg: pna.write('SENSe1:AVERage:COUNt {}'.format(nAvg))
    if ifBandwidth: pna.write('SENSe1:BANDwidth {}'.format(ifBandwidth))
    
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

    s2 = ['S11','S12',
          'S21','S22']
    s3 = ['S11','S12','S13',
          'S21','S22','S23',
          'S31','S32','S33']
    s4 = ['S11','S12','S13','S14',
          'S21','S22','S23','S24',
          'S31','S32','S33','S34',
          'S41','S42','S43','S44']
    
    if sPorts < 2 or sPorts > 4:
        raise ValueError('Please Specify a number of ports between 2 and 4. '
                         'Currently, {} ports are specified.'.format(sPorts))
    s = [s2,s3,s4]
    sParms = s[sPorts-2]
    
    
    # explicitly redefine smus as local vars for readability 
    gate = smus[0]
    drain = smus[1]
    drive = smus[2]
    for x in smus:
        x.write('SOURce:VOLTage:LEVel 0.0')
        x.write(':CONFigure:VOLTage:DC')
        x.query('*OPC?')
    
    for vg in voltages[0]:
        gate.write('SOURce:VOLTage:LEVel '+str(vg)) # Sets voltage, output on
        for vd in voltages[1]:
            drain.write('SOURce:VOLTage:LEVel '+str(vd))
            for vdr in voltages[2]:
                drive.write('SOURce:VOLTage:LEVel '+str(vdr))
                for x in smus:
                    x.write(':CONFigure:VOLTage:DC')
                    x.query('*OPC?')
                   # print(x.query(':SENSe:DATA:LATest')) #err -113, -440                 
                #pna measurement here
                print("SMU Voltages set to the following - Gate: " + str(vg) + " Drain: " + str(vd) + " Drive: " + str(vdr))
                print("Now Sleeping for 2 min to allow system to equilibriate")
                for i in range(delay):
                    time.sleep(1)
                    if i%10 == 0:
                        print(str(i) + "/" + str(delay))

                filename = '{}_Vg{}Vd{}Vdr{}.s{}p'.format(testname,str(vg).replace('.','_'),str(vd).replace('.','_'),str(vdr).replace('.','_'),sPorts)
                pnaSetup(pna)
                for s in sParms:
                    measName = 'meas'+s 
                    print(measName)
#                    pna.write("DISPlay:WINDow1:STATE ON")
                    pna.write("CALCulate1:PARameter:DEFine:EXTended \'{}\',{}".format(measName,s))
                    pna.write('CALCulate1:PARameter:SELect \"{}\"'.format(measName))
#                    pna.write("DISPlay:WINDow1:TRACe1:FEED \'{}\'".format(measName)) # duplicate trace number
                    pna.timeout = 450000
                    pna.write("SENSe1:SWEep:MODE SINGle") 
                    pna.query('*OPC?')
                    pna.timeout = 2000
#                    pna.write("DISPlay:WINDow1:TRACe1:DELete")                                       
                print(':CALCulate1:DATA:SNP:PORTs:SAVE {},\'{}\\{}\' '.format('\'1,2,3\'',savedir,filename)) # query unterminated, also need to insert quotes around directory name
                pna.write(':CALCulate1:DATA:SNP:PORTs:SAVE {},\'{}\\{}\''.format('\'1,2,3\'',savedir,filename)) #read 16 S parms in SNP format
                ####********************* THIS COMMAND CAN NOT CREATE NEW FOLDERS!!!!********************!!!!!
                pna.query('*OPC?') 
                pna.write('CALCulate1:PARameter:DELete \"{}\"'.format(measName))

#                shutil.copy('\\\\192.168.1.1\\{}\\{}'.format(savedir,filename),'{}\\{}'.format(localsavedir,filename))                
                
    for x in smus:
        x.write('SOURce:VOLTage:LEVel 0.0')
        x.write(':CONFigure:VOLTage:DC')
        x.query('*OPC?')
        x.write(':OUTPut:STATe OFF')
        


    
def disconnect(smus, pna):
    '''
    Disconnect from the three SMUs and PNA. 
    
    Parameters:
    -----------
    smus : list
        A list of the connected SMUs
    pna
        The connected PNA
    
    Returns:
    ----------
    N/A
    '''
    pna.write('SENSe1:SWEep:MODE HOLD')    
    pna.close()
    for x in smus:
        x.write('SOURce:VOLTage:LEVel 0.0')
        x.write(':CONFigure:VOLTage:DC')
        x.query('*OPC?')
        x.write(':OUTPut:STATe OFF')
        x.close()
    
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
    ports = 2 # number of sPorts used in the measurement
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
#       pnaTestParms = {'ifBandwidth' : '50', # Hz, see above for options
#                    'startFreq' : 30E9, #Hz # use only if code does cal
#                    'stopFreq' : 33E9, #Hz # use only if code does cal
#                    'nPoints' : 201,
#                    'avgMode' : 'SWEEP', # POINT or SWEEP
#                    'nAvg' : 1
#                    }
    pnaTestParms=None
    localsavedir = 'C:\\Test' # Does nothing currently
    voltages = [Vg,Vd,Vdr]
    
    smus, pna = connect()
    for x in smus: smuSetup(x, maxVoltage, compliance)
    pnaInitSetup(pna)
    try:
      sParmMeas(voltages, smus, pna, ports, savedir, localsavedir, testname, delayTime, pnaTestParms)
    except visa.VisaIOError as e:
        print(e.args)
        pna.write('SENSe1:SWEep:MODE HOLD')    
        for x in smus:
          x.write(':OUTPut:STATe OFF')
          
        
   # pna.query('CALCulate1:PARameter:CATalog') # VisaIOError: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.
    
    disconnect(smus, pna)
    
    exit
if __name__ == "__main__":
    main()