import numpy
from pywarpustruct import USMesh
from pygeo import pyBlock, DVGeometry
from pyspline import pySpline
from pyoptsparse import SqliteDict
import warnings

# ffd deformation
FFDFile = 'ffd.fmt'
DVGeo = DVGeometry(FFDFile)

x = [0.0+5.41/4.0 , 6.24+1.29/4.0]
y = [0.0     , 1.16]
z = [-1.0E-03, 12.6]

nTwist = 5
tmp = pySpline.Curve(x=x, y=y, z=z, k=2)
X = tmp(numpy.linspace(0, 1, nTwist+1))
c1 = pySpline.Curve(X=X, k=2)
DVGeo.addRefAxis('wing', c1)

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
