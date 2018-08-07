#!/usr/bin/env python

import numpy as np

NNdata300 = []
NNdata400 = []

def process_shower(shower):
    E_proton  = shower.Reconstruction.E_Proton
    E_iron    = shower.Reconstruction.E_Iron
    Zen       = shower.Reconstruction.zen
    coredist  = shower.Reconstruction.CoreDist()
    Type      = shower.Primary.Type
    
    # for log(E_avg) > 16.5
    Q400      = 0.
    MuonPE400 = 0.
    nMuon400  = 0.

    
    for i in range(len(shower.Signals.Tank)):
        if shower.Signals.LatDist[i] > 400 and shower.Signals.TotalPE[i] != 0:
            totalVEM = shower.Signals.TotalVEM[i]
            totalPE  = shower.Signals.TotalPE[i]
            scale = totalVEM/totalPE
            scaledPE = scale*shower.Signals.MuonPE[i]
            nMuon400 += shower.Signals.nMuons[i]
            MuonPE400 += scaledPE
            if totalVEM >= 0.6 and totalVEM <= 2.0:
                Q400 += totalVEM
                
    NNdata400.append([E_proton,E_iron,Zen,coredist,Q400,MuonPE400,nMuon400,Type])


protondata = np.load('./data/proton_showers.npy')
for shower in protondata:
    process_shower(shower)
del protondata

irondata = np.load('./data/iron_showers.npy')
for shower in irondata:
    process_shower(shower)
del irondata

print 'saving ./data/NN_data_400m.npy'
np.save('./data/NN_data_400m.npy',NNdata400)
