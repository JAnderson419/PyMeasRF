# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 15:27:42 2018
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

import Keithley2400 as k2400
import time

drain = k2400.Keithley2400('GPIB1::25::INSTR')
#drain.readError()
drain.smuSetup(10,.001)
drain.setVoltage(1.2)
time.sleep(3)
drain.outputOff()
time.sleep(1)
drain.setVoltage(1.2)
time.sleep(3)
drain.disconnect()