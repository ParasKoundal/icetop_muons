#!/usr/bin/env python

# This script makes a plot of signals vs VEMs from muons
# It bins showers by zenith angle (found in settings) and plots each range as a
# different color. The points on the plot are also binned and averaged, and a
# and a line is fit to the averages

import numpy as np
from ShowerClass import *
import matplotlib.pyplot as plt
from matplotlib import pylab
import seaborn as sns

import os

# SETTINGS ---------------------------------------------------------------------
element      = 1 # set 1 for protons, 2 for iron
distance     = 400 # set distance where we make cut on signal, unit: meters
q_lowerlimit = 0.6 # lower cut for tank charge, unit: VEM
q_upperlimit = 2.0 # upper cut for tank charge, unit: VEM
logE_min     = 15.5
logE_max     = 16
# ------------------------------------------------------------------------------


# where to find data
data_location = './data/'

#load the data
if element == 1:
    Data = np.load(data_location+"proton_showers.npy")
    primary = "Proton"
elif element == 2:
    Data = np.load(data_location+"iron_showers.npy")
    primary = "Iron"
else:
    print "Please set 'element' to either 1 (proton) or 2 (iron)"
    exit()

zen1 = [[],[],[],[]] # cos(zenith) in (0.9,1.0)
zen2 = [[],[],[],[]] # cos(zenith) in (0.8,0.9)

# Collect data from all the showers
for shower in Data:
    logE = np.log10(shower.Primary.Energy)
    if logE > logE_min and logE < logE_max:
            
            muonPE_  = 0
            Tot_     = 0
            HLC_     = 0
            SLC_     = 0
            
            for i in range(len(shower.Signals.Tank)): # loop through every tank
                if shower.Signals.LatDist[i] >= distance and \
                shower.Signals.TotalPE[i] > 0:
                    
                    # convert PEs to VEM
                    totalVEM = shower.Signals.TotalVEM[i]
                    totalPE  = shower.Signals.TotalPE[i]
                    scale = totalVEM/totalPE
                    scaledPE = scale*shower.Signals.MuonPE[i]
                    
                    # sum signals that are within cuts
                    if scaledPE >= q_lowerlimit and scaledPE <= q_upperlimit:
                        muonPE_ += scaledPE
                    if totalVEM >= q_lowerlimit and totalVEM <= q_upperlimit:
                        Tot_ += totalVEM
                    if shower.Signals.HLCVEM[i] >= q_lowerlimit and \
                    shower.Signals.HLCVEM[i] <= q_upperlimit:
                        HLC_ += shower.Signals.HLCVEM[i]
                    if shower.Signals.SLCVEM[i] >= q_lowerlimit and \
                    shower.Signals.SLCVEM[i] <= q_upperlimit:
                        SLC_ += shower.Signals.SLCVEM[i]

            # add the summed signals to the array for the corr. angle range
            zen = shower.Primary.zen
            if np.cos(zen) >= 0.9 and np.cos(zen) <= 1.0:
                zen1[0].append(muonPE_)
                zen1[1].append(Tot_)
                zen1[2].append(HLC_)
                zen1[3].append(SLC_)
            if np.cos(zen) >= 0.8 and np.cos(zen) < 0.9:
                zen2[0].append(muonPE_)
                zen2[1].append(Tot_)
                zen2[2].append(HLC_)
                zen2[3].append(SLC_)


#plt.scatter(zen1[0],zen1[1],marker='.')
#plt.show()

# ------------------------------------------------------------------------------
# Figure -----------------------------------------------------------------------
# ------------------------------------------------------------------------------

plt.rcParams["figure.figsize"] = [15,5]
fig, (ax1,ax2,ax3) = plt.subplots(1,3)

# plot the angle ranges, all 3 signals
colors = sns.color_palette()
counter = 0

#plt.rc('text', usetex=True)

label1 = r'$0.9 < cos(\theta) < 1.0$'
label2 = r'$0.8 < cos(\theta) < 0.9$'

sns.regplot(x=zen1[0],y=zen1[2],x_bins=10,ci=95,label=label1,ax=ax1)
sns.regplot(x=zen2[0],y=zen2[2],x_bins=10,ci=95,label=label2,ax=ax1)

sns.regplot(x=zen1[0],y=zen1[3],x_bins=10,ci=95,label=label1,ax=ax2)
sns.regplot(x=zen2[0],y=zen2[3],x_bins=10,ci=95,label=label2,ax=ax2)

sns.regplot(x=zen1[0],y=zen1[1],x_bins=10,ci=95,label=label1,ax=ax3)
sns.regplot(x=zen2[0],y=zen2[1],x_bins=10,ci=95,label=label2,ax=ax3)


# main title
cuts = "Cuts:  tank >"+str(distance)+"m from shower core,   "+str(q_lowerlimit)+ \
                                    " VEM < charge < "+str(q_upperlimit)+" VEM"
                                    
fig.suptitle("Primary: "+primary+", log(E) $\in$ ("+str(logE_min)+", "+ \
                                        str(logE_max)+")\n"+cuts,fontsize=15)

# axis titles
ax1.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax2.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax3.set_xlabel("Charge of Photoelectrons from Muons (VEM)")

ax1.set_ylabel("HLC Charge (VEM)")
ax2.set_ylabel("SLC Charge (VEM)")
ax3.set_ylabel("Total Charge (VEM)")

# legend
ax1.legend()
ax2.legend()
ax3.legend()


# save the figure
figure_location = "./figures/"
figure_name = figure_location + 'muon_charge_zenith_comparison_past_'+str(distance)+'m_'+primary+'.png'
                                   
                                                            
print "Saving figure "+figure_name
pylab.savefig(figure_name, bbox_inches='tight')


# open the figure just saved
os.system("eog "+figure_name)


