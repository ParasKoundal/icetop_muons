#!/usr/bin/env python

# This script takes I3 simulation files and and stores relevant data (plus some 
# meta data) in the Shower data structure, defined in ShowerClass.py. The data 
# is saved data folder.
# Note that it stores all the data during run and then saves it all at the end. 
# Thus you can use the current data structures in the data folder while this 
# program is running. At the end of execution, this program will then update 
# those files with the new data. This also means if you accidently run this
# script, you can just cancel it before completion and nothing will happen to
# the current data

# ------------------------------------------------------------------------------
# make sure IceTray environment is active
import os
if not 'I3_BUILD' in os.environ:
    raise Exception('To run this script start an IceTray environment \n' + \
                     'This can be achieved via ./env-shell.sh')
# ------------------------------------------------------------------------------


import numpy as np
import glob

from ShowerClass import Shower, LatDist, which_tank

from icecube.dataio import I3File
from icecube import icetray, dataclasses, recclasses, simclasses

#data files location
data_location = './data/i3files/'

# get geometry info
geom_file  = I3File("./data/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz")
geom_frame = geom_file.pop_frame()
geometry   = geom_frame['I3Geometry']
geom_file.close()


# arrays to hold all the showers
ProtonData = []
IronData   = []


# --------------------------------------------------------------------------
# Now get the data from the files -------------------------------------------

# list of appropriate files in folder
files = glob.glob(data_location + 'Level2*')

