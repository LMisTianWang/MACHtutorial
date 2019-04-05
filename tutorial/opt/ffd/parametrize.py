#rst Import libraries
import numpy
from pygeo import DVGeometry
from pywarp import MBMesh

#rst Create DVGeometry object
FFDFile = 'ffd.xyz'
DVGeo = DVGeometry(FFDFile)

#rst Create reference axis
nRefAxPts = DVGeo.addRefAxis('wing', xFraction=0.25, alignIndex='k')

#rst Dihedral
def dihedral(val, geo):
    C = geo.extractCoef('wing')
    for i in range(1, nRefAxPts):
        C[i,1] += val[i-1]
    geo.restoreCoef(C, 'wing')
#rst Twist
def twist(val, geo):
    for i in range(1, nRefAxPts):
        geo.rot_z['wing'].coef[i] = val[i-1]
#rst Taper
def taper(val, geo):
    s = geo.extractS('wing')
    slope = (val[1] - val[0])/(s[-1] - s[0])
    for i in range(nRefAxPts):
        geo.scale_x['wing'].coef[i] = slope * (s[i] - s[0]) + val[0]

#rst Add global dvs
nTwist = nRefAxPts - 1
DVGeo.addGeoDVGlobal(dvName='dihedral', value=[0]*nTwist, func=dihedral,
                    lower=-10, upper=10, scale=1)
DVGeo.addGeoDVGlobal(dvName='twist', value=[0]*nTwist, func=twist,
                    lower=-10, upper=10, scale=1)
DVGeo.addGeoDVGlobal(dvName='taper', value=[1]*2, func=taper,
                    lower=0.5, upper=1.5, scale=1)

#rst Add local dvs
# Comment out one or the other
DVGeo.addGeoDVLocal('local', lower=-0.5, upper=0.5, axis='y', scale=1)
DVGeo.addGeoDVSectionLocal('slocal', secIndex='k', axis=1, lower=-0.5, upper=0.5, scale=1)

#rst Embed points
gridFile = 'wing_vol.cgns'
meshOptions = {'gridFile':gridFile}
mesh = MBMesh(options=meshOptions)
coords = mesh.getSurfaceCoordinates()

DVGeo.addPointSet(coords, 'coords')

#rst Change dvs
dvDict = DVGeo.getValues()
dvDict['twist'] = numpy.linspace(0, 50, nRefAxPts)[1:]
dvDict['dihedral'] = numpy.linspace(0, 3, nRefAxPts)[1:]
dvDict['taper'] = numpy.array([1.2, 0.5])
dvDict['slocal'][::5] = 0.5
DVGeo.setDesignVars(dvDict)

#rst Update
DVGeo.update('coords')
DVGeo.writePlot3d('ffd_deformed.xyz')
DVGeo.writePointSet('coords', 'surf')
