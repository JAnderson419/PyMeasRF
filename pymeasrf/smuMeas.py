# -*- coding: utf-8 -*-
"""
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

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
    
class SMUmeas():
    '''
    Class for handling measurements made with multiple SMUs.
    
    smus : list
        A list of the connected SMU objects with voltages to be iterated through.
        If no SMUs are specified in the list, the function simply calls pna.sMeas().
    localsavedir : string    
        The local directory where SMU data will be saved.
    testname : string
        Identifier for the test that will be used in saved filenames.
    '''
    def __init__(self, smus, localsavedir, testname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1):               
        self.smus = smus
        self.localsavedir = localsavedir
        self.testname = testname
        self.delay = delay
        self.measTime = measTime
        self.postMeasDelay = postMeasDelay
        self.smuMeasInter = smuMeasInter
        
    
    def formatData(data):
        data = data.split(',')
        n = len(data) / 5
        if n != int(n):
            print('Warning! SMU data doesn\'t have expected number of columns.')
        formatData = [np.zeros(int(n)) for i in range(0,5)]
        for i,d in enumerate(data): formatData[i % 5][i // 5] = d
        return formatData
    
    def measure(self, smuX = None, smuY = None, smuZ = None):
        '''
        Uses SMUs as V source and measures time, V force, and I sense. 
        Will plot V vs I for two SMUs, given smuX and smuY
        
        Parameters
        -----------
        
        smuX : int
            Position of x-axis (voltage) SMU in list passed at creation of SMUmeas.
            
        smuY : int
            Position of y-axis (current) SMU in list passed at creation of SMUmeas.
            
        smuZ : int
            Position of z-axis (color) SMU (voltage data) in list passed at creation of measurement.
            
        Returns
        -----------
        N/A
        '''
        smuData = [None]*len(self.smus)
        for i,x in enumerate(self.smus):
          if x.voltages.all() == None:
            raise ValueError('No voltages defined for SMU \'{}\''.format(x.label))
          x.visaobj.write(':FORMat:ELEMents VOLTage, CURRent, RESistance, TIME, STATus')
          x.resetTime()
          smuData[i] = [np.zeros(1) for i in range(0,5)]
        currentV = [None for i in range(0,len(self.smus))]
            
        def setVoltageLoop(l = len(self.smus)):
          
            if l >= 1:
                for i in self.smus[l-1].voltages:
#                    print('{} {}'.format(self.smus[l-1].label,i))
                    currentV[l-1] = i
                    setVoltageLoop(l-1)
            else:
              print('Setting SMU voltages. ',end='')
              testname2 = self.testname
              for i,v in enumerate(currentV):
                print('{} {} V'.format(self.smus[i].label,v), end='  ')
                self.smus[i].setVoltage(v)
                testname2 = testname2 + '_{}{}V'.format(self.smus[i].label,str(v).replace('.','_'))
              print('') # prints newline character after SMU voltages are listed
              if self.delay:
                  print("\nWaiting for {} sec to allow system to equilibriate".format(str(self.delay)))
                  for i in range(self.delay):
                      time.sleep(1)
                      if i%10 == 0:
                          print(str(i) + "/" + str(self.delay))
              
              
              for i,x in enumerate(self.smus):
                  x.visaobj.timeout = 120000
                  if self.measTime > self.smuMeasInter:
                      print("\nMeasuring for {} sec.".format(str(self.measTime)))
                      x.startMeas(tmeas = self.smuMeasInter)
                      for r in range(self.measTime):
                          time.sleep(1)
                      data = x.stopMeas()
                  else:
                      data = x.meas()
                  if self.postMeasDelay: x.setVoltage(0)
                  x.visaobj.timeout = 2000
                  smuData[i] = np.append(smuData[i],formatData(data),1)
              
              if self.postMeasDelay:
                  
                  print("\nWaiting for {} sec before the next measurement".format(str(self.postMeasDelay)))
                  for i in range(self.postMeasDelay):
                      time.sleep(1)
                      if i%10 == 0:
                          print(str(i) + "/" + str(self.postMeasDelay))                
                
        setVoltageLoop()
        plt.close('all')  
        if (smuX != None and smuY != None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            if smuZ != None:
                colormap = mpl.cm.get_cmap('jet',len(smuData[smuZ][:][:,1:][0]))
                ax.scatter(smuData[smuX][:][:,1:][0],smuData[smuY][:][:,1:][1]*1E6, c = smuData[smuZ][:][:,1:][0])
#                cbar = fig.colorbar(ax)
#                cbar.set_label('{} Voltage (V)'.format(self.smus[smuZ].label))
            else:
                ax.plot(smuData[smuX][:][:,1:][0],smuData[smuY][:][:,1:][1])
            ax.set_xlabel('{} Voltage (V)'.format(self.smus[smuX].label))
            ax.set_ylabel('{} Current (uA)'.format(self.smus[smuY].label))
            ax.set_title(self.testname)
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
            
def main():
    biases1 = np.linspace(-5, 5, 25)
    biases = np.append(np.linspace(0, -5, 13), biases1)
    biases = np.append(biases, biases1[::-1])
    biases = np.append(biases, np.linspace(-5, 0, 13))
    smus = [
#          k2400.Keithley2400('GPIB1::24::INSTR', label='gate', voltages = np.linspace(0,20,5)),
          k2400.Keithley2400('GPIB0::4::INSTR', label='bias', voltages=biases)
#          k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
           ]

    compliance = 0.100 #Amps IE 105uA = 0.000105 
    maxVoltage = 5 #Maximum expected voltage to be used
    delayTime = 2 #Time between setting SMU voltage and measurement in seconds

#    testname = 'HeatingTest_SteadyStateRes_180sDelay_180sCool_2Vmax' # name snp files will be saved as current file name format is as follows:
    testname = 'NNO_actuator_test_4-2-3_3V_broken'
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    localsavedir = r'C:\Users\Jackson\Desktop\NNO' # Directory where SMU data will be saved
    
    for x in smus: 
        x.smuSetup(maxVoltage, compliance)
        x.visaobj.write(':SYSTem:BEEPer:STATe 0')
    test = SMUmeas(smus, localsavedir, testname, delay=delayTime, measTime=0, postMeasDelay=0)
    
    test.measure()
    for x in smus:
        x.disconnect()
            
if __name__ == "__main__":
    main()