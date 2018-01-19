# Import the librabry
import numpy
from pygeo import *
from adflow import *

    # Ignore deprecation warnings
import warnings
warnings.filterwarnings("ignore")

gridFile = 'wing_mvol2.cgns'
FFDFile = 'FFD.fmt'

aeroOptions = {'gridFile': gridFile}
CFDSolver = ADFLOW(options=aeroOptions)
DVGeo = DVGeometry(FFDFile)
DVCon = DVConstraints()
DVCon.setDVGeo(DVGeo)
DVCon.setSurface(CFDSolver.getTriangulatedMeshSurface())

# Choose the axis for the projection:  (X^Vect(wingspan direction))
DVCon.addProjectedAreaConstraint(name='projy', scaled=False, axis='y')
area1 = DVCon.constraints['projAreaCon']['projy'].X0

print 'Original area:', area1
