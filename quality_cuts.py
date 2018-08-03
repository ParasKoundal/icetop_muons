#!/usr/bin/env python

import numpy as np
from numpy.linalg import norm
import glob
import os

from icecube.dataio import I3File
from icecube import icetray, dataclasses, recclasses,simclasses

#data files location
data_location = '/cr/data01/hagne/John_project/Donghwa/'
# where to save the frames that passed the quality cuts
cut_location = "./data/i3files"

# get geometry info
geom_file  = I3File("GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz")
geom_frame = geom_file.pop_frame()
geometry   = geom_frame['I3Geometry']
geom_file.close()
iron_energy   = []
proton_energy = []


# --------------------------------------------------------------------------
# Now get the data from the files ------------------------------------------

# list of appropriate files in folder
files  = glob.glob(data_location + 'Level2*')


total_frames = 0 # want to print out how many frames passed

# loop through files
nfiles = len(files)
for file_number in range(nfiles):

    file_name = files[file_number]
    i3f = I3File(file_name)

    cut_file_name = cut_location + file_name[len(data_location):]
    cut_file = I3File(cut_file_name, I3File.Writing)


    print "Starting",file_name,"(file",file_number+1,"of",str(nfiles)+")"

    passed_frames = 0 # how many frames passed the cuts
    
    while i3f.more():
        frame = i3f.pop_physics()
        header = frame["I3EventHeader"]
        if header.sub_event_stream == "ice_top":

            run = header.run_id
            event = header.event_id

            # Apply quality cuts -------------------------------
            # Stage 1: cuts on reconstruction params and frame -

            laputop = frame["LaputopStandard"]
            xcr = laputop.pos.x
            ycr = laputop.pos.y
            cdr = np.sqrt(xcr**2 + ycr**2) # reconstructed core distance
            zenr = laputop.dir.zenith
            S125 = frame["LaputopStandardParams"].s125

            tcr = laputop.time # reconstructed core time, needed later

            # there is one more cut I can apply before looking at pulses
            # there is a flag for whether 5 stations were triggered
            five_stations_triggered = frame["QFilterMask"]["IceTopSTA5_12"].condition_passed

            quality_flag = [0,0,0,0,0]
            if cdr < 400: # core distance inside containment area
                quality_flag[0] = 1
            if np.cos(zenr) >= 0.8: # shower not too slanted
                quality_flag[1] = 1
            if S125 >= 1: # strong enough signal at 125m from core
                quality_flag[2] = 1
            if five_stations_triggered == True: # five stations triggered
                quality_flag[3] = 1
            if ('MCPrimary' in frame and  # Does the frame have all the modules we want?
                'OfflineIceTopHLCVEMPulses' in frame and
                'OfflineIceTopSLCVEMPulses' in frame and
                'MCPrimaryInfo' in frame and
                'IceTopComponentPulses_Muon' in frame and
                'IceTopComponentPulses_Electron' in frame and
                'IceTopComponentPulses_ElectronFromChargedMesons' in frame and
                'IceTopComponentPulses_Gamma' in frame and
                'IceTopComponentPulses_GammaFromChargedMesons' in frame and
                'IceTopComponentPulses_Hadron' in frame):
                quality_flag[4] = 1


            if sum(quality_flag) == 5: # does the event pass all of the previous cuts?

                # Apply quality cuts -------------------------------
                # Stage 2: cuts on pulse data ----------------------

                # --------------------
                # HLC tanks ----------
                # --------------------
                events_HLC  = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,'OfflineIceTopHLCVEMPulses')
                oms_HLC     = []
                strings_HLC = []
                charges_HLC = []
                times_HLC   = []
                dist_HLC    = []
                latdist_HLC = []

                # pulse data --
                for key, pulses in events_HLC:
                    for p in pulses:
                        if np.abs(tcr - p.time) <= 1000: # only take events within 1 micro sec of core
                            oms_HLC.append(key.om) # tank/PMT id
                            strings_HLC.append(key.string) # station id
                            charges_HLC.append(p.charge) # charge deposited

                # distances --
                omkey_HLC = [icetray.OMKey(strings_HLC[i],oms_HLC[i]) for i in range(len(strings_HLC))]
                for i in range(len(strings_HLC)):
                    xi   = geometry.omgeo[omkey_HLC[i]].position.x 
                    yi   = geometry.omgeo[omkey_HLC[i]].position.y 
                    d = np.sqrt(xi**2 + yi**2)

                    dist_HLC.append(d)

                # --------------------
                # SLC tanks ----------
                # --------------------
                events_SLC  = dataclasses.I3RecoPulseSeriesMap.from_frame(frame,'OfflineIceTopSLCVEMPulses')
                oms_SLC     = []
                strings_SLC = []
                charges_SLC = []
                times_SLC   = []
                dist_SLC    = []
                latdist_SLC = []

                # pulse data --
                for key, pulses in events_SLC:
                    for p in pulses:
                        if np.abs(tcr - p.time) <= 1000: # only take events within 1 micro sec of core
                            oms_SLC.append(key.om) # tank/PMT id
                            strings_SLC.append(key.string) # station id
                            charges_SLC.append(p.charge) # charge deposited

                # distances --
                omkey_SLC = [icetray.OMKey(strings_SLC[i],oms_SLC[i]) for i in range(len(strings_SLC))]
                for i in range(len(strings_SLC)):
                    xi   = geometry.omgeo[omkey_SLC[i]].position.x 
                    yi   = geometry.omgeo[omkey_SLC[i]].position.y 
                    d = np.sqrt(xi**2 + yi**2)

                    dist_SLC.append(d)

                all_charges = np.append(charges_HLC,charges_SLC)
                all_dist    = np.append(dist_HLC,dist_SLC)

                max_charge      = max(all_charges)
                max_charge_dist = all_dist[np.argmax(all_charges)]
                if max_charge >= 6 and max_charge_dist <= 300:
                    # this frame passed all the quality cuts
                    passed_frames += 1
                    total_frames += 1

                    # add it to the cut file
                    # ------------------------------------
                    # what frames does this frame rely on?
                    parents = i3f.get_mixed_frames()
                    for P in parents:
                        cut_file.push(P)
                    # save the frame to the file
                    cut_file.push(frame)

    cut_file.close()
    if passed_frames == 0: # we don't need the file if it doesn't contain any frames!
        os.system("rm {0}".format(cut_file_name))

    #os.system("rm {0}".format(file_name)) # remove the original data file

print "-------------------------"
print total_frames,"frames passed the cut"








