#!/usr/bin/env python

import numpy as np

NNdata400  = []

# function that collects the data wanted for use in the neural network
def process_shower(shower):
    Run       = shower.Run
    E_proton  = shower.Reconstruction.E_Proton
    E_iron    = shower.Reconstruction.E_Iron
    Zen       = shower.Reconstruction.zen
    Type      = shower.Primary.Type
    

    Q400    = 0.
    MuonVEM = 0.
    nMuon   = 0.

    
    for i in range(len(shower.Signals.Tank)):
        if shower.Signals.LatDist[i] > 400 and shower.Signals.TotalPE[i] != 0:
            totalVEM = shower.Signals.TotalVEM[i]
            totalPE  = shower.Signals.TotalPE[i]
            scale    = totalVEM/totalPE
            scaledPE = scale*shower.Signals.MuonPE[i]
            nMuon   += shower.Signals.nMuons[i]
            MuonVEM += scaledPE
            if totalVEM >= 0.6 and totalVEM <= 2.0:
                Q400 += totalVEM

    NNdata400_.append([Run,E_proton,E_iron,Zen,Q400,MuonVEM,nMuon,Type])

# function that avarages the NN data for each run
def avg_runs(NNdata400_,Type):
    
    run_list = set()
    for shower in NNdata400_:
        run_list.add(shower[0])
    
    for run in run_list:
        nShowers     = 0.
        E_proton_tot = 0.
        E_iron_tot   = 0.
        Zen_tot      = 0.
        Q400_tot     = 0.
        MuonVEM_tot  = 0.
        nMuon_tot    = 0.
        for shower in NNdata400_:
            if shower[0] == run:
                nShowers     += 1.
                E_proton_tot += shower[1]
                E_iron_tot   += shower[2]
                Zen_tot      += shower[3]
                Q400_tot     += shower[4]
                MuonVEM_tot  += shower[5]
                nMuon_tot    += shower[6]
                
        E_proton_avg = E_proton_tot/nShowers
        E_iron_avg   = E_iron_tot/nShowers
        Zen_avg      = Zen_tot/nShowers
        Q400_avg     = Q400_tot/nShowers
        MuonVEM_avg  = MuonVEM_tot/nShowers
        nMuon_avg    = nMuon_tot/nShowers
        NNdata400.append([E_proton_avg,E_iron_avg,Zen_avg,Q400_avg,MuonVEM_avg,nMuon_avg,Type])







NNdata400_ = []
protondata = np.load('./data/proton_showers.npy')
for shower in protondata:
    process_shower(shower)
del protondata
avg_runs(NNdata400_,"proton")

NNdata400_ = []
irondata = np.load('./data/iron_showers.npy')
for shower in irondata:
    process_shower(shower)
del irondata
avg_runs(NNdata400_,"iron")


print 'saving ./data/NN_data_400m.npy'
np.save('./data/NN_data_400m.npy',NNdata400)

