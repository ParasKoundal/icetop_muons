#!/usr/bin/env python

# This script makes 2 different plots to analyze the various signals vs distance
# The first is a 2d histogram of charge vs distance
# The seconds plots various vertical slices of the first

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab


element  = 2   # set 1 for protons, 2 for iron

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


# where to save the figures
figure_location = "./figures/"


# Collect the data
HLC_latdist = []
HLC_charge  = []
SLC_latdist = []
SLC_charge  = []
for shower in Data:
    for i in range(len(shower.Signals.Tank)):
        if shower.Signals.HLCVEM[i] > 0:
            HLC_latdist.append(shower.Signals.LatDist[i])
            HLC_charge.append(shower.Signals.HLCVEM[i])
        elif shower.Signals.SLCVEM[i] > 0:
            SLC_latdist.append(shower.Signals.LatDist[i])
            SLC_charge.append(shower.Signals.SLCVEM[i])



# THE FIGURES
# ==============================================================================
# ==============================================================================
# ==============================================================================

# FIGURE 1
# 1x3 plot
# 11: 2d histogram of HLC vs lateral distance
# 12: 2d histogram of SLC vs lateral distance
# 13: 2d histogram of total charge vs lateral distance
# ------------------------------------------------------------------------------

plt.rcParams["figure.figsize"] = [16,5]
fig1, (ax1_11, ax1_12, ax1_13) = plt.subplots(1,3)

HLC_charge_log = [np.log10(i) for i in HLC_charge]
HLC_latdist_log = [np.log10(i) for i in HLC_latdist]
SLC_charge_log = [np.log10(i) for i in SLC_charge]
SLC_latdist_log = [np.log10(i) for i in SLC_latdist]
all_charge_log = np.concatenate([HLC_charge_log,SLC_charge_log])
all_latdist_log = np.concatenate([HLC_latdist_log,SLC_latdist_log])

ax1_11.hist2d(HLC_latdist_log,HLC_charge_log,bins=200,range=[[1,3.2],[-1,3]])
ax1_11.set_title("HLC")
ax1_11.set_xlabel("Log10(Lateral Distance / m)")
ax1_11.set_ylabel("Log10(Charge / VEM)")

ax1_12.hist2d(SLC_latdist_log,SLC_charge_log,bins=200,range=[[1,3.2],[-1,3]])
ax1_12.set_title("SLC")
ax1_12.set_xlabel("Log10(Lateral Distance / m)")
ax1_12.set_ylabel("Log10(Charge / VEM)")

ax1_13.hist2d(all_latdist_log,all_charge_log,bins=200,range=[[1,3.2],[-1,3]])
ax1_13.set_title("All Charges")
ax1_13.set_xlabel("Log10(Lateral Distance / m)")
ax1_13.set_ylabel("Log10(Charge / VEM)")

# ------
plt.subplots_adjust(wspace = 0.25)
if element == 1:
    plot_name = figure_location + 'charge_vs_lateral_distance_proton.png'
else:
    plot_name = figure_location + 'charge_vs_lateral_distance_iron.png'
print "Saving",plot_name
pylab.savefig(plot_name, bbox_inches='tight')

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------



# FIGURE 2
# 4x3 plot
# 11: number of SLC's vs log10(charge) at 100m
# 12: number of SLC's vs log10(charge) at 200m
# 13: number of SLC's vs log10(charge) at 300m
# 14: number of SLC's vs log10(charge) at 400m
# 21: number of HLC's vs log10(charge) at 100m
# 22: number of HLC's vs log10(charge) at 200m
# 23: number of HLC's vs log10(charge) at 300m
# 24: number of HLC's vs log10(charge) at 400m
# 31: number of all deposits vs log10(charge) at 100m
# 32: number of all deposits vs log10(charge) at 200m
# 33: number of all deposits vs log10(charge) at 300m
# 34: number of all deposits vs log10(charge) at 400m
# ------------------------------------------------------------------------------

plt.rcParams["figure.figsize"] = [20,14]
fig2, ((ax2_11, ax2_12, ax2_13, ax2_14), (ax2_21, ax2_22, ax2_23, ax2_24),
    (ax2_31, ax2_32, ax2_33, ax2_34)) = plt.subplots(3, 4)

# histograms of log10(charge) around given distances
log_SLC_100 = [] # row 1, column 1
log_SLC_200 = [] # row 2, column 1
log_SLC_300 = [] # row 3, column 1
log_SLC_400 = [] # row 4, column 1
for i in range(len(SLC_latdist)):
    if SLC_latdist[i] > 80 and SLC_latdist[i] < 120:
        log_SLC_100.append(np.log10(SLC_charge[i]))
    if SLC_latdist[i] > 180 and SLC_latdist[i] < 220:
        log_SLC_200.append(np.log10(SLC_charge[i]))
    if SLC_latdist[i] > 280 and SLC_latdist[i] < 320:
        log_SLC_300.append(np.log10(SLC_charge[i]))
    if SLC_latdist[i] > 380 and SLC_latdist[i] < 420:
        log_SLC_400.append(np.log10(SLC_charge[i]))

