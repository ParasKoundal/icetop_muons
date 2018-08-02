#!/usr/bin/env python

# This script makes a plot of total VEMs vs VEMs from muons
# It bins showers by energy ranges (found in settings) and plots each range as a
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
distance     = 300 # set distance where we make cut on signal, unit: meters
q_lowerlimit = 0.6 # lower cut for tank charge, unit: VEM
q_upperlimit = 2.0 # upper cut for tank charge, unit: VEM
# Array of log(E) bin edges
E = [15.0,15.5,16.0,16.5,17.0]
# ------------------------------------------------------------------------------

# create a dictionary that will hold the signals for the different energy ranges
# the energy ranges are numbered by increasing energy, starting with 0
E_dict = dict()
for i in range(len(E)-1):
    # first array for muon PEs, second for total VEMs, then HLC, then SLC
    E_dict[i] = [[],[],[],[]]

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


# Collect data from all the showers
for shower in Data:
     # step through the energy ranges to find which one the shower belongs to
    for j in range(len(E)-1):
        if np.log10(shower.Primary.Energy) >= E[j] and \
        np.log10(shower.Primary.Energy) < E[j+1]:
            
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

            # add the summed signals to the array for the corr. energy range
            E_dict[j][0].append(muonPE_)
            E_dict[j][1].append(Tot_)
            E_dict[j][2].append(HLC_)
            E_dict[j][3].append(SLC_)



# ------------------------------------------------------------------------------
# Figure -----------------------------------------------------------------------
# ------------------------------------------------------------------------------

plt.rcParams["figure.figsize"] = [15,5]
fig, (ax1,ax2,ax3) = plt.subplots(1,3)

# plot the energy ranges
#colors = ['blue','orange','green','red']
colors = sns.color_palette()
counter = 0
for i in E_dict:
    label = str(E[i])+" < log(E) < "+str(E[i+1])
    sns.regplot(x=E_dict[i][0],y=E_dict[i][2],x_bins=10,ci=95,label=label,
                                                ax=ax1,color=colors[counter])
    sns.regplot(x=E_dict[i][0],y=E_dict[i][3],x_bins=10,ci=95,label=label,
                                                ax=ax2,color=colors[counter])
    sns.regplot(x=E_dict[i][0],y=E_dict[i][1],x_bins=10,ci=95,label=label,
                                                ax=ax3,color=colors[counter])
    counter += 1
    

# main title
cuts = "Cuts:  tank >"+str(distance)+"m from shower core,   "+str(q_lowerlimit)+ \
                                    " VEM < charge < "+str(q_upperlimit)+" VEM"
fig.suptitle("Primary: "+primary+"     "+cuts,fontsize=15)

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
figure_name = figure_location + 'muon_charge_E_binned_past_'+str(distance)+'m_'\
                                                            +primary+'.png'

print "Saving figure "+figure_name
pylab.savefig(figure_name, bbox_inches='tight')


# open the figure just saved
os.system("eog "+figure_name)

