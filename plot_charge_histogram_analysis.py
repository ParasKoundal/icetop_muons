#!/usr/bin/env python

# This script makes plots that analyze the histogram of charge past a certain
# distance. It breaks this signal up into HLC and SLC components, as well as 
# muon vs non-muon components

import numpy as np
from ShowerClass import *
import matplotlib.pyplot as plt
from matplotlib import pylab

import os

# SETTINGS -----------------------------------------------
element  = 1   # set 1 for protons, 2 for iron
distance = 300 # set distance where we make cut on signal
E_lowerlimit = 0#10**(15.5) # lower limit on primary energy
E_upperlimit = 10**100#10**(16) # upper limit on primary energy
# --------------------------------------------------------


# where to find data
data_location = './data/'

#load the data
if element == 1:
    Data = np.load(data_location+"proton_showers.npy")
elif element == 2:
    Data = np.load(data_location+"iron_showers.npy")
else:
    print "Please set 'element' to either 1 (proton) or 2 (iron)"
    exit()


muontot  = [] # total muon signal
muonHLC  = [] # muon HLCs
muonSLC  = [] # muon SLCs
othertot = [] # total signal from other particles
otherHLC = [] # HLCs from other particles
otherSLC = [] # SLCs from other particles
HLC      = [] # all HLCs
SLC      = [] # all SLCs

for shower in Data:
    if shower.Primary.Energy > E_lowerlimit and \
    shower.Primary.Energy < E_upperlimit:
        for i in range(len(shower.Signals.Tank)): # loop through every tank

            # only tanks far enough from the core AND containing some charge
            if shower.Signals.LatDist[i] > distance and \
            shower.Signals.TotalPE[i] > 0:

                # scale the PE by (total VEM)/(total PE)
                scale = shower.Signals.TotalVEM[i]/shower.Signals.TotalPE[i]
                muon_signal  = scale*shower.Signals.MuonPE[i]
                muontot.append(muon_signal)
                other_signal = scale*shower.Signals.OtherPE[i]
                othertot.append(other_signal)

                if shower.Signals.HLCVEM[i] > 0: # check if this is an HLC
                    HLC.append(shower.Signals.HLCVEM[i])
                    muonHLC.append(muon_signal)
                    otherHLC.append(other_signal)

                elif shower.Signals.SLCVEM[i] > 0: # check if this is an SLC
                    SLC.append(shower.Signals.SLCVEM[i])
                    muonSLC.append(muon_signal)
                    otherSLC.append(other_signal)


# Take log of all the data
muontot_log  = [np.log10(i) for i in muontot if i != 0]
muonHLC_log  = [np.log10(i) for i in muonHLC if i != 0]
muonSLC_log  = [np.log10(i) for i in muonSLC if i != 0]

othertot_log = [np.log10(i) for i in othertot if i != 0]
otherHLC_log = [np.log10(i) for i in otherHLC if i != 0]
otherSLC_log = [np.log10(i) for i in otherSLC if i != 0]

HLC_log      = [np.log10(i) for i in HLC if i != 0]
SLC_log      = [np.log10(i) for i in SLC if i != 0]



# Create the figure

plt.rcParams["figure.figsize"] = [20,8.5]
fig,(ax1,ax2) = plt.subplots(1,2)

# Left Side
# --------------

# Muon and Other particle signals
ax1.hist(muontot_log,bins=40,range=[-1.5,1.5],histtype='step',
                linewidth=1,color='red',label='Muon signal (HLC+SLC)',zorder=2)
ax1.hist(othertot_log,bins=40,range=[-1.5,1.5],histtype='step',linewidth=1,
                        color='blue',label='Other signal (HLC+SLC)',zorder=1)

# HLC & SLC signals
ax1.hist(HLC_log,bins=40,range=[-1.5,1.5],histtype='step',
            linewidth=3.5,color='green',label='HLCs (All particles)',zorder=3)
ax1.hist(SLC_log,bins=40,range=[-1.5,1.5],histtype='step',linewidth=3,
                            color='lime',label='SLCs (All particles)',zorder=4)

# Titles and Labels
ax1.set_title("\nMuon signal and non-Muon signal\nplotted with HLCs and SLCs\n",
                                                        dict(size='xx-large'))
ax1.text(0.04,0.93,"r > "+str(distance)+"m",dict(size='xx-large'),
                                                    transform = ax1.transAxes)
ax1.set_xlabel("log10( charge / VEM )",dict(size='x-large'))
ax1.set_ylabel("Number of pulses",dict(size='x-large'))
ax1.legend()


# Right Side
# --------------

#Charges for muons
ax2.hist(muonHLC_log,bins=40,range=[-1.5,1.5],histtype='step',
                            linewidth=2,color='red',label='Muon HLCs',zorder=3)
ax2.hist(muonSLC_log,bins=40,range=[-1.5,1.5],histtype='step',
                        linewidth=3,color='orange',label='Muon SLCs',zorder=4)
# Charges for other particles
ax2.hist(otherHLC_log,bins=40,range=[-1.5,1.5],histtype='step',
                        linewidth=1,color='blue',label='Other HLCs',zorder=1)
ax2.hist(otherSLC_log,bins=40,range=[-1.5,1.5],histtype='step',
                        linewidth=3,color='aqua',label='Other SLCs',zorder=2)

# Titles and Labels
ax2.set_title("\nMuon signal and non-Muon signal\nbroken down in HLCs and SLCs\n"
                                                        ,dict(size='xx-large'))
ax2.text(0.04,0.93,"r > "+str(distance)+"m",dict(size='xx-large'),
                                                    transform = ax2.transAxes)
ax2.set_xlabel("log10( charge / VEM )",dict(size='x-large'))
ax2.set_ylabel("Number of pulses",dict(size='x-large'))
ax2.legend()


# Save the figure

# where to save the figures
figure_location = "./figures/"

if element == 1:
    figure_name = figure_location + 'analysis_charge_past_'+str(distance)+ \
                                                                'm_Proton.png'
elif element == 2:
    figure_name = figure_location + 'analysis_charge_past_'+str(distance)+ \
                                                                    'm_Iron.png'

print "Saving figure "+figure_name
pylab.savefig(figure_name, bbox_inches='tight')

os.system("eog "+figure_name)

