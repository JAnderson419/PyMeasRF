#Agilent33220a.py
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

import visa
import numpy as np

class Agilent33220a:
    '''
    A class for controlling the Agilent 33220a Arbitrary Waveform Generator 
    using VISA commands. This class should also work for other AWGs that 
    implement the same syntax as no spec limits are currently implemented in the code.
    For detailed specifications, see page 336 of the 33220a User's Guide.  
    '''
    
    
    def __init__(self, resource, label = None):
        '''
        Creates a new instrument instance and attempts connection. 
        
        Parameters:
        -----------
        resource : str
            A string containing the VISA address of the device.
        label : str
            The name of the device that will be used to label data uniquely.
        
        Returns:
        ----------
        N/A
        '''
        self.connect(resource, label) 
    
    def connect(self, resource, label = None):
        '''
        Connect to the instrument. 
        
        Parameters:
        -----------
        resource : str
            A string containing the VISA address of the device.
        label : str
            The name of the device that will be used to label data uniquely.
        Returns:
        ----------
        N/A
        '''
        rm = visa.ResourceManager()
        self.label = label
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)

    def basicOutput(self, wform, freq, ampl, offset = 0):
        '''
        Uses apply command to quickly define waveform for continuous output. 
        
        From the 33220a manual, page 163:           
        The APPLy command performs the following operations:
            • Sets the trigger source to Immediate (equivalent to sending the
              TRIG:SOUR IMM command).
            • Turns off any modulation, sweep, or burst mode currently enabled
              and places the instrument in the continuous waveform mode.
            • Turns on the Output connector (OUTP ON command) but does not
              change the output termination setting (OUTP:LOAD command).
            • Overrides the voltage autorange setting and automatically enables
              autoranging (VOLT:RANG:AUTO command).
            • For square waveforms, overrides the current duty cycle setting and
              automatically selects 50% (FUNC:SQU:DCYC command).
            • For ramp waveforms, overrides the current symmetry setting and
              automatically selects 100% (FUNC:RAMP:SYMM command).
        
        Parameters:
        -----------
        wform : str
            The waveform to be output. 
            Options include SINusoid, SQUare, RAMP, PULSe, NOISe, DC, USER
            (Case sensitive, may define using entire word or only uppercase letters).
            
            For NOISe: freq is not applicable but must be defined.
           
            For DC: freq and ampl not applicable but must be defined.
        freq : float
            The frequency of the waveform in kHz.
        ampl : float
            The peak-to-peak amplitude of the waveform in volts.
        offset : float 
            The DC offset of the waveform in volts.
        Returns:
        ----------
        N/A
        '''
        
        self.visaobj.write('APPLy:{} {} KHZ, {} VPP, {} V'.format(wform,freq,ampl,offset))

    def fsweepOutput(self, wform, freqStart, freqStop, ampl, offset = 0, sweepTime = 1, sweepType = 'LIN', trig = 'IMMediate'):
        '''
        Performs a frequency sweep.
        
        Parameters:
        -----------
        wform : str
            The waveform to be output. 
            Options include SINusoid, SQUare, RAMP, USER
            (Case sensitive, may define using entire word or only uppercase letters).
        freqStart : float
            The sweep start frequency of the waveform in kHz.
        freqStop : float
            The sweep end frequency of the waveform in kHz.
        ampl : float
            The peak-to-peak amplitude of the waveform in volts.
        offset : float 
            The DC offset of the waveform in volts.
        sweepTime : float
            The period of the sweep in seconds. Values from 1ms to 500s allowed.
        sweepType : str
            Specifies linear or logarithmic freq spacing.
            Acceptable values are 'LIN' or 'LOG'.
        trig : str
            Specifies trigger source for sweep/burst mode. 
            Acceptable values are:
                
            'IMMediate' : waveform is output continuously
            
            'EXTernal' : waits for a signal from the Trig In connector, performs one sweep/burst
            
            'BUS' : waits for a software bus trigger, performs one sweep/burst
        Returns:
        ----------
        N/A
        '''
        self.visaobj.write('FUNCtion {}'.format(wform))
        self.visaobj.write('FREQuency:STARt {} KHZ'.format(freqStart))
        self.visaobj.write('FREQuency:STOP {} KHZ'.format(freqStop))
        self.visaobj.write('VOLTage {} VPP'.format(ampl))
        self.visaobj.write('VOLTage:OFFSet {} V'.format(offset))
        self.visaobj.write('SWEep:SPACing {}'.format(sweepType))
        self.visaobj.write('SWEep:TIME {} S'.format(sweepTime))
        self.visaobj.write('TRIGger:SOURce {}'.format(trig))
        self.visaobj.write('SWEep:STATe ON')

    def trigger(self):
        '''
        Asserts a trigger over the software bus.
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.assert_trigger()
          
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
        print(self.visaobj.query('SYSTem:ERRor?'))
        
    def outputOff(self):
        '''
        Turns off output. 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.write(':OUTPut OFF')        
        
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
        self.visaobj.control_ren(6) # sends GTL (Go To Local) command
        self.visaobj.close()