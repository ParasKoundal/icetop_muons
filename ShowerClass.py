
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
        self.Run         = None
        self.Event       = None
        self.Primary     = Primary()
        self.nMuons      = None
        self.TotalMuons  = None
        self.nMuonPulses = None
        self.Signals     = Signals()
        self.S500        = None

    # Functions to print a table that summarizes the shower
    # see the bottom for the function that prints the tables
    def Table(self):
        print_table(self,"normal")
    def Table_300m(self):
        print_table(self,"300m")
    def Table_Long(self):
        print_table(self,"long")


# attributes of the primary of the shower
class Primary:
    def __init__(self):
        self.Type     = None
        self.Energy   = None
        self.x        = None
        self.y        = None
        self.z        = None
    def CoreDist(self):
        return np.sqrt(self.x**2 + self.y**2)

# attributes of the signals from the shower
class Signals:
    def __init__(self):
        self.Tank     = []
        self.LatDist  = []
        self.MuonPE   = []
        self.OtherPE  = []
        self.TotalPE  = []
        self.HLCVEM   = []
        self.SLCVEM   = []
        self.TotalVEM = []   
        self.nMuons   = []

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------




# This function is used to calculate lateral distances
def LatDist(xc,yc,zc,N,key,geometry):

    # location of current tank
    xi   = geometry.omgeo[key].position.x 
    yi   = geometry.omgeo[key].position.y 
    zi   = geometry.omgeo[key].position.z
    R    = [xi-xc, yi-yc, zi-zc] # vector that points from shower core to the event

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






# The function below prints a table that summarizes the shower
# the header is always the same, but there are three options for printing out the tank-by-tank data:
#   normal - this prints out every tank with a signal
#   past_300 - this only prints tanks whose lateral distance from the shower core is > 300m
#   long - this prints out every tank, even the ones without a signal

