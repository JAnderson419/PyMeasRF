# -*- coding: utf-8 -*-
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

import visa
import numpy as np
import time
import AgilentPNAXUtils as pnaUtils
import Keithley2400 as k2400
import matplotlib.pyplot as plt

def formatData(data):
    data = data.split(',')
    n = len(data) / 5
    if n != int(n):
        print('Warning! SMU data doesn\'t have expected number of columns.')
    formatData = [np.zeros(int(n)) for i in range(0,5)]
    for i,d in enumerate(data): formatData[i % 5][i // 5] = d
    return formatData
        

def sParmMeas(smus, pna, sPorts, savedir, localsavedir, testname, delay = 0, pnaparms = None): 
    '''
    PNA s-parameter measurement with arbitrary number of nested smu voltage steps.
    
    Handles any number of SMUs by recursively iterating through objects. 
    Voltages are entered from the SMU voltage lists into a temporary currentV list, with all SMU voltages being set simultaneously.
    A pause then occurs for the delay period specified with sMeas being called at the conclusion. 
    Data is fetched from the SMUs after each sMeas() and appended to the SMU data array.
    
    SMU data is plotted and saved in localsavedir. 
    PNA data saved in savedir on PNA.
    
    TODO: Implement base class for measurements.
    
    Parameters:
    -----------
    
    smus : list
        A list of the connected SMU objects with voltages to be iterated through.
        If no SMUs are specified in the list, the function simply calls pna.sMeas().
    pna : AgilentPNAx
        The connected PNA.
    sPorts : string
        The ports to be used in S-parameter measurement.
    savedir : string
        The directory on the PNA in which to save snp files.
    localsavedir : string    
        The local directory where SMU data will be saved.
    testname : string
        Identifier for the test that will be used in saved filenames.
    delay: int
        The delay (in seconds) between SMU setting and PNA sweep. 
        Defaults to 0.
    pnaparms : dict
        A dictionary containing test parameters to set on the pna.
        
    Returns:
    ----------
    N/A
    '''
    
    if smus:
        smuData = [None]*len(smus)
        for i,x in enumerate(smus):
          if x.voltages == None:
            raise ValueError('No voltages defined for SMU \'{}\''.format(x.label))
          x.visaobj.write(':FORMat:ELEMents VOLTage, CURRent, RESistance, TIME, STATus')
          x.resetTime()
          smuData[i] = [np.zeros(1) for i in range(0,5)]
        currentV = [None for i in range(0,len(smus))]
        
        def setVoltageLoop(l = len(smus)):
          
            if l >= 1:
                for i in smus[l-1].voltages:
                    print('{} {}'.format(smus[l-1].label,i))
                    currentV[l-1] = i
                    setVoltageLoop(l-1)
            else:
              print('Setting SMU voltages. ',end='')
              testname2 = testname
              for i,v in enumerate(currentV):
                print('{} {} V'.format(smus[i].label,v), end='  ')
                smus[i].setVoltage(v)
                smus[i].startMeas()
                testname2 = testname2 + '_{}{}V'.format(smus[i].label,str(v).replace('.','_'))
              print("\nWaiting for {} sec to allow system to equilibriate".format(str(delay)))
              for i in range(delay):
                  time.sleep(1)
                  if i%10 == 0:
                      print(str(i) + "/" + str(delay))
              
              pna.sMeas(sPorts, savedir, localsavedir, testname2, pnaparms)
              for i,x in enumerate(smus):
                  data = x.stopMeas()
                  smuData[i] = np.append(smuData[i],formatData(data),1)
     
        setVoltageLoop()
    else:
        pna.sMeas(sPorts, savedir, localsavedir, testname, pnaparms)
    
    plt.close('all')      
    for i,x in enumerate(smus): 
        x.outputOff()
        smuData1 = smuData[i][:][:,1:]
        filename = '{}\\{}_{}.csv'.format(localsavedir,testname,x.label)
        print('Saving {} data on local PC in {}'.format(x.label,filename))
        np.savetxt(filename,np.transpose(smuData1),delimiter=',')
      
        # plot data
        fig = plt.figure(i)
        fig.suptitle(x.label)
        ax = fig.add_subplot(211)
        ax.plot(smuData1[3],smuData1[1],'.',markersize=10)
        ax.set_ylabel('Current (A)')
        ax1 = fig.add_subplot(212)
        ax1.plot(smuData1[3],smuData1[0],'.',markersize=10)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)')
    
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
    
    pna = pnaUtils.AgilentPNAx('TCPIP0::192.168.1.1::inst0::INSTR')
    ############################# User specified test Parameters ###################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################

    smus = [
#          k2400.Keithley2400('GPIB1::24::INSTR', label='gate', voltages = [0]),
          k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [.2, .4])
#          k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
           ]

    compliance = 0.100 #Amps IE 105uA = 0.000105 
    maxVoltage = 100 #Maximum expected voltage to be used 
    ports = '1,2' # string containing comma separated port numbers to be used
    delayTime = 2 #Time between setting SMU voltage and measurement in seconds

    testname = 'Test2' # name snp files will be saved as current file name format is as follows:
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    savedir = 'C:\\Documents\\pyvisa' # Directory where snp files will be saved on PNA
    localsavedir = r'C:\Users\hybrid\Desktop\PythonData' # Directory where SMU data will be saved
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

    for x in smus: x.smuSetup(maxVoltage, compliance)
    pna.pnaInitSetup()
    try:
      sParmMeas(smus, pna, ports, savedir, localsavedir, testname, delayTime, pnaTestParms)
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