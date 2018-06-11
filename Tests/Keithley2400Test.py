# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 15:27:42 2018
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""
from context import pymeasrf
import pymeasrf.Keithley2400 as k2400
import time

#drain = k2400.Keithley2400('GPIB1::25::INSTR')
drain = k2400.Keithley2400('GPIB0::25::INSTR')
#print(drain.visaobj.query(':SYSTem:BEEPer:STATe?'))
drain.visaobj.write(':SYSTem:BEEPer:STATe 0')
#print(drain.visaobj.query(':SYSTem:BEEPer:STATe?'))
drain.readError()
drain.smuSetup(30,.001)
print(drain.visaobj.query('SOURce:VOLTage:PROTection?')+' '+ 
      drain.visaobj.query('SENse:CURRent:PROTection?'))
drain.setVoltage(25)
time.sleep(3)
drain.outputOff()
drain.smuSetup(10,.001)
drain.setVoltage(1.2)
drain.visaobj.write(':FORMat:ELEMents VOLTage, CURRent, RESistance, TIME, STATus')
time.sleep(3)
drain.outputOff()
time.sleep(1)
drain.setVoltage(1.2)
time.sleep(3)
drain.resetTime()
data = drain.meas()
print(data)
#
#drain.visaobj.write(':ARM:COUNt 1')
#drain.visaobj.write(':TRIGger:COUNt 2500')
#drain.visaobj.write(':INITiate')
#time.sleep(3)
#drain.visaobj.write(':ABORt')
#data = drain.visaobj.query('FETCh?')
#print(data)

drain.disconnect()