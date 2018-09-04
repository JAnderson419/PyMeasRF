# -*- coding: utf-8 -*-

from context import pymeasrf
import pymeasrf.AgilentN9030A as pxaUtil
import pymeasrf.Agilent33220a as awgUtil
import numpy as np
import matplotlib.pyplot as plt

def oscMeas():
    plot = 0
    savedir = r'C:\Users\BRKAdmin\Documents\Shreyas'
    testname = r'test'
    vpp = [0.02,0.1,0.5,1]
    vOffset = np.linspace(-0.7,0,1)
    fDrive = np.linspace(16000.200,16000.300,20)
    
    vOffset = np.concatenate((vOffset,vOffset[-2::-1]))
    fDrive = np.concatenate((fDrive,fDrive[-2::-1]))
    print (vOffset)
    print (fDrive)
    
    pxa = pxaUtil.AgilentN9030A('TCPIP0::A-N9030A-31424::inst0::INSTR')
    awg = awgUtil.Agilent33220a('TCPIP0::169.254.2.20::inst0::INSTR')
    data = {}    

    for i,voff in enumerate(vOffset):
        for j,f in enumerate(fDrive):
            awg.basicOutput('SIN',f,0.05,voff)
            data['raw'] = pxa.read('SAN')
            data['freq'] = data['raw'].split(',')[0::2]
            data['mag'] = data['raw'].split(',')[1::2]
            filename = '{}\\{}_{}_{}_{}Voff_{}Freq.csv'.format(savedir,testname,i,j,voff,f)
            print('Saving data on local PC in {}'.format(filename))
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