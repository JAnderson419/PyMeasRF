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
        '''
        Creates a new Keithley 2400 SMU instance and attempts connection. 
        
        Parameters:
        -----------
        resource : str
            A string containing the VISA address of the device.
        label : str
            The name of the SMU that will be used to label data uniquely.
        voltages : list or array-like
            A list of voltages the user would like forced. 
            Used for stepping through voltage settings during measurements.
        
        Returns:
        ----------
        N/A
        '''
        self.connect(resource, label, voltages) 
        self.voltageLimits = [20,40,60,80,120,160,210]
    
    def connect(self, resource, label = None, voltages = None):
        '''
        Connect to the Keithley 2400 SMU. 
        
        Parameters:
        -----------
        resource : str
            A string containing the VISA address of the device.
        label : str
            The name of the SMU that will be used to label data uniquely.
        voltages : list or array-like
            A list of voltages the user would like forced. 
            Used for stepping through voltage settings during measurements.
        Returns:
        ----------
        N/A
        '''
        rm = visa.ResourceManager()
        self.label = label
        self.voltages = np.asarray(voltages)
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)

    def smuSetup(self, maxVolt = 20, comp = 0.000105):
        '''
        Sets the compliance of the SMU. Voltage protection is set to the smallest
        value that allows tests to be completed (smallest value larger than maxVolt).
        Default values for 2400 are 105uA, 20V
        
        Parameters:
        -----------
        maxVolt : float
            Maximum voltage to be applied to the device during testing.
        comp : float
            The current compliance to be set in amps.
        
        Returns:
        ----------
        N/A
        '''
       # smu.write(':DISPlay:ENABle 1; CNDisplay')

        self.visaobj.write('SOURce:FUNCtion:MODE VOLTage')
        self.visaobj.write('SOURce:VOLTage:RANGe:AUTO 1')
        self.visaobj.write('SOURce:VOLTage 0')        
        if maxVolt >160:
            print('Specified voltage larger than 160 V. Setting limit to 210 V.')
            self.visaobj.write('SOURce:VOLTage:PROTection:LEVel NONE')
        else:
            for i in self.voltageLimits:
                if maxVolt > i:
                    next
                else:
                    self.visaobj.write('SOURce:VOLTage:PROTection:LEVel ' + str(i))
                    break
        self.visaobj.write(':SENSe:CURRent:PROTection:LEVel ' + str(comp))
#        self.visaobj.write('SOURce:FUNCtion:MODE VOLTage')
#        self.visaobj.write('SOURce:VOLTage:LEVel 0')

    def setVoltage(self,voltage):
        '''
        Configures the SMU for sensing current while acting as a voltage source at the given voltage.
        
        Parameters:
        -----------
        voltage : double
            The voltage to be output.
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.write('SOURce:VOLTage {}'.format(str(voltage)))
        self.visaobj.write(':CONFigure:VOLTage:DC')
        self.visaobj.query('*OPC?')
        self.visaobj.write(':SENSe:FUNCtion:ON "CURRent"')

    def readError(self):
        '''
        Prints the most recent error and clears it from the error register on the SMU. 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        print(self.visaobj.query('SYSTem:ERRor:NEXT?'))
    
    def resetTime(self):
        '''
        Sets the internal timer to zero.
        
        Timer is based on internal clock and will slowly accumulate error. 
        It should not be used for measurements where anything more than millisecond level precision is required.
        See Keithley 2400 documentation for more detail.
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.write(':SYSTem:TIME:RESet')
    
    def meas(self, n = 1):
        '''
        Initiates aa measurement on the SMU and reads the data when complete. 
        
        Parameters:
        -----------
        n : int
            The number of measurements to instruct the device to take.
            1 to 2500
        Returns:
        ----------
        data : str
            Comma seperated list of data from the SMU. 
            Returned data controlled by ':FORMat:ELEMents' command. 
            Default format is 'VOLTage, CURRent, RESistance, TIME, STATus'
            Unavailable data returned as 10^37 value.
        '''
        self.visaobj.write(':ARM:COUNt 1')
        self.visaobj.write(':TRIGger:COUNt {}'.format(n))
        data = self.visaobj.query('READ?')
        return data
    
    def startMeas(self, n = 2500, tmeas = 1):
        '''
        Initiates an ongoing measurement on the SMU. 
        
        This must be followed up by a stopMeas() function or a manual 'FETCh?' command to retreive the data.
        
        Parameters:
        -----------
        n : int
            The number of measurements to instruct the device to take.
            1 to 2500
        tmeas : int
            The time (in seconds) between measurement operations
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.write(':ARM:COUNt 1')
        self.visaobj.write(':TRIGger:COUNt {}'.format(n))
        self.visaobj.write(':TRIGger:DELay {}'.format(tmeas))
        self.visaobj.write(':INITiate')

    def stopMeas(self):
        '''
        Aborts an ongoing measurement 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        data : str
            Comma seperated list of data from the SMU. 
            Returned data controlled by ':FORMat:ELEMents' command. 
            Default format is 'VOLTage, CURRent, RESistance, TIME, STATus'
            Unavailable data returned as 10^37 value.
        '''
        self.visaobj.write(':ABORt')
        data = self.visaobj.query('FETCh?')
        return data

    def outputOff(self):
        '''
        Sets voltage to sezo and turns off output. 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.setVoltage(0)
        self.visaobj.write(':OUTPut:STATe OFF')        
        
    def disconnect(self):
        '''
        Turns off output and disconnects from the SMU. 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.outputOff()
        self.visaobj.write(':SYSTem:KEY 23') # return to local
        self.visaobj.close()
        