import numpy
from pygeo import DVGeometry

# ffd deformation
FFDFile = 'ffd.xyz'
DVGeo = DVGeometry(FFDFile)

nTwist = DVGeo.addRefAxis('wing', c1)

def twist(val, geo):
        for i in xrange(nTwist):
                geo.rot_z['wing'].coef[i+1] = val[i]

DVGeo.addGeoDVGlobal('twist', 0*numpy.ones(nTwist), twist,lower=-50, upper=50, scale=0.2)

dvDict = DVGeo.getValues()
dvDict['twist'] = numpy.linspace(0, 50, nTwist)
DVGeo.setDesignVars(dvDict)


# Mesh deformation
gridFile = 'wing_mvol2.cgns'
meshOptions = {'gridFile':gridFile,'warpType':'unstructured'}
mesh = USMesh(options=meshOptions)

coords0 = mesh.getSurfaceCoordinates()
coords = coords0.copy()
DVGeo.addPointSet(coords, 'coords')

mesh.setSurfaceCoordinates(DVGeo.update('coords'))
mesh.warpMesh()
DVGeo.writePlot3d('ffd-deform.fmt')
mesh.writeGrid('postwarp.cgns')
