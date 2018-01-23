# Import libraries
import numpy
from pygeo import DVGeometry

# Create DVGeometry object
FFDFile = 'ffd.xyz'
DVGeo = DVGeometry(FFDFile)

# Create reference axis
nRefAxPts = DVGeo.addRefAxis('wing', xFraction=0.25, alignIndex='k')
DVGeo.writeRefAxes('refaxes.dat')   # write reference axis to file
nTwist = nRefAxPts - 1

# Set up global design variable callback functions
def twist(val, geo):
    for i in range(1, nRefAxPts):
        geo.rot_z['wing'].coef[i] = val[i-1]

def dihedral(val, geo):
    C = geo.extractCoef('wing')
    for i in range(1, nRefAxPts):
        C[i,1] = val[i-1]
    geo.restoreCoef(C, 'wing')

def taper(val, geo):
    s = geo.extractS('wing')
    slope = (val[1] - val[0])/(s[-1] - s[0])
    for i in range(nRefAxPts):
        geo.scale_x['wing'].[i] = slope * (s[i] - s[0]) + val[0]

# Add global design variables to DVGeo
DVGeo.addGeoDVGlobal(dvName='twist', value=[0]*nTwist, func=twist,
                    lower=-10, upper=10, scale=1)
DVGeo.addGeoDVGlobal(dvName='dihedral', value=[0]*nTwist, func=dihedral,
                    lower=-10, upper=10, scale=1)
DVGeo.addGeoDVGlobal(dvName='taper', value=[1]*2, func=taper,
                    lower=0.5, upper=1.5, scale=1)

# Set up local design variables
DVGeo.addGeoDVLocal('local', lower=-0.5, upper=0.5, axis='y', scale=1)
DVGeo.addGeoDVSectionLocal('slocal', secIndex='k', axis=1, lower=-0.5, upper=0.5, scale=1))

# Embed point set in FFD
coords = numpy.array([0, 0, 0])
DVGeo.addPointSet(coords, 'coords')

# Change design variables
dvDict = DVGeo.getValues()
dvDict['twist'] = numpy.linspace(0, 50, nTwist)
dvDict['dihedral'] = numpy.linspace(0, 3, nTwist)
dvDict['taper'] = numpy.linspace(0, 3, nTwist)
dvDict['slocal'][::5] = 0.5
DVGeo.setDesignVars(dvDict)

# Update point set
DVGeo.update('coords')

# Write deformed ffd
DVGeo.writePlot3d('ffd_deformed.xyz')
