# -*- coding: utf-8 -*-
"""
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

import numpy as np
import pyplot as plt
import time

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
    def __init__(self, smus, localsavedir, testname, delay = 0):               
        self.smus = smus
        self.localsavedir = localsavedir
        self.testname = testname
        self.delay = delay
        
    
    def formatData(data):
        data = data.split(',')
        n = len(data) / 5
        if n != int(n):
            print('Warning! SMU data doesn\'t have expected number of columns.')
        formatData = [np.zeros(int(n)) for i in range(0,5)]
        for i,d in enumerate(data): formatData[i % 5][i // 5] = d
        return formatData
    
    def measure(self, smuX = None, smuY = None):
        '''
        Uses SMUs as V source and measures time, V force, and I sense. 
        Will plot V vs I for two SMUs, given smuX and smuY
        
        Parameters
        -----------
        
        smuX : int
            Position of x-axis (voltage) SMU in list passed at creation of SMUmeas.
            
        smuY : int
            Position of y-axis (current) SMU in list passed at creation of SMUmeas.
            
        Returns
        -----------
        N/A
        '''
        smuData = [None]*len(self.smus)
        for i,x in enumerate(self.smus):
          if x.voltages == None:
            raise ValueError('No voltages defined for SMU \'{}\''.format(x.label))
          x.visaobj.write(':FORMat:ELEMents VOLTage, CURRent, RESistance, TIME, STATus')
          x.resetTime()
          smuData[i] = [np.zeros(1) for i in range(0,5)]
        currentV = [None for i in range(0,len(self.smus))]
            
        def setVoltageLoop(l = len(self.smus)):
          
            if l >= 1:
                for i in self.smus[l-1].voltages:
                    print('{} {}'.format(self.smus[l-1].label,i))
                    currentV[l-1] = i
                    setVoltageLoop(l-1)
            else:
              print('Setting SMU voltages. ',end='')
              testname2 = self.testname
              for i,v in enumerate(currentV):
                print('{} {} V'.format(self.smus[i].label,v), end='  ')
                self.smus[i].setVoltage(v)
                testname2 = testname2 + '_{}{}V'.format(self.smus[i].label,str(v).replace('.','_'))
              print("\nWaiting for {} sec to allow system to equilibriate".format(str(self.delay)))
              for i in range(self.delay):
                  time.sleep(1)
                  if i%10 == 0:
                      print(str(i) + "/" + str(self.delay))
              
              
              for i,x in enumerate(self.smus):
                  x.visaobj.timeout = 120000
                  data = x.meas()
                  x.visaobj.timeout = 2000
                  smuData[i] = np.append(smuData[i],self.formatData(data),1)
              
        setVoltageLoop()
        plt.close('all')  
        if smuX and smuY:
            fig = plt.figure(0)
            ax = fig.add_subplot(111)
            ax.plot(smuData[smuX][:][:,1:][0],smuData[smuY][:][:,1:][1])
            ax.set_xlabel('{} Voltage (V)'.format(self.smus[smuX].label))
            ax.set_ylabel('{} Current (A)'.format(self.smus[smuY].label))
        for i,x in enumerate(self.smus): 
            x.outputOff()
            smuData1 = smuData[i][:][:,1:]
            filename = '{}\\{}_{}.csv'.format(self.localsavedir,self.testname,x.label)
            print('Saving {} data on local PC in {}'.format(x.label,filename))
            np.savetxt(filename,np.transpose(smuData1),delimiter=',')
          
            # plot data
            fig = plt.figure(i+1)
            fig.suptitle(x.label)
            ax = fig.add_subplot(211)
            ax.plot(smuData1[3],smuData1[1],'.',markersize=10)
            ax.set_ylabel('Current (A)')
            ax1 = fig.add_subplot(212)
            ax1.plot(smuData1[3],smuData1[0],'.',markersize=10)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Voltage (V)')