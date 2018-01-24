"""
Generate a simple wing-box sructure for the mdo-tutorial wing using
pyLayout. This file will generate a .bdf file directly for use in TACS
"""
# ======================================================================
#         Import modules
# ======================================================================
import numpy
from pygeo import pyGeo, geo_utils
from pylayout import pyLayout

surfFile = 'wing.igs'
geo = pyGeo('iges', fileName=surfFile)
chords = [5, 1.25]
offsets = [0, 7.5]
span = 14.001
nribs  = 19
nbreak = 3
nspars = 10
elementOrder = 2
spanSpace = 5*numpy.ones(nribs-1, 'intc')
ribSpace = 2*numpy.ones(nspars+1, 'intc')
verticalSpace = 3
ribStiffnerSpace = 2
stringerSpace = 2
# Blanking for ribs
ribBlank = numpy.ones((nribs, nspars-1), 'intc') # None
ribBlank[0, :] = 0 # Blank root rib

# Blanking for spars
sparBlank = numpy.zeros((nspars, nribs-1), 'intc')
sparBlank[0, :] = 1 # Keep First
sparBlank[-1, :] = 1 # Keep Last

# Blanking for top_stringers:
topStringerBlank = numpy.zeros((nspars, nribs-1), 'intc')
topStringerBlank[:, :] = 1 # NO Blanking

# Blanking for bot_stringers:
botStringerBlank = numpy.zeros((nspars, nribs-1), 'intc')
botStringerBlank[:, :] = 1 # NO Blanking

# Blanking for rib stiffners:
ribStiffnerBlank = numpy.zeros((nribs, nspars), 'intc') # NO rib
                                                        # stiffeners
teEdgeList = []
# ------------------------------------------

# Setup 'X', the array of rib/spar intersections
leList = [[offsets[0] + 0.01*25*chords[0], 0, .01],
          [offsets[0] + 0.01*25*chords[0], 0, 1.5],
          [offsets[1] + 0.01*15*chords[1], 0, span]]

teList = [[offsets[0] + 0.01*80*chords[0], 0, .01],
          [offsets[0] + 0.01*80*chords[0], 0, 1.5],
          [offsets[1] + 0.01*75*chords[1], 0, span]]

X = numpy.zeros((nribs, nspars, 3))

# Now Fill in between le_list and te_list with liear_edge
X[0:nbreak, 0] = geo_utils.linearEdge(leList[0], leList[1], nbreak)
X[0:nbreak, -1] = geo_utils.linearEdge(teList[0], teList[1], nbreak)

X[nbreak-1:nribs, 0] = geo_utils.linearEdge(
    leList[1], leList[2], nribs-nbreak+1)
X[nbreak-1:nribs, -1] = geo_utils.linearEdge(
    teList[1], teList[2], nribs-nbreak+1)

# Finally fill in chord-wise with linear edges
for i in xrange(nribs):
    X[i, :] = geo_utils.linearEdge(X[i, 0], X[i, -1], nspars)

# Set up pyLayout
layout = pyLayout.Layout(geo, teEdgeList,
                         nribs, nspars,
                         elementOrder=elementOrder,
                         X=X,
                         ribBlank=ribBlank,
                         sparBlank=sparBlank,
                         topStringerBlank=topStringerBlank,
                         botStringerBlank=botStringerBlank,
                         ribStiffnerBlank=ribStiffnerBlank,
                         minStringer_height = 0.025,
                         maxStringer_height = 0.025,
                         spanSpace=spanSpace,
                         ribSpace=ribSpace,
                         vSpace=verticalSpace,
                         stringerSpace=stringerSpace,
                         ribStiffnerSpace=ribStiffnerSpace,
                         flipRibStiffner=False,
                         flipUp=False,
                         )

# Generate bdf file by calling 'finalize'
layout.finalize('wingbox.bdf')

# Also write a tecplot file so we can look at higher order models:
layout.writeTecplot('wingbox.dat')
