
# This is a class to store relevant data from IceTop Showers, in a
# pythonic format that is easily accesible
# There are also functions to calculate lateral distance, 
# to match the OMKey to the Station/Tank name to be saved,
# and to print out a table that summarizes the shower data


import numpy as np


# DEFINITION OF SHOWER DATA STRUCTURE (used in "Showers.py") -----------
# ----------------------------------------------------------------------
class Shower:

    def __init__(self):
        self.Run            = None
        self.Event          = None
        self.Primary        = Primary()
        self.TotalMuons     = None
        self.nMuonPulses    = None
        self.Signals        = Signals()
        self.Reconstruction = Primary()

    # Functions to print a table that summarizes the shower
    # see the bottom for the function that prints the tables
    def Table(self,dist=0):
        print_table(self,dist)

# attributes of the primary of the shower
class Primary:
    def __init__(self):
        self.Type     = None
        self.Energy   = None
        self.x        = None
        self.y        = None
        self.z        = None
        self.zen      = None
    def CoreDist(self):
        return np.sqrt(self.x**2 + self.y**2)

# attributes of the signals from the shower
class Signals:
    def __init__(self):
        self.Tank      = []
        self.LatDist   = []
        self.MuonPE    = []
        self.OtherPE   = []
        self.TotalPE   = []
        self.HLCVEM    = []
        self.SLCVEM    = []
        self.TotalVEM  = []   
        self.nMuons    = []
        self.TimeDelay = []

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------




# This function is used to calculate lateral distances
def LatDist(xc,yc,zc,N,key,geometry):

    # location of current tank
    xi   = geometry.omgeo[key].position.x 
    yi   = geometry.omgeo[key].position.y 
    zi   = geometry.omgeo[key].position.z
    R    = [xi-xc, yi-yc, zi-zc] # vector that points from shower core to tank

    d    = np.linalg.norm(R) # distance from shower core
    latd = np.sqrt( d**2 - np.dot(N,R)**2 ) # distance from shower axis

    return latd



# This function matches the OMKey to the Station/Tank number to be saved
def which_tank(key):

    s = key.string
    t = key.om
    if s < 10:
        s = "0"+str(s)
    else:
        s = str(s)

    if t in [61,62]:
        t = "1"
    elif t in [63,64]:
        t = "2"

    tank = "Station"+s+"_Tank"+t
    return tank



# This function calculates the time delay of a signal
def time_delay(tcr,xc,yc,zc,N,key,geometry,tpulse):
    
    # direction of the shower
    nx,ny,nz = N
    
    # location of current tank
    xi   = geometry.omgeo[key].position.x 
    yi   = geometry.omgeo[key].position.y 
    zi   = geometry.omgeo[key].position.z
    
    c = 0.3 # speed of light (m/ns)

    time_delay = tcr + nx*(xi-xc)+ny*(yi-yc) - np.sqrt(1-nx**2-ny**2)*(zi-zc)/c - tpulse
    return time_delay




# The function below prints a table that summarizes the shower
# the header prints a summary of the shower
# after the header is a table that shows the tank-by-tank data
# there is an optional paramter 'dist' that allows you to put a cut on tank
# distance. Example: shower.Table(300) only prints the tanks that are greater
# than 300m from the shower core.

def print_table(self,dist):

    # HEADER --------------------------------------
    print "\n\n{0:->130}".format("")
    print "{0:->130}".format("")
    print "SHOWER SUMMARY"
    print "Run:",self.Run," Event:",self.Event
    print "Primary:",self.Primary.Type,"  {0:.4} eV".format(self.Primary.Energy),"  zenith: {0:.4}".format(self.Primary.zen)
    print "Shower core is {0:.2f}m from the center of IceTop".format(self.Primary.CoreDist())
    print str(self.TotalMuons)+" muons hit detectors"
    print "There were",self.nMuonPulses,"muon pulses in IceTop"
    print "{0:->130}".format("\n")

    # TANK-BY-TANK DATA ---------------------------
    if dist == 0:
        print "Below are the signals in each tank (excluding tanks with no signal):\n"
    else:
        print "Below are the signals in each tank >"+str(dist)+"m from the core (excluding tanks with no signal):\n"
    
    print "{0:<18}{1:>16}{2:^12}{3:^12}{4:^12}{5:^12}{6:^12}{7:^12}{8:^8}{9:>16}".format(
            " ","Lateral Dist (m)","Muon PEs","Other PEs","Total PEs","HLCs (VEM)","SLCs (VEM)","Total VEM","nMuons","Time Delay (ns)")
    s = self.Signals
    for i in range(len(s.Tank)):
        if s.TotalPE[i] + s.TotalVEM[i] != 0:
            if s.LatDist[i] >= dist:
                print "{0:<18}{1:>10.2f}{2:>14.0f}{3:>12.0f}{4:>12.0f}{5:>12.2f}{6:>12.2f}{7:>12.2f}{8:>8.0f}{9:>16.3f}".format(
                    s.Tank[i],s.LatDist[i],s.MuonPE[i],s.OtherPE[i],s.TotalPE[i],s.HLCVEM[i],s.SLCVEM[i],s.TotalVEM[i],s.nMuons[i],s.TimeDelay[i])


    # Bottom frame
    print "{0:->130}".format("")
    print "{0:->130}".format("\n")






