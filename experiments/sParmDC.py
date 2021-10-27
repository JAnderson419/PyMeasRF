# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 17:29:00 2018

@author: Jackson Anderson
"""
import visa
import numpy as np
from context import pymeasrf
import pymeasrf.AgilentPNAXUtils as pnaUtils
import pymeasrf.Keithley2400 as k2400
import pymeasrf.pnaSMU as pnaSMU
import pymeasrf.smuMeas as smuMeas

def FETtestDC():


    compliance = 0.300 #Amps IE 105uA = 0.000105 
    maxVoltage = 20 #Maximum expected voltage to be used     
    testname = 'die4_A72' # name snp files will be saved as current file name format is as follows:
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'_
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    localsavedir = r'' # Directory where SMU data will be saved
    ############################# END User specified test Parameters ###############################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    
    ### DC Characterization ###
    idvgSMUs =  [k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = np.linspace(-15,0,16)),
                 k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [2]),
     #            k2400.Keithley2400('GPIB1::26::INSTR', label = 'source', voltages = [0])
                 ]
    for x in idvgSMUs: x.smuSetup(maxVoltage, compliance)
    idVgname = testname + '_IdVg'
    idVg = smuMeas.SMUmeas(idvgSMUs, localsavedir, idVgname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
    idVg.measure(smuX = 0, smuY = 1, smuZ = 0)
    for x in idvgSMUs: x.disconnect()
    
    idvdSMUs = [k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = np.linspace(0,2,21)), 
                k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = [-10,-8,-6,-5,-2,0]),  
     #           k2400.Keithley2400('GPIB1::26::INSTR', label = 'source', voltages = [0])
                ]
    for x in idvdSMUs: x.smuSetup(maxVoltage, compliance)
    idVdname = testname + '_IdVd'
    idVd = smuMeas.SMUmeas(idvdSMUs, localsavedir, idVdname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
    idVd.measure(smuX = 0, smuY = 0, smuZ = 1)
    for x in idvdSMUs: x.disconnect()
    
def rftTest():
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

    # user seperated list of SMUs to be connected. Voltages will be iterated over in order (first SMU iterates first).
    smus = [k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]), 
          k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]),  
          k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0,0.2,0.4,0.6,0.8])
           ]

    compliance = 0.200 #Amps IE 105uA = 0.000105 
    maxVoltage = 20 #Maximum expected voltage to be used 
    ports = '1,2,3,4' # string containing comma separated port numbers to be used
    delayTime = 3 #Time between setting SMU voltage and measurement in seconds
    postMeasDelay = 60
    trueMode = False
    DCtest = 1
    portPower = [-10]
    #phase = np.linspace(0,180,37)

    testname = 'run1_diex3y1_A2' # name snp files will be saved as current file name format is as follows:
    #'testname_VgX_XVdY_YVdrZ_Z.sXp'
    #So for example if testname is load and the Vg = 1.0V, Vdr=2.0V, Vd=3.0V and it is a 2 port measurement the file output will look as follows:
    #load_Vg1_0Vd2_0Vg3_0.s2p
    savedir = r'' # Directory where snp files will be saved on PNA
    localsavedir = r'' # Directory where SMU data will be saved
    ############################# END User specified test Parameters ###############################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################
    
    ### DC Characterization ###
    if DCtest:
        idvgSMUs =  [k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = np.linspace(0,0.8,81)),
                     k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]),
                     k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
                     ]
        for x in idvgSMUs: x.smuSetup(maxVoltage, compliance)
        idVgname = testname + '_IdVg'
        idVg = smuMeas.SMUmeas(idvgSMUs, localsavedir, idVgname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
        idVg.measure(smuX = 0, smuY = 1, smuZ = 1)
        for x in idvgSMUs: x.disconnect()
        
        idvdSMUs = [k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = np.linspace(0,0.8,81)), 
                    k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = np.linspace(0,0.8,9)),  
                    k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
                    ]
        for x in idvdSMUs: x.smuSetup(maxVoltage, compliance)
        idVdname = testname + '_IdVd'
        idVd = smuMeas.SMUmeas(idvdSMUs, localsavedir, idVdname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
        idVd.measure(smuX = 0, smuY = 0, smuZ = 1)
        for x in idvdSMUs: x.disconnect()
    
    ### RF Characterization ###
    for x in smus: x.smuSetup(maxVoltage, compliance)
    pna.pnaInitSetup()
    for p in portPower:
        name = '{}_{}dbm'.format(testname,p)
    #    for f in phase:
            #name = '{}_{}dbm_{}degOffset'.format(testname,p,f)
        test = pnaSMU.SParmMeas(smus, pna, ports, savedir, localsavedir, name, delayTime, postMeasDelay, smuMeasInter = 2.0, power = p, trueMode = trueMode)
        try:
        #      print('measure')
            test.measure()
        except visa.VisaIOError as e:
            print(e.args)
            pna.outputOff   
            for x in smus:
                 x.outputOff
         
    ### DC Characterization ###
    if DCtest:
        idvgSMUs =  [k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = np.linspace(0,0.8,81)),
                     k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]),
                     k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
                     ]
        for x in idvgSMUs: x.smuSetup(maxVoltage, compliance)
        idVgname = testname + '_IdVgEnd'
        idVg = smuMeas.SMUmeas(idvgSMUs, localsavedir, idVgname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
        idVg.measure(smuX = 0, smuY = 1, smuZ = 1)
        for x in idvgSMUs: x.disconnect()
        
        idvdSMUs = [k2400.Keithley2400('GPIB1::25::INSTR', label ='drain', voltages = np.linspace(0,0.8,81)), 
                    k2400.Keithley2400('GPIB1::24::INSTR', label= 'gate', voltages = np.linspace(0,0.8,9)),  
                    k2400.Keithley2400('GPIB1::26::INSTR', label = 'drive', voltages = [0])
                    ]
        for x in idvdSMUs: x.smuSetup(maxVoltage, compliance)
        idVdname = testname + '_IdVdEnd'
        idVd = smuMeas.SMUmeas(idvdSMUs, localsavedir, idVdname, delay = 0, measTime = 0, postMeasDelay = 0, smuMeasInter = 1.0)
        idVd.measure(smuX = 0, smuY = 0, smuZ = 1)
        for x in idvdSMUs: x.disconnect()
        
    for x in smus: x.disconnect()
    pna.disconnect()
    
    exit


def main():

    rftTest()
#     FETtestDC()
    
    
if __name__ == "__main__":
    main()
