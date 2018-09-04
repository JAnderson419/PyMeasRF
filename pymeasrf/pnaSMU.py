# -*- coding: utf-8 -*-
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

import visa
import numpy as np
import time
from context import pymeasrf
import pymeasrf.AgilentPNAXUtils as pnaUtils
import pymeasrf.Keithley2400 as k2400
import matplotlib.pyplot as plt
import matplotlib as mpl


def formatData(data):
    data = data.split(',')
    n = len(data) / 5
    if n != int(n):
        print('Warning! SMU data doesn\'t have expected number of columns.')
    formatData = [np.zeros(int(n)) for i in range(0,5)]
    for i,d in enumerate(data): formatData[i % 5][i // 5] = d
    return formatData

class PNAsmuMeas():
    '''
    Base class for measurements involving a PNA and Keithley SMUs.
    
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
    '''
    
    
    def __init__(self, smus, pna, sPorts, savedir, localsavedir, testname):
        
        
        self.smus = smus
        self.pna = pna
        self.sPorts = sPorts
        self.savedir = savedir
        self.localsavedir = localsavedir
        self.testname = testname
           
    
class SParmMeas(PNAsmuMeas): 
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
    delay : int
        The delay (in seconds) between SMU setting and PNA sweep. 
        Defaults to 0.
    postMeasDelay : int
        The delay (in seconds) that the SMU waits at 0 V after sMeas and before the next bias condition.
    smuMeasInter : int
        The time interval (in seconds) between SMU measurements.
        Values from 0 to 999 accepted.
    pnaparms : dict
        A dictionary containing test parameters to set on the pna.
        
    Returns:
    ----------
    N/A
    '''

    def __init__(self, smus, pna, sPorts, savedir, localsavedir, testname, delay = 0,
<<<<<<< HEAD
                 postMeasDelay = 0, smuMeasInter = 1.0, power = None, pnaparms = None, trueMode = False, phaseOffset = 0): 
=======
                  postMeasDelay = 0, smuMeasInter = 1.0, power = None, pnaparms = None, trueMode = False):      
>>>>>>> 442f6d7758c9746588aaaee6fc57daca4da79790
        PNAsmuMeas.__init__(self,smus,pna,sPorts,savedir,localsavedir,testname)
        self.delay = delay
        self.postMeasDelay = postMeasDelay
        self.smuMeasInter = smuMeasInter
        self.pnaparms = pnaparms
        self.trueMode = trueMode
        self.power = power
<<<<<<< HEAD
        self.phaseOffset = phaseOffset
        
=======
>>>>>>> 442f6d7758c9746588aaaee6fc57daca4da79790
        
    def measure(self, smuX = None, smuY = None, smuZ = None):
        '''
        Uses SMUs as V source and measures time, V force, and I sense. 
        Will plot V vs I for two SMUs, given smuX and smuY
        
<<<<<<< HEAD
=======
    def measure(self, smuX = None, smuY = None, smuZ = None):
        '''
        Uses SMUs as V source and measures time, V force, and I sense. 
        Will plot V vs I for two SMUs, given smuX and smuY
        
>>>>>>> 442f6d7758c9746588aaaee6fc57daca4da79790
        Parameters
        -----------
        
        smuX : int
            Position of x-axis SMU (voltage data) in list passed at creation of measurement.
            
        smuY : int
            Position of y-axis SMU (current data) in list passed at creation of measurement.
        smuZ : int
            Position of z-axis (color) SMU (voltage data) in list passed at creation of measurement.
            
        Returns
        -----------
        N/A
        '''        
        if self.smus:
            smuData = [None]*len(self.smus)
            for i,x in enumerate(self.smus):
                if x.voltages.all() == None:
                    raise ValueError('No voltages defined for SMU \'{}\''.format(x.label))
                x.visaobj.write(':FORMat:ELEMents VOLTage, CURRent, RESistance, TIME, STATus')
                x.resetTime()
                smuData[i] = [np.zeros(1) for i in range(0,5)]
            currentV = [None for i in range(0,len(self.smus))]
            
            self.q = 1 # counter for test number - ensures all snp names unique
            def setVoltageLoop(l = len(self.smus)):
                
                if l >= 1:
                    for i in self.smus[l-1].voltages:
#                        print('{} {}'.format(self.smus[l-1].label,i))
                        currentV[l-1] = i
                        setVoltageLoop(l-1)
                else:
                    print('Setting SMU voltages. ',end='')
                    testname2 = self.testname + '_{}'.format(self.q)
                    self.q += 1
                    for i,v in enumerate(currentV):
                        print('{} {} V'.format(self.smus[i].label,v), end='  ')
                        self.smus[i].setVoltage(v)
                        self.smus[i].startMeas(tmeas = self.smuMeasInter)
                        testname2 = testname2 + '_{}{}V'.format(self.smus[i].label,str(v).replace('.','_'))
                    print()
                    if self.delay:
                        print("\nWaiting for {} sec to allow system to equilibriate".format(str(self.delay)))
                        for i in range(self.delay):
                            time.sleep(1)
                            if i%10 == 0:
                                print(str(i) + "/" + str(self.delay))
                  
<<<<<<< HEAD
                    self.pna.sMeas(self.sPorts, self.savedir, self.localsavedir, testname2, self.power,
                                   self.pnaparms, bal = self.trueMode, phase = self.phaseOffset)
                    for i,x in enumerate(self.smus):
                        x.visaobj.timeout = 1200000
                        data = x.stopMeas()
                        x.visaobj.timeout = 2000000
=======
                    self.pna.sMeas(self.sPorts, self.savedir, self.localsavedir, testname2, self.power, self.pnaparms, bal = self.trueMode)
                    for i,x in enumerate(self.smus):
                        x.visaobj.timeout = 1200000
                        data = x.stopMeas()
                        x.visaobj.timeout = 20000
>>>>>>> 442f6d7758c9746588aaaee6fc57daca4da79790
                        smuData[i] = np.append(smuData[i],formatData(data),1)
                        if self.postMeasDelay: x.setVoltage(0)
                    
                    if self.postMeasDelay:
                        print("\nWaiting for {} sec before the next measurement".format(str(self.postMeasDelay)))
                        for i in range(self.postMeasDelay):
                            time.sleep(1)
                            if i%10 == 0:
                                print(str(i) + "/" + str(self.postMeasDelay))
                  
         
            setVoltageLoop()
        else:
            self.pna.sMeas(self.sPorts, self.savedir, self.localsavedir, self.testname, self.power, self.pnaparms, bal = self.trueMode)
        
        plt.close('all') 
<<<<<<< HEAD

=======
>>>>>>> 442f6d7758c9746588aaaee6fc57daca4da79790
        
        if self.smus:
            if (smuX != None and smuY != None):
                fig = plt.figure()
                ax = fig.add_subplot(111)
                if smuZ != None:
                    colormap = mpl.cm.get_cmap('jet',len(smuData[smuZ][:][:,1:][0]))
                    ax.scatter(smuData[smuX][:][:,1:][0],smuData[smuY][:][:,1:][1]*1E6, c = smuData[smuZ][:][:,1:][0], cmap = colormap)
#                    cbar = plt.colorbar(ax)
#                    cbar.set_label('{} Voltage (V)'.format(self.smus[smuZ].label))
                else:
                    ax.plot(smuData[smuX][:][:,1:][0],smuData[smuY][:][:,1:][1]*1E6)
                ax.set_xlabel('{} Voltage (V)'.format(self.smus[smuX].label))
                ax.set_ylabel('{} Current (uA)'.format(self.smus[smuY].label))
                plt.savefig('{}\\{}_xy'.format(self.localsavedir,self.testname))
                
            for i,x in enumerate(self.smus): 
                x.outputOff()
                smuData1 = smuData[i][:][:,1:]
                filename = '{}\\{}_{}.csv'.format(self.localsavedir,self.testname,x.label)
                print('Saving {} data on local PC in {}'.format(x.label,filename))
                np.savetxt(filename,np.transpose(smuData1),delimiter=',')
              
                # plot data
                fig = plt.figure()
                fig.suptitle(x.label)
                ax = fig.add_subplot(211)
                ax.plot(smuData1[3],smuData1[1]*1E6,'.',markersize=10)
                ax.set_ylabel('Current (uA)')
                ax1 = fig.add_subplot(212)
                ax1.plot(smuData1[3],smuData1[0],'.',markersize=10)
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Voltage (V)')
            
    def timeIntervalMeasure(self, measTimeInterval, numIntervals):
        '''
        Carries out s-Parameter measurements (with arbitrary number of SMU bias
        points) at a set time interval.
        
        Parameters
        -----------
        
        measTimeInterval : int
            Number of seconds between triggering of an sParmMeas cycle.
            
        numIntervals : int
            Number of times to repeat the measurement.
            
        Returns
        -----------
        N/A
        '''
        testname = self.testname # record starting testname
        meashr = measTimeInterval // 3600
        measmin = (measTimeInterval % 3600) // 60
        meassec = (measTimeInterval % 3600) % 60
        
        totalTime = numIntervals*measTimeInterval
        totalhr = totalTime // 3600
        totalmin = (totalTime % 3600) // 60
        totalsec = (totalTime % 3600) % 60
        
        endTime = time.localtime(time.time()+totalTime)
        print('Starting time: {}.'.format(time.asctime()))
        print('Performing {} measurements over {} hours, {} minutes, and {} seconds.'.format(numIntervals,totalhr,totalmin,totalsec))
        print('Estimated completion after: {}.'.format(time.asctime(endTime)))
        for i in range(0,numIntervals):
            print('Starting measurement {}: {}.'.format(i+1,time.asctime()))
            self.testname = '{}_{}__{}'.format(i+1,time.strftime('%d_%b_%Y__%H_%M_%S'),testname)
            self.measure()
            print('Measurement {} complete: {}.'.format(i+1,time.asctime()))
            print('Waiting for {} hours, {} minutes, and {} seconds.'.format(meashr,measmin,meassec))
            for j in range(measTimeInterval):
               time.sleep(1)
        self.testname = testname # return testname to original value
        
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
          k2400.Keithley2400('GPIB1::24::INSTR', label='gate', voltages = [0.8]),
          k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [0.17]),
          k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
           ]

    compliance = 0.200 #Amps IE 105uA = 0.000105 
    maxVoltage = 20 #Maximum expected voltage to be used 
    ports = '1,2,3,4' # string containing comma separated port numbers to be used
    delayTime = 2 #Time between setting SMU voltage and measurement in seconds

    testname = 'RFTtest' # name snp files will be saved as current file name format is as follows:
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    savedir = 'C:\\Documents\\RFT' # Directory where snp files will be saved on PNA
    localsavedir = r'D:\MeasurementData\RFT' # Directory where SMU data will be saved
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
    meas = SParmMeas(None, pna, ports, savedir, localsavedir, testname, delayTime, pnaTestParms)
    try:
       meas.measure()
#      meas.timeIntervalMeasure(900,144)
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