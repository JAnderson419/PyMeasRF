# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 11:48:27 2018

@author: ander906
"""

import matplotlib.pyplot as plt
import numpy as np



gateFile = r'F:\RFT\C1_dbmSweep_noDC\smus\C1_IdVd_gate.csv'
drainFile = r'F:\RFT\C1_dbmSweep_noDC\smus\C1_IdVd_drain.csv'

z = 1
gate = np.genfromtxt(gateFile, delimiter = ',')
drain = np.genfromtxt(drainFile, delimiter = ',')

gate = np.transpose(gate)
drain = np.transpose(drain)

vg = gate[0]
vdr = drain[0]
idr = drain[1]

vg = np.around(vg,decimals = 3)
change = np.where(np.diff(vg))[0]+1
change = np.append(change,[-1])
print(change)

plt.close('all')    
fig = plt.figure(1)
ax = fig.add_subplot(111)
if z:
    first = 1
    for x,i in enumerate(change):
        if first:
            first = 0
            ax.plot(vdr[0:i],idr[0:i]*1E6,'.')
        else:
            ax.plot(vdr[change[x-1]:i],idr[change[x-1]:i]*1E6,'.')
    ax.legend(vg[change])
else:
    ax.plot(vdr,idr*1E6,'.')