def print_table(self,flag):

    # HEADER --------------------------------------
    print "\n\n{0:->130}".format("")
    print "{0:->130}".format("")
    print "SHOWER SUMMARY"
    print "Run:",self.Run," Event:",self.Event
    print "Primary:",self.Primary.Type,"{0:.4} eV".format(self.Primary.Energy)
    print "Shower core is {0:.2f}m from the center of IceTop".format(self.Primary.CoreDist())
    print "The original Corsika shower had {0:,} muons".format(self.TotalMuons)
    print "There were",self.nMuonPulses,"muon pulses in IceTop"
    print "S500 = {0:.4f}".format(self.S500)
    print "{0:->130}".format("\n")

    # TANK-BY-TANK DARA ---------------------------

    # NORMAL TABLE
    if flag == "normal":
        print "Below are the signals in each tank (excluding tanks with no signal):\n"

        print "{0:<20}{1:>10}{2:^15}{3:^15}{4:^15}{5:^15}{6:^15}{7:^15}".format(
            " ","Lateral Dist (m)","Muon PEs","Other PEs","Total PEs","HLCs (VEM)","SLCs (VEM)","Total Signal (VEM)")
        s = self.Signals
        totals = np.zeros(6)
        nrows = 0.0
        for i in range(len(s.Tank)):
            if s.TotalPE[i] + s.TotalVEM[i] != 0:
                signals = [s.MuonPE[i],s.OtherPE[i],s.TotalPE[i],s.HLCVEM[i],s.SLCVEM[i],s.TotalVEM[i]]
                for j in range(len(signals)):
                    totals[j] += signals[j]
                nrows += 1.0
                print "{0:<20}{1:>10.2f}{2:>15.0f}{3:>15.0f}{4:>15.0f}{5:>15.2f}{6:>15.2f}{7:>15.2f}".format(
                    s.Tank[i],s.LatDist[i],signals[0],signals[1],signals[2],signals[3],
                    signals[4],signals[5])
        print "{0:->130}".format("")
        print "{0:>30}{1:>15.0f}{2:>15.0f}{3:>15.0f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Total:",totals[0],totals[1],
            totals[2],totals[3],totals[4],totals[5])
        print "{0:>30}{1:>15.2f}{2:>15.2f}{3:>15.2f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Mean:",totals[0]/nrows,
            totals[1]/nrows,totals[2]/nrows,totals[3]/nrows,totals[4]/nrows,totals[5]/nrows)

    # >300m TABLE
    elif flag == "300m":
        print "Below are the signals in each tank that is greater than 300m from the shower core:\n"

        print "{0:<20}{1:>10}{2:^15}{3:^15}{4:^15}{5:^15}{6:^15}{7:^15}".format(
            " ","Lateral Dist (m)","Muon PEs","Other PEs","Total PEs","HLCs (VEM)","SLCs (VEM)","Total Signal (VEM)")
        s = self.Signals
        totals = np.zeros(6)
        nrows = 0.0
        for i in range(len(s.Tank)):
            if s.TotalPE[i] + s.TotalVEM[i] != 0:
                if s.LatDist[i] > 300:
                    signals = [s.MuonPE[i],s.OtherPE[i],s.TotalPE[i],s.HLCVEM[i],s.SLCVEM[i],s.TotalVEM[i]]
                    for j in range(len(signals)):
                        totals[j] += signals[j]
                    nrows += 1.0
                    print "{0:<20}{1:>10.2f}{2:>15.0f}{3:>15.0f}{4:>15.0f}{5:>15.2f}{6:>15.2f}{7:>15.2f}".format(
                        s.Tank[i],s.LatDist[i],signals[0],signals[1],signals[2],signals[3],
                        signals[4],signals[5])
        print "{0:->130}".format("")
        print "{0:>30}{1:>15.0f}{2:>15.0f}{3:>15.0f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Total:",totals[0],totals[1],
            totals[2],totals[3],totals[4],totals[5])
        print "{0:>30}{1:>15.2f}{2:>15.2f}{3:>15.2f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Mean:",totals[0]/nrows,
            totals[1]/nrows,totals[2]/nrows,totals[3]/nrows,totals[4]/nrows,totals[5]/nrows)

    # LONG TABLE
    elif flag == "long":
        print "Below are the signals in each tank:\n"

        print "{0:<20}{1:>10}{2:^15}{3:^15}{4:^15}{5:^15}{6:^15}{7:^15}".format(
            " ","Lateral Dist (m)","Muon PEs","Other PEs","Total PEs","HLCs (VEM)","SLCs (VEM)","Total Signal (VEM)")
        s = self.Signals
        totals = np.zeros(6)
        nrows = 0.0
        for i in range(len(s.Tank)):
            signals = [s.MuonPE[i],s.OtherPE[i],s.TotalPE[i],s.HLCVEM[i],s.SLCVEM[i],s.TotalVEM[i]]
            for j in range(len(signals)):
                totals[j] += signals[j]
            nrows += 1.0
            print "{0:<20}{1:>10.2f}{2:>15.0f}{3:>15.0f}{4:>15.0f}{5:>15.2f}{6:>15.2f}{7:>15.2f}".format(
                s.Tank[i],s.LatDist[i],signals[0],signals[1],signals[2],signals[3],
                signals[4],signals[5])
        print "{0:->130}".format("")
        print "{0:>30}{1:>15.0f}{2:>15.0f}{3:>15.0f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Total:",totals[0],totals[1],
            totals[2],totals[3],totals[4],totals[5])
        print "{0:>30}{1:>15.2f}{2:>15.2f}{3:>15.2f}{4:>15.2f}{5:>15.2f}{6:>15.2f}".format("Mean:",totals[0]/nrows,
            totals[1]/nrows,totals[2]/nrows,totals[3]/nrows,totals[4]/nrows,totals[5]/nrows)

    # Bottom frame
    print "{0:->130}".format("")
    print "{0:->130}".format("\n")






