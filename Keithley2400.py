#Keithley2400.py
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

import visa
import numpy as np

class Keithley2400:
    def __init__(self, resource, label = None, voltages = None):
        rm = visa.ResourceManager()
        self.label = label
        self.voltages = voltages
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit  
    
    def connect(self, resource, label = None, voltages = None):

        rm = visa.ResourceManager()
        self.label = label
        self.voltages = voltages
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit

    def smuSetup(self, voltRange = 21, comp = 0.000105):
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
#            self.visaobj.write(':SENSe:VOLTage:RANGe ' + str(voltRange))
            self.visaobj.write(':SENSe:CURRent:PROTection:LEVel ' + str(comp))
        self.visaobj.write('SOURce:FUNCtion:MODE VOLTage')
        self.visaobj.write('SOURce:VOLTage:LEVel 0')

    def setVoltage(self,voltage):
        self.visaobj.write('SOURce:VOLTage:LEVel {}'.format(str(voltage)))
        self.visaobj.write(':CONFigure:VOLTage:DC')
        self.visaobj.query('*OPC?')
        self.visaobj.write(':SENSe:FUNCtion:ON "CURRent"')

    def readError(self):
        print(self.visaobj.query('SYSTem:ERRor:NEXT?'))
    
    def resetTime(self):
        self.visaobj.write(':SYSTem:TIME:RESet')
    
    def meas(self,n = 1):
        self.visaobj.write(':ARM:COUNt 1')
        self.visaobj.write(':TRIGger:COUNt {}'.format(n))
        data = self.visaobj.query('READ?')
        return data
    
    def startMeas(self, n = 1):
        self.visaobj.write(':ARM:COUNt 1')
        self.visaobj.write(':TRIGger:COUNt 2500')
        self.visaobj.write(':TRIGger:DELay {}'.format(n))
        self.visaobj.write(':INITiate')

    def stopMeas(self):
        self.visaobj.write(':ABORt')
        data = self.visaobj.query('FETCh?')
        return data

    def outputOff(self):
        self.setVoltage(0)
        self.visaobj.write(':OUTPut:STATe OFF')        
        
    def disconnect(self):
        self.outputOff()
        self.visaobj.write(':SYSTem:KEY 23') # return to local
        self.visaobj.close()
        