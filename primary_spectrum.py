#!/usr/bin/env python

# This script creates a histogram that shows the energy spectra of the iron and
# proton primaries

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab


data_location = './data/'

#load the data
protondata = np.load(data_location+"proton_showers.npy")
irondata   = np.load(data_location+"iron_showers.npy")

proton_energy = []
iron_energy   = []

for shower in protondata:
    proton_energy.append(shower.Primary.Energy)
for shower in irondata:
    iron_energy.append(shower.Primary.Energy)
    

log_p_en  = [np.log10(i) for i in proton_energy]
log_fe_en = [np.log10(i) for i in iron_energy]
data = [log_p_en,log_fe_en]


# The histogram

fig,ax = plt.subplots(1,1)
ax.hist(data,bins=21,histtype='step',stacked=False,alpha=1,
                                                    label=["Protons","Fe56"])
ax.legend(loc=2)
ax.set_xlabel("log10(primary energy / eV)")
ax.set_xlim(15,17.1)
plt.xticks([15.0,15.5,16.0,16.5,17.0])
ax.text(0.625, 0.95, "{0} proton showers".format(len(proton_energy)),
                                    dict(size='large'),transform = ax.transAxes)
ax.text(0.625, 0.90, "{0} iron showers".format(len(iron_energy)),
                                    dict(size='large'),transform = ax.transAxes)


# where to save the figures
figure_location = "./figures/"

pylab.savefig(figure_location + 'primary_energy_spectrum.png', 
                                                            bbox_inches='tight')
print "Creating",figure_location + 'primary_energy_spectrum.png'
