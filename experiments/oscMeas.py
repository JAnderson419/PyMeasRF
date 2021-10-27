# -*- coding: utf-8 -*-

from context import pymeasrf
from os.path import join
import time
import pymeasrf.AgilentN9030A as pxaUtil
import pymeasrf.Agilent33220a as awgUtil
import numpy as np
import matplotlib.pyplot as plt

def oscMeas():
    plot = 0
    savedir = r'SaveDir'
    testname = r'test'
    vpp = [0.02,0.1,0.5,1]
    vOffset = [-0.93, -0.75, -0.50, 0]
    f0 = 16.000070E6 # Hz
    spanf = 300 # Hz
    nfreq = [0.5, 2, 3, 4]
    
#    vpp = np.concatenate((vpp,vpp[-2::-1]))
#    vOffset = np.concatenate((vOffset,vOffset[-2::-1]))
#    print (vpp)
#    print (vOffset)

    
    pxa = pxaUtil.AgilentN9030A('TCPIP0::A-N9030A-31424::inst0::INSTR')
    awg = awgUtil.Agilent33220a('TCPIP0::169.254.2.20::inst0::INSTR')
    data = {}    

    for h, nf in enumerate(nfreq):
        fDrive = np.linspace(nf*f0-spanf/2,nf*f0+spanf/2,61)
        fDrive = np.concatenate((fDrive, fDrive[-2::-1]))
#        print (fDrive)
        for i, voff in enumerate(vOffset):
            for j, vamp in enumerate(vpp):
                if voff == 0 and vamp == 1: next
                for k, f in enumerate(fDrive):
                    awg.basicOutput('SIN',f,vamp,voff)
                    time.sleep(5)
                    data['raw'] = pxa.read('SAN')
                    data['freq'] = data['raw'].split(',')[0::2]
                    data['mag'] = data['raw'].split(',')[1::2]
                    filename = join(savedir,'{}_{}f0_{}Voff_{}Vamp_{}Freq.csv'.format(testname,nf,voff,vamp,f))
                    print('Saving data on local PC in {}'.format(filename))
                    print(filename)
                    f =  open(filename, 'w')
                    for q, l in enumerate(data['freq']):
                        f.write('{},{}\n'.format(data['freq'][q],data['mag'][q]))
                    f.close()
    pxa.disconnect()
    awg.disconnect()
            
    
  #  print(data['freq'],data['mag'])
    
    if plot:
        fig = plt.figure(1)
        plt.cla()
        ax = fig.add_subplot(111)
        ax.plot(data['freq'],data['mag'],'-',markersize=10)
        ax.set_xticks(ax.get_xticks()[::500])
        ax.set_yticks(ax.get_yticks()[::100])
        ax.set_xlabel('Frequency [kHz]')
        ax.set_ylabel('Signal Magnitude [dBm]')

    
def main():
    oscMeas()
    exit
    
main()