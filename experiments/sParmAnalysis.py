# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 12:04:45 2018

@author: Jackson Anderson
"""
import re
import os
import copy as cp
from warnings import warn
from cycler import cycler
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np
import skrf as rf
# pylint: disable=C0103

'''
This program inputs raw snp files and provides many different functions for
viewing them. It is set up for plotting differential data and can handle normal
or mixed mode s parameters as data input. Deembedding with an open will also
be done if deembed is set to true and a directory of open files is given. The
code will scan the open directory for a file with identical DC bias conditions
and save the deembedded s parameters in a seperate file for easy export to
other programs such as ADS or Matlab.
'''


datadir = r'D:\19_MIDAS_14LPP'  # location of device SnP files
opendir = r''  # location of device open deembedding files

# Device overview plot
filterRegex = r'2019_MIDAS_14LPP_die1_18.*'  # regex to filter SNP files in datadir
regexSinglePlot = r'2019_MIDAS_14LPP_die1_18_ITMS_-10dbm_6_drain0_3V_gate0_8V_drive0_8V'  # regex to select single device for detailed plots


####################
# User Inputs ######
####################


mixedmodeport = [1, 3, 0, 2]  # 1+, 1-, 2+, 2-
# Default is 13 input, 24 output.
debug = False
deembed = 0     # 0 - no deembedding
                # 1- Deembeds data with open that has matching bias conditions,
                # 2- Deembeds data with open & short - Work In Progress
bal = False  # Set true if importing true mode SNP data

### plot options ###
plotS = 1  # Plots singled ended and differential reflection parameters  for regexSinglePlot
plotZ = 1  # Plots input impedances: re, im, and mag  for regexSinglePlot
plotSmith = 0  # Plots reflection parameters  for regexSinglePlot
plot21 = 1  # Plots Sdd21 and Sdd12: mag, phase, and ifft  for regexSinglePlot
plot21all = 1  # Plots Smm21 mag for regexSinglePlot
plotgmddRatio = 0  # Plots ratio of gmdd to gmcc, gmdc, and gmcd  for regexSinglePlot
plotgm = 1  # Plots gmdd for filterRegex

gmrel = False  # controls whether gmddrel plot is relative or not - data controlled by filterRegex
nsmoothgm = 11  # smooths gm plots (gm, gmddratio, gmddrel) with rolling average
####################

opendir = os.path.join(datadir, 'open')
shortdir = os.path.join(datadir, 'short', 'short_test')


def filteredReadDir(directory):
    files = os.listdir(directory)
    # filter files to snp or pickled ntwk, removing file extension   
    files = [m.group(1) for f in files for m in [re.search(r'(.*)\.(ntwk|[sS]\d[pP])$',f)] if m]
    # remove duplicates (if data saved in multiple formats)
    files = list(set(files)) 
    files.sort()
    return files


def open_Network(filename):
    '''Checks to see if pickled data exists, if not loads from s4p'''
    try:
        d = rf.Network(filename+'.ntwk')
    except FileNotFoundError:
        print('Loading from s4p.')
        d = rf.Network(filename+'.s4p')
    return d


def smooth(y, box_pts):
    '''
    Rolling average fn from convolution. From scrx2.

    See https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    '''
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def gmm_reorder(m):
    '''
    Reorders data from form 11 12 with each submatrix as dd dc
                            21 22                        cd cc
    to form dd dc with each submatrix as 11 12
            cd cc                        21 22

    '''
    b = np.array([1, 0, 0, 0,
                  0, 0, 1, 0,
                  0, 1, 0, 0,
                  0, 0, 0, 1]).reshape(4, 4)
    m = b.dot(m.dot(b))
    return m


def open_deembed(data, data_open, datadir=None):
    '''
    Subtracts admittance of open from that of device and saves results in new
    network n. If save_deembedded is defined, saves a copy of the deembedded
    network in snp format.
    '''
    d = open_Network(data)
    o = open_Network(data_open)
    n = rf.Network()
    n.frequency = d.frequency
    n.z0 = d.z0
    n.name = d.name
    ### Time Gate before Deembed ###
#    for i in range(len(d.s[0,:,0])):
#        for j in range(len(d.s[0,0,:])):
#            dsub = rf.Network()
#            osub = rf.Network()
#            dsub.s = np.zeros((len(d.f),1,1))
#            osub.s = np.zeros((len(o.f),1,1))
#            dsub.s[:,0,0] = d.s[:,i,j]
#            osub.s[:,0,0] = o.s[:,i,j]
#            d.s[:,i,j] = dsub.s.time_gate(center=0,span=15)
#            o.s[:,i,j] = osub.s.time_gate(center=0,span=15)
#    d.y = rf.s2y(d.s)
#    o.y = rf.s2y(o.s)
    ################################
#    d.y = rf.z2y(d.z)
#    o.y = rf.z2y(o.z)
    n.y = d.y - o.y
    n.s = rf.y2s(n.y)
    n.z = rf.y2z(n.y)
    if datadir:
        savedir = os.path.join(datadir, 'deembedded_open')
        if not os.path.isfile(os.path.join(savedir, n.name)):
            n.write_touchstone(dir=savedir)
    return n


def short_deembed(data, data_open, data_short, datadir=None):
    '''
    Subtracts admittance of open from that of device and short, then subtracts
    dembeded short impedance from device and saves results in new
    network n. If save_deembedded is defined, saves a copy of the deembedded
    short and device networks in snp format.
    '''
    d = open_deembed(data, data_open, datadir)
    # s = open_deembed(data_short, data_open, datadir)
    s = open_Network(data_short)
    n = rf.Network()
    n.frequency = d.frequency
    n.z0 = d.z0
    n.name = d.name
    n.z = d.z-s.z
    n.s = rf.z2s(n.z)
    n.y = rf.y2z(n.z)
    if datadir:
        savedir = os.path.join(datadir, 'deembedded_openshort')
        if not os.path.isfile(os.path.join(savedir, n.name)):
            n.write_touchstone(dir=savedir)
    return n


def search_filelist(filelist, bias_regex, power_regex = None):
    '''
    Attempts to find match for bias and power regex in a list of filenames
    '''
    for f in filelist:
        if re.search(bias_regex, f): # find DC bias match
            if power_regex != None: # match power if specified
                if re.search(m.group(1), f):
                    return f
            else:
                warn('No Power Match Found. Using '+f)
                return f
        else:
            warn('No DC Bias match found. Using '+f)
            return f

###################################################
    # End of Functions ############################
    ###############################################


def main():
    
    data = []
    keys = ['filename', 'data', 'mmdata']
    
    gmdddir = os.path.join(datadir, 'gmdd')

    files = filteredReadDir(datadir)
    
    for i, f in enumerate(files):
        m = re.search(r'(-*\d+dbm)?.*((drain|gate|drive).*(drain|gate|drive).*(drain|gate|drive).*V).*$', f)
        if debug:
            print(f)
    #    if m:
        if re.search(filterRegex, f):
            if not os.path.exists(gmdddir):
                os.makedirs(gmdddir)
            if deembed:
                subdirs = []
                opendata = None
                shortdata = None
    
                # Define required subdirs for each type, subdir of final deembedded
                # data coming first in the list
                if deembed == 1:
                    subdirs = ['deembedded_open']
                elif deembed == 2:
                    subdirs = ['deembedded_openshort', 'deembedded_open']
                else:
                    raise ValueError('Undefined deembedding type. Check value of deembed.')
                # Create dirs for deembedded data if they doesn't exist
                for s in subdirs:
                    savedir = os.path.join(datadir, s)
                    if not os.path.exists(savedir):
                        os.makedirs(savedir)
                # Check if file has been deembedded prior
                if os.path.isfile(os.path.join(datadir, subdirs[0], f)):
                    rfdata = open_Network(os.path.join(datadir, subdirs[0], f))
    
                else: # search for suitable open in opendir
                    openfiles = filteredReadDir(opendir)
                    opendata = search_filelist(openfiles, m.group(2), m.group(1))
                    if deembed == 1:
                        rfdata = open_deembed(os.path.join(datadir, f),
                                              os.path.join(opendir, opendata),
                                              datadir)
                    elif deembed == 2:
                        shortfiles = os.listdir(shortdir)
                        # shortdata = search_filelist(shortfiles, m.group(2), m.group(1))
                        shortdata = 'Sept18run_die1_10Ghz_short_-10dbm_1_drain0_0V_gate0_0V_drive0_0V.s4p'
                        # print(shortdata,opendata)
                        rfdata = short_deembed(os.path.join(datadir, f),
                                               os.path.join(opendir, opendata),
                                               os.path.join(shortdir, shortdata),
                                               datadir)
    
            # using raw rfdata - no deembedding
            else:
                rfdata = open_Network(os.path.join(datadir, f))
#                if not os.path.isfile(os.path.join(savedir, rfdata.name)):
#                    rfdata.write(dir=savedir)
    
            if bal:
                # raw data is mmdata in form 11 12 with each submatrix as dd dc
                #                            21 22                        cd cc
                for i, freq in enumerate(rfdata.f):
                    # reorder 4x4 matrix for each freq seperately
                    # to decrease memory usage
                    rfdata.s[i, :, :] = gmm_reorder(rfdata.s[i, :, :])
                sedata = cp.deepcopy(rfdata)
                sedata.gmm2se(2)
                sedata.renumber([0, 1, 2, 3], mixedmodeport)
                vals = [f, sedata, rfdata]
            else:
                mmdata = cp.deepcopy(rfdata)
                # renumber ports for single ended to differential conversion
                mmdata.renumber([0, 1, 2, 3], mixedmodeport)
                mmdata.se2gmm(2)
                # mmdata now in form  Sdd  Sdc
                #                     Scd  Scc
                vals = [f, rfdata, mmdata]
            data.append(dict(zip(keys, vals)))
    
    plt.close('all')
    
    ### One-time plot setup
    if filterRegex:
        fig = plt.figure(1)
        ax1 = fig.add_subplot(211)
        ax12 = fig.add_subplot(212, sharex=ax1)
    
    if plotgm:
        fig2 = plt.figure(2)
        ax2 = fig2.add_subplot(111)
    
    if plotgmddRatio:
        fig4 = plt.figure(4)
        ax41 = fig4.add_subplot(311, sharex=ax1)
        ax42 = fig4.add_subplot(312, sharex=ax1)
        ax43 = fig4.add_subplot(313, sharex=ax1)
        ax412 = ax41.twinx()
        ax422 = ax42.twinx()
        ax432 = ax43.twinx()
    
    if plotS:
        fig3 = plt.figure(3)
        ax3 = fig3.add_subplot(111)
        fig8 = plt.figure(8)
        ax8 = fig8.add_subplot(111)
    
    if plotZ:
        fig7 = plt.figure(7)
        ax7 = fig7.add_subplot(311, sharex=ax1)
        ax72 = fig7.add_subplot(312, sharex=ax1)
        ax73 = fig7.add_subplot(313, sharex=ax1)
    
    if plotSmith:
        fig5 = plt.figure(5)
        ax5 = fig5.add_subplot(111)
    
    if plot21:
        fig9 = plt.figure(9)
        ax9 = fig9.add_subplot(311)
        ax92 = fig9.add_subplot(312)
        ax93 = fig9.add_subplot(313)
    
    if plot21all:
        fig10 = plt.figure(10)
        ax10 = fig10.add_subplot(111)
    
    plotData = []
    for d in data:
        if re.search(filterRegex, d['filename']):
            plotData.append(d)
        if re.search(regexSinglePlot, d['filename']):
    
            if plotS:
                ax3.set_title('Singled Ended S Params ' + d['filename'])
                ax3.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                d['data'].plot_s_db(m=0, n=0, ax=ax3)
                d['data'].plot_s_db(m=1, n=1, ax=ax3)
                d['data'].plot_s_db(m=2, n=2, ax=ax3)
                d['data'].plot_s_db(m=3, n=3, ax=ax3)
                fig3.autofmt_xdate(rotation=20, ha='right')
    
    
                ax8.set_title('Mixed Mode S Params ' + d['filename'])
                d['mmdata'].plot_s_db(m=0, n=0, ax=ax8, label='Sdd11')
                d['mmdata'].plot_s_db(m=1, n=1, ax=ax8, label='Sdd22')
                d['mmdata'].plot_s_db(m=2, n=2, ax=ax8, label='Scc11')
                d['mmdata'].plot_s_db(m=3, n=3, ax=ax8, label='Scc22')
                ax8.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                fig8.autofmt_xdate(rotation=20, ha='right')
    #
            if plot21:
                ax9.set_title(d['filename'])
                d['mmdata'].plot_s_db(m=1, n=0, ax=ax9, label='Sdd21')
                d['mmdata'].plot_s_db(m=0, n=1, ax=ax9, label='Sdd12')
                d['mmdata'].plot_s_db_time(m=1, n=0, ax=ax92, label='Sdd21')
                d['mmdata'].plot_s_db_time(m=0, n=1, ax=ax92, label='Sdd12')
                d['mmdata'].plot_s_deg_unwrap(m=1, n=0, ax=ax93, label='Sdd21')
                d['mmdata'].plot_s_deg_unwrap(m=0, n=1, ax=ax93, label='Sdd12')
                ax9.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax93.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                # following snippet taken from autofmt_xdate
                # Preserves all subplot xaxis since the ifft is in time domain
                for ax in fig9.get_axes():
                    for label in ax.get_xticklabels():
                        label.set_ha('right')
                        label.set_rotation(20)
    #            ax93.plot(d['mmdata'].f,abs(d['mmdata'].s21.group_delay[:,0,0]), label = 'Sdd21 Group Delay')
    #            ax93.plot(d['mmdata'].f,abs(d['mmdata'].s12.group_delay[:,0,0]), label = 'Sdd12 Group Delay')
            if plot21all:
                ax10.set_title(d['filename'])
                d['mmdata'].plot_s_db(m=1, n=0, ax=ax10, label='Sdd21')
                d['mmdata'].plot_s_db(m=1, n=2, ax=ax10, label='Sdc21')
                d['mmdata'].plot_s_db(m=3, n=0, ax=ax10, label='Scd21')
                d['mmdata'].plot_s_db(m=3, n=2, ax=ax10, label='Scc21')
                d['mmdata'].plot_s_db(m=0, n=1, ax=ax10, label='Sdd12')
                d['mmdata'].plot_s_db(m=0, n=3, ax=ax10, label='Sdc12')
                d['mmdata'].plot_s_db(m=2, n=1, ax=ax10, label='Scd12')
                d['mmdata'].plot_s_db(m=2, n=3, ax=ax10, label='Scc12')
                ax10.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                fig10.autofmt_xdate(rotation=20, ha='right')
    
            ## gm calculations ##
            gmdd = smooth(rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 1, 0]-rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 0, 1], nsmoothgm)
            gmdc = smooth(rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 1, 2]-rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 0, 3], nsmoothgm)
            gmcd = smooth(rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 3, 0]-rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 2, 1], nsmoothgm)
            gmcc = smooth(rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 3, 2]-rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 2, 3], nsmoothgm)
            if plotgm:
    
    #            np.savetxt(os.path.join(gmdddir,'absgmdd_{}.csv'.format(d['filename'])),np.transpose([d['mmdata'].f,abs(gmdd)]), delimiter =',')
    
                ax2.semilogy(d['mmdata'].f, np.abs(gmdd), label='|Y$_{dd21}$ - Y$_{dd12}$|')
                ax2.semilogy(d['mmdata'].f, np.abs(gmdc), label='|Y$_{dc21}$ - Y$_{dc12}$|')
                ax2.semilogy(d['mmdata'].f, np.abs(gmcd), label='|Y$_{cd21}$ - Y$_{cd12}$|')
                ax2.semilogy(d['mmdata'].f, np.abs(gmcc), label='|Y$_{cc21}$ - Y$_{cc12}$|')
    
                ax2.xaxis.set_major_formatter(EngFormatter(unit='GHz'))
                ax2.set_ylabel('Transconductance [S]')
                ax2.set_title(d['filename'])
                ax2.legend(fontsize='x-large')
                fig2.autofmt_xdate(rotation=20, ha='right')
    
            ### gm ratio plotting ###
            if plotgmddRatio:
                ax41.set_title(d['filename'])
                ax41.semilogy(d['mmdata'].f, (np.abs(gmdd)/np.abs(gmcc)))
                ax41.set_ylabel('$\\frac{|gm_{dd}|}{|gm_{cc}|}$', color='b', fontsize='x-large')
                ax41.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax412.semilogy(d['mmdata'].f, np.abs(gmdd), 'r--', alpha=0.5)
                ax412.set_ylabel('|gm$_{dd}$| [S]', color='r')
                ax412.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
    
                ax42.semilogy(d['mmdata'].f, (np.abs(gmdd)/np.abs(gmdc)))
                ax42.set_ylabel('$\\frac{|gm_{dd}|}{|gm_{dc}|}$', color='b', fontsize='x-large')
                ax42.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax422.semilogy(d['mmdata'].f, np.abs(gmdd), 'r--', alpha=0.5)
                ax422.set_ylabel('|gm$_{dd}$| [S]', color='r')
                ax422.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
    
                ax43.semilogy(d['mmdata'].f, (np.abs(gmdd)/np.abs(gmcd)))
                ax43.set_ylabel('$\\frac{|gm_{dd}|}{|gm_{cd}|}$', color='b', fontsize='x-large')
                ax43.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax432.semilogy(d['mmdata'].f, np.abs(gmdd), 'r--', alpha=0.5)
                ax432.set_ylabel('|gm$_{dd}$| [S]', color='r')
                ax432.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                fig4.autofmt_xdate(rotation=20, ha='right')
            if plotZ:
                ax7.set_title('SE Z params ' + d['filename'])
                d['data'].plot_z_re(m=0, n=0, ax=ax7, label='Z11')
                d['data'].plot_z_im(m=0, n=0, ax=ax72, label='Z11')
                d['data'].plot_z_mag(m=0, n=0, ax=ax73, label='Z11')
                d['data'].plot_z_re(m=1, n=1, ax=ax7, label='Z22')
                d['data'].plot_z_im(m=1, n=1, ax=ax72, label='Z22')
                d['data'].plot_z_mag(m=0, n=0, ax=ax73, label='Z22')
                d['data'].plot_z_re(m=2, n=2, ax=ax7, label='Z33')
                d['data'].plot_z_im(m=2, n=2, ax=ax72, label='Z33')
                d['data'].plot_z_mag(m=0, n=0, ax=ax73, label='Z33')
                d['data'].plot_z_re(m=3, n=3, ax=ax7, label='Z44')
                d['data'].plot_z_im(m=3, n=3, ax=ax72, label='Z44')
                d['data'].plot_z_mag(m=0, n=0, ax=ax73, label='Z44')
                ax7.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax72.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
                ax73.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
            if plotSmith:
                ax5.set_title(d['filename'])
                d['data'].plot_s_smith(m=0, n=0, ax=ax5, draw_labels=True, label='S11')
                d['data'].plot_s_smith(m=1, n=1, ax=ax5, draw_labels=True, label='S22')
                d['data'].plot_s_smith(m=2, n=2, ax=ax5, draw_labels=True, label='S33')
                d['data'].plot_s_smith(m=3, n=3, ax=ax5, draw_labels=True, label='S44')
    
    #
    if plotData:
    
        plotData = sorted(plotData, key=lambda k: k['filename'])
        gmddref = np.zeros(len(plotData[0]['data'].f))
        ls = ['-', '--', ':']
        if len(plotData) > 7:
            colormap = plt.cm.tab10
            ax1.set_prop_cycle(cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(plotData))]))
            ax12.set_prop_cycle(cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(plotData))]))
        if len(plotData) > 18:
            legendFont = 'xx-small'
        elif len(plotData) > 12:
            legendFont = 'x-small'
        elif len(plotData) > 8:
            legendFont = 'small'
        else:
            legendFont = 'medium'
        for i, d in enumerate(plotData):
            gmdd = rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 1, 0]-rf.s2y(d['mmdata'].s, d['mmdata'].z0)[:, 0, 1]
            if not os.path.isfile(os.path.join(gmdddir, 'gmdd_{}.csv'.format(d['filename']))):
#                np.savetxt(os.path.join(gmdddir, 'absgmdd_{}.csv'.format(d['filename'])), np.transpose([d['mmdata'].f, abs(gmdd)]), delimiter =',')
                np.savetxt(os.path.join(gmdddir, 'gmdd_{}.csv'.format(d['filename'])), np.transpose([d['mmdata'].f, gmdd]), delimiter =',')
            if gmrel:
                if not np.count_nonzero(gmddref):
                    gmddref = gmdd
                    ax1.set_title('Gmdd referenced to {}'.format(d['filename']))
                ax1.plot(d['mmdata'].f, np.abs(smooth(gmdd-gmddref, nsmoothgm)), alpha=0.7, lw=3, linestyle=ls[i%len(ls)], label=d['filename'])
                ax12.plot(d['mmdata'].f, np.unwrap(np.angle(smooth(gmdd-gmddref, nsmoothgm))*180/np.pi), alpha=0.7, label=d['filename'])
                ax1.set_ylabel('|gm$_{dd}$-gm$_{ddref}$| [S]')
                ax12.set_ylabel('Phase gm$_{dd}$-gm$_{ddref}$, [deg]')
            else:
                ax1.set_title('Gmdd')
                ax1.plot(d['mmdata'].f, smooth(np.abs(gmdd), nsmoothgm), alpha=0.7, lw=3, linestyle=ls[i%len(ls)], label=d['filename'])
                ax12.plot(d['mmdata'].f, np.unwrap(np.angle(smooth(gmdd, nsmoothgm))*180/np.pi), alpha=0.7, label=d['filename'])
                ax1.set_ylabel('|gm$_{dd}$| [S]')
                ax12.set_ylabel('Phase gm$_{dd}$, [deg]')
    
        ax1.yaxis.set_major_formatter(EngFormatter())
        ax1.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        ax12.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        ax12.set_xlabel('Frequency')
        fig.autofmt_xdate(rotation=20, ha='right')
        ax1.legend(fontsize=legendFont)
    
    if plotZ:
        ax7.legend()
        ax7.set_ylabel('Real Impedance [Ohms]')
        ax72.set_ylabel('Imaginary Impedance [Ohms]')
        ax7.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        ax72.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        fig7.autofmt_xdate(rotation=20, ha='right')

if __name__ == '__main__':
    main()