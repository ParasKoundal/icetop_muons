#!/usr/bin/env python

import numpy as np
from ShowerClass import *
import matplotlib.pyplot as plt
from matplotlib import pylab


# SETTINGS ---------------------------------------------------------------------
element      = 1 # set 1 for protons, 2 for iron
distance     = 300 # set distance where we make cut on signal, unit: meters
q_lowerlimit = 0.6 # lower cut for tank charge, unit: VEM
q_upperlimit = 2.0 # upper cut for tank charge, unit: VEM
E_lowerlimit = 10**(15.5) # lower limit on primary energy, unit eV
E_upperlimit = 10**(16.0) # upper limit on primary energy, unit eV
# ------------------------------------------------------------------------------

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

S500  = []
signal = []


for shower in Data:
    if shower.Primary.Energy > E_lowerlimit and \
    shower.Primary.Energy < E_upperlimit:
        S500_ = shower.S500
        signal_ = 0

        for i in range(len(shower.Signals.Tank)):
            if shower.Signals.LatDist[i] >= distance and \
            shower.Signals.TotalPE[i] > 0:
                scale = shower.Signals.TotalVEM[i]/shower.Signals.TotalPE[i]
                scaledPE = scale*shower.Signals.MuonPE[i]
                if scaledPE > q_lowerlimit and scaledPE < q_upperlimit:
                    signal_ += scaledPE

        S500.append(S500_)
        signal.append(signal_)




plt.rcParams["figure.figsize"] = [10,8]
fig,ax = plt.subplots(1,1)

ax.scatter(signal,S500)
ax.set_xlabel("S500")
ax.set_ylabel("Charge of Photoelectrons from Muons")

# main title
cuts = "Cuts:  tank >"+str(distance)+"m from shower core,  "+ \
                str(q_lowerlimit)+" VEM < charge < "+str(q_upperlimit)+" VEM"
primaryE = "$log_{10}($"+str(np.log10(E_lowerlimit))+ \
            "$) < E_{primary} < log_{10}($"+str(np.log10(E_upperlimit))+"$)$"
fig.suptitle(cuts+"\n"+primaryE,fontsize=15)


# where to save the figures
figure_location = "./figures/"

if element == 1:
    fig_name = figure_location + 'S500_vs_muon_charge_proton.png'
else:
    fig_name = figure_location + 'S500_vs_muon_charge_iron.png'
print "Saving",fig_name
pylab.savefig(fig_name, bbox_inches='tight')
    
