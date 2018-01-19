#AgilentPNAXUtils.py
'''
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
'''

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
        
       

    def clearWindow(self,winNum):
        traces = self.visaobj.query('DISPlay:WINDow{}:CATalog?'.format(winNum))
        if re.search("EMPTY",traces):
            next
        else:
            traces = traces.split(',')
            for trace in traces:
                self.visaobj.write("DISPlay:WINDow{}:{}:DELete".format(winNum,trace)) 
            
    def disconnect(self):
        self.outputOff()
#        self.clearWindows()
        self.visaobj.close()
        
        
    def pnaSetup(self, portNums, ifBandwidth = None,startFreq = None, stopFreq = None,
                 centFreq = None, spanFreq = None, nPoints = None, 
                 avgMode = None, nAvg = None):
        '''
        PNA measurement setup. Unpacks a dict of setup 
        
        Parameters:
        -----------
        ifBandwidth: int
            IF (receiver) bandwidth. Allowable values include:
            1,          2,    3,    5,    7,
            10,   15,   20,   30,   50,   70,
            100,  150,  200,  300,  500,  700,
            1k,   1.5k, 2k,   3k,   5k,   7k,
            10k,  15k,  20k,  30k,  50k,  70k,
            100k,       200k, 280k, 360k, 600k
        centerFreq & spanFreq : int
            frequency range of measurement. Max: 50 GHz. Cannot be used with start/stopFreq.
        startFreq & stopFreq : int
            frequency range of measurement. Max: 50 GHz. Cannot be used with center/spanFreq.
        nPoints : int
            number of points in measurement (1 to 32,001)
        avgMode : string
            Determines type of averaging done by PNA. 
            POINT : averages at each frequency point before moving on
            SWEEP : averages the results of n sweeps 
        nAvg : int
            number of averages to take
    
        Returns:
        ----------
        N/A
        '''
        #set up channel here: power, cal, if bandwidth, # pts, sweep settings, avg, trigger
        pna = self.visaobj
        pna.write('CALCulate:PARameter:DELete:ALL')
        
        for n in portNums: 
          pna.write('DISPlay:WINDow:ENABle 1'.format(n))
          self.clearWindow(n)
    
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
        
        sParms = []
        nums = sPorts.split(',')
        
        if len(nums) < 1 or len(nums) > 4:
            raise ValueError('Please Specify a number of ports between 1 and 4. '
                             'Currently, {} ports are specified.'.format(str(len(nums))))
        filename = '{}.s{}p'.format(testname,str(len(nums)))
        self.pnaSetup(nums, **pnaparms)
        self.checkCal()
        
        for i in nums:
            for j in nums:
                s = 'S{}_{}'.format(i,j)
                sParms.append('S{}_{}'.format(i,j))
                measName = 'meas'+s 
                print(measName)
                pna.write("CALCulate:PARameter:DEFine:EXTended \'{}\',{}".format(measName,s))
                pna.write("DISPlay:WINDow{}:TRACe{}:FEED \'{}\'".format(i,j,measName))
        
        
#        for s in sParms:
#            measName = 'meas'+s 
#            print(measName)
#            pna.write("CALCulate:PARameter:DEFine:EXTended \'{}\',{}".format(measName,s))
#            pna.write('CALCulate1:PARameter:SELect \"{}\"'.format(measName))
#            pna.write("DISPlay:WINDow1:TRACe1:FEED \'{}\'".format(measName)) # duplicate trace number
        pna.timeout = 450000
        pna.write("SENSe1:SWEep:MODE SINGle") 
        pna.query('*OPC?')
        pna.timeout = 2000
#            pna.write("DISPlay:WINDow1:TRACe1:DELete")    
        print('Saving snp data on PNA in {}\\{}'.format(savedir,filename)) # query unterminated, also need to insert quotes around directory name
        pna.write(':CALCulate1:DATA:SNP:PORTs:SAVE \'{}\',\'{}\\{}\''.format(sPorts,savedir,filename)) #read 16 S parms in SNP format
        pna.query('*OPC?') 
        self.outputOff()

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
            print('Current calibration: {}'.format(calname))
            
    def getCalInfo(self):
        print(self.visaobj.query('SENSe1:CORRection:CSET:ACTivate? NAME'))
        print(self.visaobj.query('SENSe1:CORRection:CSET:TYPE:CATalog? NAME'))
        
    def getAvailCals(self):
        print(self.visaobj.query('CSET:CATalog?'))
