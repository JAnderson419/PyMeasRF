# -*- coding: utf-8 -*-
"""
@author: Jackson Anderson
ander906@purdue.edu
HybridMEMS
"""

import AgilentPNAXUtils as pnaUtils

pna = pnaUtils.AgilentPNAx('TCPIP0::192.168.1.1::inst0::INSTR')
pna.getCalInfo()
pna.disconnect()

exit