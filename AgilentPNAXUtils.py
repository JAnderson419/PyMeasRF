#AgilentPNAXUtils.py

import visa
import numpy as np
import re as re

class AgilentPNAx:
    def __init__(self, resource):
        rm = visa.ResourceManager()
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit
    
    
    def connect(self, resource):
        '''
        Connect to the PNA. 
        
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
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          exit

    def pnaInitSetup(self):
        pna = self.visaobj
    #    pna.write("SYST:FPReset") # reset, delete measurements, traces, & windows
    #    pna.write('*CLS')
    #    pna.query('*OPC?')
        pna.write('CALCulate:PARameter:DELete:ALL')
        pna.write('SENSe1:SWEep:MODE HOLD')
        pna.write('DISPlay:ENABLE ON') # set to OFF to speed up measurement
        
        #TODO: add check to see if trace exists or not
        traces = pna.query('DISPlay:WINDow1:CATalog?')
        if re.search('(^|,)1,',traces):
            pna.write("DISPlay:WINDow1:TRACe1:DELete") 
        
        
    def pnaSetup(self, ifBandwidth = None,startFreq = None, stopFreq = None,
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
        pna = self.visaobj
    
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

        
    def sMeas(self, sPorts, savedir, localsavedir, testname, pnaparms = None):
        pna = self.visaobj
        
        s2 = ['S11','S12',
              'S21','S22']
        s3 = ['S11','S12','S13',
              'S21','S22','S23',
              'S31','S32','S33']
        s4 = ['S11','S12','S13','S14',
              'S21','S22','S23','S24',
              'S31','S32','S33','S34',
              'S41','S42','S43','S44']
        
        numPorts = len(re.findall('\d+',str))
        
        if numPorts < 2 or numPorts > 4:
            raise ValueError('Please Specify a number of ports between 2 and 4. '
                             'Currently, {} ports are specified.'.format(str(numPorts)))
        s = [s2,s3,s4]
        sParms = s[numPorts-2]
        filename = '{}.s{}p'.format(testname,numPorts)
        self.pnaSetup(pna, **pnaparms)
        for s in sParms:
            measName = 'meas'+s 
            print(measName)
    #                    pna.write("DISPlay:WINDow1:STATE ON")
            pna.write("CALCulate:PARameter:DEFine:EXTended \'{}\',{}".format(measName,s))
            pna.write('CALCulate1:PARameter:SELect \"{}\"'.format(measName))
            pna.write("DISPlay:WINDow1:TRACe1:FEED \'{}\'".format(measName)) # duplicate trace number
            pna.timeout = 450000
            pna.write("SENSe1:SWEep:MODE SINGle") 
            pna.query('*OPC?')
            pna.timeout = 2000
            pna.write("DISPlay:WINDow1:TRACe1:DELete") 
            self.checkCal()                                   
        print(':CALCulate1:DATA:SNP:PORTs:SAVE \'{}\',\'{}\\{}\' '.format(sPorts,savedir,filename)) # query unterminated, also need to insert quotes around directory name
        pna.write(':CALCulate1:DATA:SNP:PORTs:SAVE {},\'{}\\{}\''.format(sPorts,savedir,filename)) #read 16 S parms in SNP format
        pna.query('*OPC?') 

    def outputOff(self):
        self.visaobj.write('SENSe1:SWEep:MODE HOLD') 


    ###############################
    # Wincal saves calfiles with format
    # CalSet_###
    ##########################
    
    def checkCal(self):
        calname = self.visaobj.query('SENSe1:CORRection:CSET:ACTivate? NAME')
        if calname == "No Calset Selected":
            raise ValueError('No active calset for the measurement. Aborting')
        else:
            print(calname)
            
    def getCalInfo(self):
        print(self.visaobj.query('SENSe1:CORRection:CSET:ACTivate? NAME'))
        print(self.visaobj.query('SENSe1:CORRection:CSET:TSET:TYPE?'))
        print(self.visaobj.query('SENSe1:CORRection:CSET:TYPE:CATalog? NAME'))
        
    def getAvailCals(self):
        print(self.visaobj.query('CSET:CATalog?'))
