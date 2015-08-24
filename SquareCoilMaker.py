#!/usr/bin/python
import argparse
from numpy import array, sqrt, pi, log


#
# Square pcb coil maker, for kicad's footprint file format.
#  The pad used as via in double sided coils are as of yet, untested.
#
class CoilMaker:
    def __init__(self, name, turns, sides, width, height, linew, space, via, drill):
        self.ComponentName = name
        self.NumberOfTurns = turns
        self.twoSided = sides
        self.Ymax = -((height/2)- linew/2)
        self.Xmax = (width/2)- linew/2
        self.Ymin = (height/2)- linew/2
        self.Xmin = -((width/2)- linew/2)
        self.corners = array([self.Xmax, self.Ymax, self.Xmin, self.Ymin])
        self.linewidth = linew
        self.spacing = space
        self.viasize = via
        self.drillsize = drill
        self.sign = array([1, -1, -1, 1])
        self.DL = self.spacing*2
        self.pseudoOuterDia = sqrt(height*width) # Is this mathematically correct?
        
        
    def DrawLine(self, tmpcorn, layer="F.Cu"):
        print("(fp_line (start %.2f %.2f) (end %.2f %.2f) (layer %s) (width %.2f))" % (tmpcorn[0],tmpcorn[1],tmpcorn[2],tmpcorn[3], layer, self.linewidth) )

    def CoilLinesFront(self, corners, DL): 
        print("""(pad 1 smd rect (at %.2f %.2f) (size %.2f %.2f) (layers F.Cu))"""% (corners[0], corners[3]+DL, self.linewidth, self.linewidth) )
        for turn in range(0,self.NumberOfTurns):
            self.DrawLine([corners[0], corners[3]+DL, corners[0], corners[1]]) #Right side
            self.DrawLine([corners[0], corners[1], corners[2], corners[1]]) #Top side
            self.DrawLine([corners[2], corners[1], corners[2], corners[3]]) #Left side
            self.DrawLine([corners[2], corners[3], corners[0]-DL, corners[3]]) #Bottom side
            if (turn == (self.NumberOfTurns -1) and self.twoSided == 1):
                #if (corners[0] - corners[2] < corners[3] - corners[1]):
                #    self.innerDia = (corners[0] - corners[2]) - self.linewidth
                #else:
                #    self.innerDia = (corners[3] - corners[1]) - self.linewidth
                self.innerDia = sqrt( ((corners[0] - corners[2]) - self.linewidth) * ((corners[3] - corners[1]) - self.linewidth) )
                print("""(pad 2 smd rect (at %.2f %.2f) (size %.2f %.2f) (layers F.Cu))"""% (corners[0]-DL, corners[3], self.linewidth, self.linewidth) )
            corners = corners - (DL*self.sign)

    def CoilLinesBack(self, corners, DL): 
        corners = corners - ( (DL*self.sign) * (self.NumberOfTurns-1))
        print(""" (pad "" thru_hole circle (at %.2f %.2f) (size %.2f %.2f) (drill %.2f) (layers *.Cu *.Mask F.SilkS)
        (zone_connect 2))""" % (corners[0]-DL, corners[3], self.viasize, self.viasize, self.drillsize ))
        
        #if ((corners[0]-DL) - corners[2] < corners[3] - corners[1]):
        #    self.innerDia = ((corners[0]-DL) - corners[2]) - self.linewidth
        #else:
        #    self.innerDia = (corners[3] - corners[1]) - self.linewidth
        self.innerDia = sqrt( (((corners[0]-DL) - corners[2]) - self.linewidth) *(  ((corners[3]+DL) - corners[1]) - self.linewidth ) )
        for turn in range(0,self.NumberOfTurns):
            self.DrawLine([corners[0]-DL, corners[3], corners[0]-DL, corners[1]], "B.Cu") #Right side
            self.DrawLine([corners[0]-DL, corners[1], corners[2], corners[1]], "B.Cu") #Top side
            self.DrawLine([corners[2], corners[1], corners[2], corners[3]+DL], "B.Cu") #Left side
            if (turn == (self.NumberOfTurns-1)):
                self.DrawLine([corners[2], corners[3]+DL, corners[0]-DL, corners[3]+DL], "B.Cu") #Bottom side
                print("""(pad 2 smd rect (at %.2f %.2f) (size %.2f %.2f) (layers B.Cu))"""% (corners[0]-DL, corners[3]+DL, self.linewidth, self.linewidth) )
            else:
                self.DrawLine([corners[2], corners[3]+DL, corners[0], corners[3]+DL], "B.Cu") #Bottom side
            corners = corners + (DL*self.sign)

    def MakeCoil(self):
        print( """(module "%s" (layer F.Cu) (tedit 55A681D4)
          (fp_text reference G*** (at 0 0) (layer F.SilkS) hide
            (effects (font (thickness 0.3)))
          )
          (fp_text value "%s" (at 0 -2.54) (layer F.SilkS) hide
            (effects (font (thickness 0.3)))
          )""" % (self.ComponentName, self.ComponentName))

        self.CoilLinesFront(self.corners, self.DL)
        if (self.twoSided == 2):
            self.CoilLinesBack(self.corners, self.DL)
        print(")")

    def getSingleInductance(self): 
        C1 = 1.27
        C2 = 2.07
        C3 = 0.18
        C4 = 0.13
        N = self.NumberOfTurns
        diaAvg = (10**-3 * (self.innerDia + self.pseudoOuterDia) / 2)
        permeability = 4*pi*10**(-7)
        fillratio = ( self.pseudoOuterDia - self.innerDia)/( self.pseudoOuterDia + self.innerDia)
        L = ((permeability *  N**2 *diaAvg* C1)/2) * (log(C2/fillratio) + C3*fillratio + C4* fillratio**2)
        return L

    def getDoubleInductance(self, thickness):
        N = self.NumberOfTurns
        X = thickness
        A = 0.184
        B = -0.525
        C = 1.038
        D = 1.001
        KC = (N**2)/( (A*X**3 + B*X**2 + C*X + D) * ( (1.67*N**2 -5.84*N +65)* 0.64) )
        L12 = self.getSingleInductance()
        Ltot = 2*L12 + 2*KC * L12
        return Ltot

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description="""Generates single or double sided board coils for use in kicad as footprints.
PS! The use of pad for via is yet untested. And the inductance calculation is rough at best""")
    parser.add_argument('-d', dest='sides', type=int, default=1, 
                        help="Number of layers used for coil, (max=2), default=1")
    parser.add_argument('-lw', dest='Linewidth', type=float, default=0.25,
                        help="Linewidth, default=0.25")
    parser.add_argument('-sp', dest='spacing', type=float, default=0.25, 
                        help="spacing, default=0.25")
    parser.add_argument('-x', '--width', dest='width', type=float, default=10, 
                        help="width (mm), default=10")
    parser.add_argument('-y', '--height', dest='height', type=float, default=20, 
                        help="height (mm), default=20")
    parser.add_argument('-via', dest='viasize', type=float, default=0.4, 
                        help="via diameter size (mm), default=0.4")
    parser.add_argument('-drill', dest='drillsize', type=float, default=0.3, 
                        help="drill diameter size (mm), default=0.3")
    parser.add_argument('-name', dest='componentname', default="Coil", 
                        help="Component name, default='Coil'")
    parser.add_argument('-N', dest='NumberOfTurns', type=int, default=7, 
                        help="Number of turns, default=7")
    parser.add_argument('--inductance', nargs='?', const=1, default=0, help="(Experimental)To output an rough estimation of inductance set this flag")
    parser.add_argument('-t', dest='thickness', type=float, default=1, 
                        help="Pcb thickness (mm), used in experimental inductance calculations, default=1")

    args = parser.parse_args()

    cm = CoilMaker(args.componentname, args.NumberOfTurns, args.sides, args.width, 
                   args.height, args.Linewidth, args.spacing, args.viasize, args.drillsize)
    cm.MakeCoil()
    
    if (args.inductance == 1):
        if (args.sides == 2):
            print("\n\nThe inductance of this double-layer-coil is approximately %g Henry" % cm.getDoubleInductance(args.thickness))
        else:
            print("\n\nThe inductance of this single-layer-coil is approximately %g Henry" % cm.getSingleInductance())
