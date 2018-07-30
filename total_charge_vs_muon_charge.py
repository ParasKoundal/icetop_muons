#!/usr/bin/env python

# This script plots total VEMs vs muon VEMs, with the cuts described in 
# 'settings'. A line is fit by binning the points and averaging, but the
# original points are also plotted for comparison

import numpy as np
from ShowerClass import *
import matplotlib.pyplot as plt
from matplotlib import pylab
import seaborn as sns

import os

# SETTINGS ---------------------------------------------------------------------
element      = 2 # set 1 for protons, 2 for iron
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


PE300  = []
SLC300 = []
HLC300 = []
VEM300 = []


for shower in Data:
    if shower.Primary.Energy > E_lowerlimit and \
    shower.Primary.Energy < E_upperlimit:
        PE300_ = 0
        SLC300_ = 0
        HLC300_ = 0
        VEM300_ = 0
        for i in range(len(shower.Signals.Tank)):
            if shower.Signals.LatDist[i] >= distance and \
            shower.Signals.TotalPE[i] > 0:
                totalVEM = shower.Signals.TotalVEM[i]
                totalPE  = shower.Signals.TotalPE[i]
                scale = totalVEM/totalPE
                scaledPE = scale*shower.Signals.MuonPE[i]
                if scaledPE > q_lowerlimit and scaledPE < q_upperlimit:
                    PE300_ += scaledPE
                if (shower.Signals.HLCVEM[i] > q_lowerlimit and 
                shower.Signals.HLCVEM[i] < q_upperlimit):
                    HLC300_ += shower.Signals.HLCVEM[i]
                if (shower.Signals.SLCVEM[i] > q_lowerlimit and 
                shower.Signals.SLCVEM[i] < q_upperlimit):
                    SLC300_ += shower.Signals.SLCVEM[i]
                if totalVEM > q_lowerlimit and totalVEM < q_upperlimit:
                    VEM300_ += shower.Signals.TotalVEM[i]

        PE300.append(PE300_)
        SLC300.append(SLC300_)
        HLC300.append(HLC300_)
        VEM300.append(VEM300_)



# ------------------------------------------------------------------------------
# Figure -----------------------------------------------------------------------
# ------------------------------------------------------------------------------


plt.rcParams["figure.figsize"] = [15,5]
fig,(ax1,ax2,ax3) = plt.subplots(1,3)

# main title
cuts = "Cuts:  tank >"+str(distance)+"m from shower core,  "+ \
                str(q_lowerlimit)+" VEM < charge < "+str(q_upperlimit)+" VEM"
primaryE = "$log_{10}($"+str(np.log10(E_lowerlimit))+ \
            "$) < E_{primary} < log_{10}($"+str(np.log10(E_upperlimit))+"$)$"
fig.suptitle(cuts+"\n"+primaryE,fontsize=15)

sns.regplot(x=PE300,y=SLC300,fit_reg=None,color='lightgray',marker='.',ax=ax1)
sns.regplot(x=PE300,y=SLC300,x_bins=10,x_ci='ci',fit_reg=True,color='blue',ax=ax1)
ax1.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax1.set_ylabel("SLC Charge (VEM)")

sns.regplot(x=PE300,y=HLC300,fit_reg=None,color='lightgray',marker='.',ax=ax2)
sns.regplot(x=PE300,y=HLC300,x_bins=10,x_ci='ci',fit_reg=True,color='blue',ax=ax2)
ax2.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax2.set_ylabel("HLC Charge (VEM)")

sns.regplot(x=PE300,y=VEM300,fit_reg=None,color='lightgray',marker='.',ax=ax3)
sns.regplot(x=PE300,y=VEM300,x_bins=10,x_ci='ci',fit_reg=True,color='blue',ax=ax3)
ax3.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax3.set_ylabel("Total Charge (VEM)")


# where to save the figures
figure_location = "./figures/"

if element == 1:
    figure_name = figure_location + 'total_charge_vs_muon_charge_past_'+ \
                                                    str(distance)+'m_Proton.png'
elif element == 2:
    figure_name = figure_location + 'total_charge_vs_muon_charge_past_'+ \
                                                    str(distance)+'m_Iron.png'

print "Saving figure "+figure_name
pylab.savefig(figure_name, bbox_inches='tight')

# open the figure just saved
os.system("eog "+figure_name)
