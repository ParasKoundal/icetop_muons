#!/usr/bin/env python

# This script makes a short version of the shower arrays. These shorter lists
# are smaller and thus faster to prototype scripts with.
# constructed by taking only showers with log(E) between 16.5 and 17.0

import numpy as np


#load the data
data_location = './data/'
protondata = np.load(data_location+"proton_showers.npy")
irondata   = np.load(data_location+"iron_showers.npy")

protonshort = []
ironshort   = []

for shower in protondata:
    logE = np.log10(shower.Primary.Energy)
    if logE >= 16.5 and logE <= 17.0:
        protonshort.append(shower)

for shower in irondata:
    logE = np.log10(shower.Primary.Energy)
    if logE >= 16.5 and logE <= 17.0:
        ironshort.append(shower)


# save the data

save_location = './data/'

np.save(save_location+'proton_showers_short.npy',protonshort)
np.save(save_location+'iron_showers_short.npy',ironshort)


print len(protonshort),len(ironshort)
