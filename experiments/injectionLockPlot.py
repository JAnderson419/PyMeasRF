# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:52:04 2018

@author: Jackson Anderson
"""

import sys
import re
import os
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import EngFormatter
import numpy as np


datadir = r'DataSaveDirHere'


harmonic = []
Voff = []
Vamp = []
data = []
keys = ['filename','measName', 'harmonic', 'injectionFreq', 'Voffset', 'Vamplitude']
files = os.listdir(datadir)

plt.close('all')

for i, f in enumerate(files):
    if re.search('\.csv',f):
        m = re.search(r'(.*)_([\d\.]*)f0_([-\d\.]*)Voff_([\d\.]*)Vamp_([\d\.]*)Freq.csv', f)
        harmonic.append(float(m.group(2)))
        Voff.append(float(m.group(3)))
        Vamp.append(float(m.group(4)))
        vals = [f, m.group(1), float(m.group(2)), float(m.group(5)), float(m.group(3)), float(m.group(4))]    
        data.append(dict(zip(keys, vals)))

    
[harmonic, Voff, Vamp] = [sorted(list(set(x))) for x in [harmonic, Voff, Vamp]]

for h in harmonic: 
    fig2, axarr2 = plt.subplots(len(Voff), len(Vamp), figsize = [9,6],
                               sharex='col', sharey='row', num=2)
    fig2.subplots_adjust(right=0.8)
    cbar_ax = fig2.add_axes([0.85, 0.15, 0.05, 0.7])

    fig3, axarr3 = plt.subplots(len(Voff), len(Vamp), figsize = [9,6],
                               sharex='col', sharey='row', num=3)
    for i,o in enumerate(Voff):
        for j,a in enumerate(Vamp):
            X = []
            Y = []
            Z = []
            for d in data:
                if d['harmonic'] == h and d['Voffset'] == o and d['Vamplitude'] == a:
                    try:
                        x, z = np.loadtxt(os.path.join(datadir, d['filename']),
                                         delimiter=",", unpack = True)                    
                    except ValueError as e:
                        print('Cannot read {}. '.format(d['filename'])+str(e))
                        continue
                    X = x
                    Y.append([d['injectionFreq']])
                    try: 
                        z = np.asfarray(z)
                        Z.append(z)
                    except ValueError as e:
                        print('''Error converting RF Powers from V$_{{offset}}$ = {} V, 
                              V$_{{pp}}$ = {} V, N = {} to array. \n{}. \n{}'''
                              .format(o, a, h, e, z))
                    z = np.ma.asarray(z)
                    Z.append(z)
                else:
                    continue
            X = np.asfarray(X) - 16E6
            Y = np.ndarray.flatten(np.asfarray(Y))
            Y = Y - np.average(Y)
            sortorder = np.argsort(Y,0)            
            try:
                Z = np.asfarray(Z)
            except ValueError as e:
                print('''Error converting RF Powers from V$_{{offset}}$ = {} V, 
                      V$_{{pp}}$ = {} V, N = {} to array. \n{}. \n{}'''
                      .format(o, a, h, e, Z))
                continue
            X, Y = np.meshgrid(X, Y)
            [X, Y, Z] = [np.array(j)[sortorder] for j in [X, Y, Z]]
            
            # Plot data for individual combination
            fig = plt.figure(1, figsize = [9,6])
            plt.clf()
            ax1 = fig.add_subplot(111)
            cs = ax1.contourf(X,Y,Z, 100, cmap=cm.jet)
            ax1.xaxis.set_major_formatter(EngFormatter(unit=''))
            ax1.yaxis.set_major_formatter(EngFormatter(unit=''))
            ax1.set_xlabel('$\Delta$ From 16 MHz (Hz)', fontsize='large')
            ax1.set_ylabel('$\Delta$ Injection from N*16 MHz (Hz)', fontsize='large')
            title = 'V$_{{offset}}$ = {} V, V$_{{pp}}$ = {} V, N = {}'.format(o,a, h)
            ax1.set_title(title, fontsize='large')
            cbar = plt.colorbar(cs)
            cbar.ax.set_ylabel('RF Power (dBm)', fontsize='large')
            
            plt.savefig(os.path.join(datadir,title)+r'.svg')
            plt.savefig(os.path.join(datadir,title)+r'.png')
#            
            cs.set_clim(-140,20)
            plt.savefig(os.path.join(datadir,title)+r'scaleFixed.svg')
            plt.savefig(os.path.join(datadir,title)+r'scaleFixed.png')            
            
            #  Add subplot to tiled image
            for k, axarr in enumerate([axarr2, axarr3]):
                if i == len(Voff)-1:
                    axarr[i,j].set_xlabel('V$_{{pp}}$={} V'.format(a))
                if j == 0:
                    axarr[i,j].set_ylabel('V$_{{bias}}$={} V'.format(o))
                cs2 = axarr[i,j].contourf(X,Y,Z, 100, cmap=cm.jet)
                axarr[i,j].set_xticklabels([])
                axarr[i,j].set_yticklabels([])
                if k == 0:
                    cs2.set_clim(-140,20)
                    if i== len(Voff)-1 and j== len(Vamp)-1:   
                        cbar2 = fig2.colorbar(cs2, cax=cbar_ax)
                        cbar2.ax.set_ylabel('RF Power (dBm)', fontsize='large')

    tileTitle = 'N={} Harmonic Injection'.format(h) 
    tileTitleFixed = tileTitle + ', Shared Color Scale'         
    fig2.suptitle('\n'+tileTitleFixed, fontsize='x-large') 
    fig3.suptitle('\n'+tileTitle, fontsize='x-large') 
        
    plt.figure(2)
    plt.savefig(os.path.join(datadir, tileTitle + r'scaleFixed.svg'))
    plt.savefig(os.path.join(datadir, tileTitle + r'scaleFixed.png'))
    plt.clf()
    plt.figure(3)
    plt.savefig(os.path.join(datadir, tileTitle + r'.svg'))
    plt.savefig(os.path.join(datadir, tileTitle + r'.png'))   
    plt.clf()
    