log_HLC_100 = [] # row 1, column 2
log_HLC_200 = [] # row 2, column 2
log_HLC_300 = [] # row 3, column 2
log_HLC_400 = [] # row 4, column 2
for i in range(len(SLC_latdist)):
    if HLC_latdist[i] > 80 and HLC_latdist[i] < 120:
        log_HLC_100.append(np.log10(HLC_charge[i]))
    if HLC_latdist[i] > 180 and HLC_latdist[i] < 220:
        log_HLC_200.append(np.log10(HLC_charge[i]))
    if HLC_latdist[i] > 280 and HLC_latdist[i] < 320:
        log_HLC_300.append(np.log10(HLC_charge[i]))
    if HLC_latdist[i] > 380 and HLC_latdist[i] < 420:
        log_HLC_400.append(np.log10(HLC_charge[i]))

log_all_100 = np.concatenate([log_SLC_100,log_HLC_100]) # row 1, column 3
log_all_200 = np.concatenate([log_SLC_200,log_HLC_200]) # row 2, column 3
log_all_300 = np.concatenate([log_SLC_300,log_HLC_300]) # row 3, column 3
log_all_400 = np.concatenate([log_SLC_400,log_HLC_400]) # row 4, column 3


# 11
ax2_11.hist(log_SLC_100,range=[-1.5,1.5],bins=40,histtype='step')
ax2_11.set_title("r = 100m +/- 20m")
ax2_11.set_xlabel("log10( charge / VEM )")
ax2_11.set_ylabel("N_SLC")

# 12
ax2_12.hist(log_SLC_200,range=[-1.5,1.5],bins=40,histtype='step')
ax2_12.set_title("r = 200m +/- 20m")
ax2_12.set_xlabel("log10( charge / VEM )")
ax2_12.set_ylabel("N_SLC")

# 13
ax2_13.hist(log_SLC_300,range=[-1.5,1.5],bins=40,histtype='step')
ax2_13.set_title("r = 300m +/- 20m")
ax2_13.set_xlabel("log10( charge / VEM )")
ax2_13.set_ylabel("N_SLC")

# 14
ax2_14.hist(log_SLC_400,range=[-1.5,1.5],bins=40,histtype='step')
ax2_14.set_title("r = 400m +/- 20m")
ax2_14.set_xlabel("log10( charge / VEM )")
ax2_14.set_ylabel("N_SLC")

# 21
ax2_21.hist(log_HLC_100,range=[-1.5,1.5],bins=40,histtype='step')
ax2_21.set_title("r = 100m +/- 20m")
ax2_21.set_xlabel("log10( charge / VEM )")
ax2_21.set_ylabel("N_HLC")

# 22
ax2_22.hist(log_HLC_200,range=[-1.5,1.5],bins=40,histtype='step')
ax2_22.set_title("r = 200m +/- 20m")
ax2_22.set_xlabel("log10( charge / VEM )")
ax2_22.set_ylabel("N_HLC")

# 23
ax2_23.hist(log_HLC_300,range=[-1.5,1.5],bins=40,histtype='step')
ax2_23.set_title("r = 300m +/- 20m")
ax2_23.set_xlabel("log10( charge / VEM )")
ax2_23.set_ylabel("N_HLC")

# 24
ax2_24.hist(log_HLC_400,range=[-1.5,1.5],bins=40,histtype='step')
ax2_24.set_title("r = 400m +/- 20m")
ax2_24.set_xlabel("log10( charge / VEM )")
ax2_24.set_ylabel("N_HLC")

# 31
ax2_31.hist(log_all_100,range=[-1.5,1.5],bins=40,histtype='step')
ax2_31.set_title("r = 100m +/- 20m")
ax2_31.set_xlabel("log10( charge / VEM )")
ax2_31.set_ylabel("N_deposits")

# 32
ax2_32.hist(log_all_200,range=[-1.5,1.5],bins=40,histtype='step')
ax2_32.set_title("r = 200m +/- 20m")
ax2_32.set_xlabel("log10( charge / VEM )")
ax2_32.set_ylabel("N_deposits")

# 33
ax2_33.hist(log_all_300,range=[-1.5,1.5],bins=40,histtype='step')
ax2_33.set_title("r = 300m +/- 20m")
ax2_33.set_xlabel("log10( charge / VEM )")
ax2_33.set_ylabel("N_deposits")

# 34
ax2_34.hist(log_all_400,range=[-1.5,1.5],bins=40,histtype='step')
ax2_34.set_title("r = 400m +/- 20m")
ax2_34.set_xlabel("log10( charge / VEM )")
ax2_34.set_ylabel("N_deposits")

# ------
plt.subplots_adjust(wspace = 0.25)
plt.subplots_adjust(hspace = 0.30)
if element == 1:
    plot_name = figure_location + 'signals_at_various_distances_proton.png'
else:
    plot_name = figure_location + 'signals_at_various_distances_iron.png'
print "Saving",plot_name
pylab.savefig(plot_name, bbox_inches='tight')

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


