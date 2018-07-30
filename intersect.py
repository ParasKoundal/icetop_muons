#!/usr/bin/env python

# This code takes an icetop shower, matches it to its corsika file, then
# calculates how many muons hit IceTop (and where). It then stores this info in
# the shower object as shower.nMuons

# First is a function that determines whether a muon intersects a tank, given
# the muon's position and direction and the tank position
# Afterwards is the main part of the code that loops through the showers

import numpy as np
import glob

from icecube.dataio import I3File
from icecube import icetray, dataclasses #recclasses, simclasses




# ------------------------------------------------------------------------------
# Intersect function -----------------------------------------------------------
# ------------------------------------------------------------------------------

def intersect(x,y,z,nx,ny,nz,tank):
    
    # code to see if the particle intersects a detector
    # if it does, function returns True, else it returns False
    
    # tank coordinates
    xtank = tank[2]
    ytank = tank[3]
    ztank = tank[4]
    
    # tank dimensions
    radius  = 1.82/2.0+0.01 # meters
    height  = 0.90+0.02 # meters
    zTop    = 0.5*height
    zBottom = -0.5*height
    
    # Relative coordinates with respect to tank
    rx = x - xtank
    ry = y - ytank
    rz = z - ztank
    
    if nx**2 + ny**2 > 0:
        
        # Inclined Track
        
        # calculate the square-root argument
        arg = (nx**2 + ny**2)*radius**2 - (nx*ry - ny*rx)**2
        
        # if arg <= 0 the tank won't be hit
        if arg <= 0:
            return False

        # times of cylinder intersections (t1 < t2)
        t1 = (-(rx*nx + ry*ny) - np.sqrt(arg))/(nx**2 + ny**2)
        t2 = (-(rx*nx + ry*ny) + np.sqrt(arg))/(nx**2 + ny**2)
        
        # z-coordinates of cylinder intersections
        z1 = rz + nz*t1
        z2 = rz + nz*t2
        
        # If the intersections are both above or both below the tank, then the 
        # tank won't be hit. Otherwise, the tank is hit
        if z1 > zTop and z2 > zTop:
            return False
        elif z1 < zBottom and z2 < zBottom:
            return False
        else:
            return True

    else:
        
        # Vertical track
        
        if np.sqrt(rx**2 + ry**2) >= radius:
            return False
        else:
            return True
            



# ------------------------------------------------------------------------------
# MAIN -------------------------------------------------------------------------
# ------------------------------------------------------------------------------

#load the showers
data_location = './data/'
protondata = np.load(data_location + 'proton_showers_short.npy')
#irondata = np.load(data_location + 'iron_showers_short.npy')


#corsika file location
corsika_location = '/cr/data01/hagne/John_project/CORSIKA/muonsPROPER/'


# get geometry info
geom_file  = I3File("./data/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3.gz")
geom_frame = geom_file.pop_frame()
geometry   = geom_frame['I3Geometry']
geom_file.close()

# list of tanks
tanks = []
for i in range(1,82):
    # arrays are [station #, tank #, number of muons detected]
    # tank 1 contains DOMs 61,62; tank 2 contains DOMs 63,64
    tanks.append([i,1])
    tanks.append([i,2])
# tank coordinates -------------------
for tank in tanks:
    station = tank[0]
    if tank[1] == 1:
        om = 61
    else:
        om = 63
    # take average x,y of the two DOMs in the tank
    # DOM 1 (61/63)
    key1 = icetray.OMKey(station,om)
    xt1  = geometry.omgeo[key1].position.x 
    yt1  = geometry.omgeo[key1].position.y
    # DOM 2 (62/64)
    key2 = icetray.OMKey(station,om+1)
    xt2  = geometry.omgeo[key2].position.x 
    yt2  = geometry.omgeo[key2].position.y
    # tank position 
    xt = (xt1+xt2)/2.0
    yt = (yt1+yt2)/2.0
    # subtract 0.2 from z because center of ice is below center of tank
    zt = geometry.omgeo[key1].position.z - 0.2
    
    
    # append tank position, and a zero, which will later hold muon numbers
    tank.extend([xt,yt,zt,0])

   
# ------------------------------------------------------------------
# Lets just look at one corsika file for now
data = []
for shower in protondata:
    if shower.Run == 26:
        data.append(shower)

number = 4
data = data[number:number+1]
# ------------------------------------------------------------------

for shower in data:

    run = str(shower.Run)
    file_name = "Muons" + "000000"[:-len(run)] + run
    corsika_file = corsika_location + file_name
    
    # shower core
    xc = shower.Primary.x
    yc = shower.Primary.y
    zc = shower.Primary.z
    
    # resent the muon number per tank
    for tank in tanks:
        tank[5] = 0

    intmuon = 0 # number of intersecting muons
    # go through file line by line
    with open(corsika_file) as infile:
        for line in infile:
            line = line.split()
            
            # the particles
            if len(line) > 0 and line[0] == 'Muon:':
                x = float(line[1]) + xc
                y = float(line[2]) + yc
                z = zc

                nx = float(line[4])
                ny = float(line[5])
                nz = float(line[6])

                #ang = np.arctan(np.sqrt(nx**2+ny**2)/nz)*180/np.pi
                for tank in tanks:
                    flag = intersect(x,y,z,nx,ny,nz,tank)
                    if flag == True:
                        intmuon += 1
                        tank[5] += 1
                        break
    
    print intmuon,"muons intersected tanks"

    for i in range(len(tanks)):
        print "{0:<22}{1:<8}{2:<8}".format(shower.Signals.Tank[i], 
                                    int(shower.Signals.MuonPE[i]), tanks[i][5])

