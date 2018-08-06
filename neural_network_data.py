#!/usr/bin/env python

import numpy as np

NNdata300 = []
NNdata400 = []

def process_shower(shower):
    E_proton  = shower.Reconstruction.E_Proton
    E_iron    = shower.Reconstruction.E_Iron
    E_avg     = np.sqrt(E_proton*E_iron) # geometric mean
    Zen       = shower.Reconstruction.zen
    coredist  = shower.Reconstruction.CoreDist()
    Type      = shower.Primary.Type
    
    # for log(E_avg) < 16.5
    Q300      = 0
    MuonPE300 = 0
    nMuon300  = 0
    
    # for log(E_avg) > 16.5
    Q400      = 0
    MuonPE400 = 0
    nMuon400  = 0
    
    if np.log10(E_avg) < 16.5:
        for i in range(len(shower.Signals.Tank)):
            if shower.Signals.LatDist[i] > 300:
                nMuon300 += shower.Signals.nMuons[i]
                MuonPE300 += shower.Signals.MuonPE[i]
                if shower.Signals.TotalVEM[i] >= 0.6 and shower.Signals.TotalVEM[i] <= 2.0:
                    Q300 += shower.Signals.TotalVEM[i]
        
        NNdata300.append([E_proton,E_iron,Zen,coredist,Q300,MuonPE300,nMuon300,Type])
    
    else:
        for i in range(len(shower.Signals.Tank)):
            if shower.Signals.LatDist[i] > 400:
                nMuon400 += shower.Signals.nMuons[i]
                MuonPE400 += shower.Signals.MuonPE[i]
                if shower.Signals.TotalVEM[i] >= 0.6 and shower.Signals.TotalVEM[i] <= 2.0:
                    Q400 += shower.Signals.TotalVEM[i]
                    
        NNdata400.append([E_proton,E_iron,Zen,coredist,Q400,MuonPE400,nMuon400,Type])


protondata = np.load('./data/proton_showers.npy')
for shower in protondata:
    process_shower(shower)
del protondata

irondata = np.load('./data/iron_showers.npy')
for shower in irondata:
    process_shower(shower)
del irondata

print 'saving ./data/NN_data_300m.npy'
np.save('./data/NN_data_300m.npy',NNdata300)
print 'saving ./data/NN_data_400m.npy'
np.save('./data/NN_data_400m.npy',NNdata400)
