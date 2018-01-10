#Keithley2400.py

import visa
import numpy as np

class Keithley2400:
    def __init__(self, resource):
        rm = visa.ResourceManager()
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit  
    
    def connect(self):

        rm = visa.ResourceManager()
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit

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

    def setVoltage(self,voltage):
        self.visaobj.write('SOURce:VOLTage:LEVel {}'.format(str(voltage)))
        self.visaobj.write(':CONFigure:VOLTage:DC')
        self.visaobj.query('*OPC?')

    def outputOff(self):
        self.setVoltage(0)
        self.visaobj.write(':OUTPut:STATe OFF')        
        
    def disconnect(self):
        self.outputOff()
        self.visaobj.close()