# loop through files
nfiles = len(files)
for file_number in range(nfiles):

    file_name = files[file_number]
    i3f = I3File(file_name)

    print "Starting",file_name,"(file",file_number+1,"of "+str(nfiles)+")"

    while i3f.more():

        frame = i3f.pop_physics()
        
        # new instance of the Shower data structure (see "ShowerClass.py")
        shower = Shower()

        header = frame["I3EventHeader"]
        shower.Run   = header.run_id
        shower.Event = header.event_id

        # ----------------------------------------------------------------------
        # Primary particle truth data ------------------------------------------
        # ----------------------------------------------------------------------
        MCPrim = frame["MCPrimary"]

        shower.Primary.Type   = MCPrim.type_string
        shower.Primary.Energy = MCPrim.energy*10**9

        xc  = shower.Primary.x = MCPrim.pos.x
        yc  = shower.Primary.y = MCPrim.pos.y
        zc  = shower.Primary.z = MCPrim.pos.z
        zen = shower.Primary.zen = MCPrim.dir.zenith # in radians
        azi = MCPrim.dir.azimuth # in radians

        # unit vector pointing back along primary trajectory 
        # (will be used for axis dist.)
        nx = -np.sin(zen)*np.cos(azi)
        ny = -np.sin(zen)*np.sin(azi)
        nz = -np.cos(zen)
        N  = [nx,ny,nz]

        tcr = MCPrim.time # I will accept signals within 1000 ns of this


        # ----------------------------------------------------------------------
        # Signals --------------------------------------------------------------
        # ----------------------------------------------------------------------

        # First I make a dictionary, with an entry for every tank
        # Each entry contains the station number and the tank number
        # note: OMs 61,62 are in tank 1, OMs 63,64 are in tank 2

        Signals_dict = dict()

        # Fill the dictionary with tank names, and their lateral distances
        # I also leave 6 empty entries in an array to hold the signal data below
        for i in range(1,10):
            for j in [1,2]:
                tank = "Station0"+str(i)+"_Tank"+str(j)
                Signals_dict[tank] = np.zeros(7)
                key = icetray.OMKey(i,j+61)
                Signals_dict[tank][0] = LatDist(xc,yc,zc,N,key,geometry)

        for i in range(10,82):
            for j in [1,2]:
                tank = "Station"+str(i)+"_Tank"+str(j)
                Signals_dict[tank] = np.zeros(7)
                key = icetray.OMKey(i,j+61)
                Signals_dict[tank][0] = LatDist(xc,yc,zc,N,key,geometry)

        # --------------------
        # Muon Pulses --------
        # --------------------

        muonpulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                                'IceTopComponentPulses_Muon')
        
        nMuonPulses = 0
        MuonPulses = []

        for key, pulses in muonpulse:
            for p in pulses:
                if p.charge > 0 and np.abs(tcr - p.time) <= 1000:
                    nMuonPulses += 1
                    tank = which_tank(key) # get the name of the tank w/ OMKey
                    Signals_dict[tank][1] += p.charge 

        shower.nMuonPulses = nMuonPulses

        # --------------------
        # Other Pulses -------
        # --------------------

        electronpulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                            'IceTopComponentPulses_Electron')
        electronmesonpulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                            'IceTopComponentPulses_ElectronFromChargedMesons')
        gammapulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                                'IceTopComponentPulses_Gamma')
        gammamesonpulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                'IceTopComponentPulses_GammaFromChargedMesons')
        hadronpulse = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                                'IceTopComponentPulses_Hadron')

        Other_pulses= [electronpulse,electronmesonpulse,gammapulse,
                                                    gammamesonpulse,hadronpulse]

        for O in Other_pulses:
            for key, pulses in O:
                for p in pulses:
                    if p.charge > 0 and np.abs(tcr - p.time) <= 1000:
                        tank = which_tank(key)  # get the name of the tank
                        Signals_dict[tank][2] += p.charge 

        # Add the total number of photoelectrons
        for tank in Signals_dict:
            Signals_dict[tank][3]= Signals_dict[tank][1] + Signals_dict[tank][2]

        # --------------------
        # HLC & SLC Signals --
        # --------------------

        # HLC data --
        events_HLC  = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                                    'OfflineIceTopHLCVEMPulses')
        for key, pulses in events_HLC:
            for p in pulses:
                if p.charge > 0 and np.abs(tcr - p.time) <= 1000:
                    tank = which_tank(key)
                    Signals_dict[tank][4] += p.charge  

        events_SLC  = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,
                                                    'OfflineIceTopSLCVEMPulses')

        # SLC data --
        for key, pulses in events_SLC:
            for p in pulses:
                if p.charge > 0 and np.abs(tcr - p.time) <= 1000:
                    tank = which_tank(key)
                    Signals_dict[tank][5] += p.charge 

        # add the total signal in VEM
        for tank in Signals_dict:
            Signals_dict[tank][6]= Signals_dict[tank][4] + Signals_dict[tank][5]

        # ------------------------
        # Add Signals to Shower --
        # ------------------------
        for tank in sorted(Signals_dict):
            shower.Signals.Tank.append(tank)
            shower.Signals.LatDist.append(Signals_dict[tank][0])
            shower.Signals.MuonPE.append(Signals_dict[tank][1])
            shower.Signals.OtherPE.append(Signals_dict[tank][2])
            shower.Signals.TotalPE.append(Signals_dict[tank][3])
            shower.Signals.HLCVEM.append(Signals_dict[tank][4])
            shower.Signals.SLCVEM.append(Signals_dict[tank][5])
            shower.Signals.TotalVEM.append(Signals_dict[tank][6])
            shower.Signals.nMuons.append(-1)


        # ----------------------------------------------------------------------
        # Reconstruction -------------------------------------------------------
        # ----------------------------------------------------------------------

        Laputop = frame["LaputopStandard"]
        LaputopParams = frame["LaputopStandardParams"]
        
        shower.Reconstruction.E_Proton = LaputopParams.e_proton
        shower.Reconstruction.E_Iron = LaputopParams.e_iron
        shower.Reconstruction.x = Laputop.pos.x
        shower.Reconstruction.y = Laputop.pos.y
        shower.Reconstruction.z = Laputop.pos.z
        shower.Reconstruction.zen = Laputop.dir.zenith
        shower.Reconstruction.S500 = LaputopParams.s500
        
        
        # ----------------------------------------------------------------------
        # Save Shower ----------------------------------------------------------
        # ----------------------------------------------------------------------

        if shower.Primary.Type == "PPlus":
            ProtonData.append(shower)
        elif shower.Primary.Type == "Fe56Nucleus":
            IronData.append(shower)
        else:
            print "ATTENTION: Run",shower.Run,"Event",shower.Event, \
                                    "has primary of type",shower.Primary.Type
            print "It will not be saved in the data files"




# save the data

save_location = './data/'

np.save(save_location+'proton_showers.npy',ProtonData)
np.save(save_location+'iron_showers.npy',IronData)



