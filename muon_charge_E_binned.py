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
element      = 2 # set 1 for protons, 2 for iron
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
    E_dict[i] = [[],[]] # first array for muon PEs, second for total VEMs


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


# Collect data from all the showers
for shower in Data:
     # step through the energy ranges to find which one the shower belongs to
    for j in range(len(E)-1):
        if np.log10(shower.Primary.Energy) >= E[j] and \
        np.log10(shower.Primary.Energy) < E[j+1]:
            PE300_  = 0 # sum of muon PEs >300m in this shower
            VEM300_ = 0 # sum of VEMs >300m in this shower
            for i in range(len(shower.Signals.Tank)): # loop through every tank
                if shower.Signals.LatDist[i] >= distance and \
                shower.Signals.TotalPE[i] > 0:
                    
                    # convert PEs to VEM
                    totalVEM = shower.Signals.TotalVEM[i]
                    totalPE  = shower.Signals.TotalPE[i]
                    scale = totalVEM/totalPE
                    scaledPE = scale*shower.Signals.MuonPE[i]
                    
                    # sum signals that are within cuts
                    if scaledPE > q_lowerlimit and scaledPE < q_upperlimit:
                        PE300_ += scaledPE
                    if totalVEM > q_lowerlimit and totalVEM < q_upperlimit:
                        VEM300_ += totalVEM

            # add the summed signals to the array for the corr. energy range
            E_dict[j][0].append(PE300_)
            E_dict[j][1].append(VEM300_)



# ------------------------------------------------------------------------------
# Figure -----------------------------------------------------------------------
# ------------------------------------------------------------------------------

plt.rcParams["figure.figsize"] = [8,7]
fig, ax = plt.subplots(1,1)

# plot the energy ranges
for i in E_dict:
    label = str(E[i])+" < log(E) < "+str(E[i+1])
    sns.regplot(x=E_dict[i][0],y=E_dict[i][1],x_bins=10,ci=95,label=label,ax=ax)
    
    
# main title
cuts = "Cuts:  tank >"+str(distance)+"m from shower core\n"+str(q_lowerlimit)+ \
                                    " VEM < charge < "+str(q_upperlimit)+" VEM"
fig.suptitle(cuts,fontsize=12)
# axis titles
ax.set_xlabel("Charge of Photoelectrons from Muons (VEM)")
ax.set_ylabel("Total Charge (VEM)")
# legend
leg = ax.legend()
# Primary type
if element == 1:
    ax.text(0.75,0.01,"Primary: Proton",dict(size='large'),transform = ax.transAxes)
elif element == 2:
    ax.text(0.80,0.01,"Primary: Iron",dict(size='large'),transform = ax.transAxes)



# save the figure
figure_location = "./figures/"
if element == 1:
    figure_name = figure_location + 'muon_charge_E_binned_past_'+str(distance)+\
                                                                'm_Proton.png'
elif element == 2:
    figure_name = figure_location + 'muon_charge_E_binned_past_'+str(distance)+\
                                                                    'm_Iron.png'

print "Saving figure "+figure_name
pylab.savefig(figure_name, bbox_inches='tight')


# open the figure just saved
os.system("eog "+figure_name)

