# ==============================================================================
#       Import modules
# ==============================================================================
import numpy
import argparse
from mpi4py import MPI
from baseclasses import *
from tacs import *
from repostate import *
from pyoptsparse import *

# ==============================================================================
#       Set up structural problem
# ==============================================================================
sp = StructProblem('2.5gload', #loadFile='../INPUT/forces.txt', loadFactor=2.5,
                     evalFuncs=['mass','ks0', 'ks1', 'ks2'])

# ==============================================================================
#       Initialize TACS
# ==============================================================================
bdfFile = '../geometry/wingbox.bdf'
structOptions = {
    'transferGaussOrder':3,
    # 'familySeparator':'..'
    }
FEASolver = pytacs.pyTACS(bdfFile, options=structOptions)

# ==============================================================================
#       Set up design variable groups
# ==============================================================================
# Give each rib its own design variable group under the 'RIBS' category
# for i in xrange(1,19):
#     FEASolver.addDVGroup('RIBS', include='RIB.%2.2d'%i)
FEASolver.addDVGroup('RIBS', include='RIB')

# Split each spar into 9 design variable groups
FEASolver.addDVGroup('SPARS', include='SPAR.00', nGroup=9)
FEASolver.addDVGroup('SPARS', include='SPAR.09', nGroup=9)

# Stringers
groups = [['L_STRING.01', 'L_STRING.02', 'L_STRING.03'],
          ['L_STRING.04', 'L_STRING.05'],
          ['L_STRING.06', 'L_STRING.07', 'L_STRING.08']]

for group in groups:
    FEASolver.addDVGroup('STRINGERS', include=group, nGroup=9)

groups = [['U_STRING.01', 'U_STRING.02', 'U_STRING.03'],
          ['U_STRING.04', 'U_STRING.05'],
          ['U_STRING.06', 'U_STRING.07', 'U_STRING.08']]

for group in groups:
    FEASolver.addDVGroup('STRINGERS', include=group, nGroup=9)

# Skins
boundLists = [
    ['SPAR.00','SPAR.09','RIB.02','RIB.04'],
    ['SPAR.00','SPAR.09','RIB.04','RIB.06'],
    ['SPAR.00','SPAR.09','RIB.06','RIB.08'],
    ['SPAR.00','SPAR.09','RIB.08','RIB.10'],
    ['SPAR.00','SPAR.09','RIB.10','RIB.12'],
    ['SPAR.00','SPAR.09','RIB.12','RIB.14'],
    ['SPAR.00','SPAR.09','RIB.14','RIB.16'],
    ['SPAR.00','SPAR.09','RIB.16','RIB.18']]

for bounds in boundLists:
    FEASolver.addDVGroup('U_SKIN', include='U_SKIN', includeBounds=bounds)
    FEASolver.addDVGroup('L_SKIN', include='L_SKIN', includeBounds=bounds)

# Skins at root are not included...do them here
u_skins = []
l_skins = []
for i in xrange(1,19):
    u_skins.append('U_SKIN/U_SKIN.%3.3d'%(i))
    l_skins.append('L_SKIN/L_SKIN.%3.3d'%(i))

FEASolver.addDVGroup('U_SKIN', include=u_skins)
FEASolver.addDVGroup('L_SKIN', include=l_skins)

def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):
    rho_2024 = 2780
    E_2024 = 73.1e9
    ys_2024 = 324e6
    nu = 0.33
    t = .02
    tMin = 0.0016 # 1/16"
    tMax = 0.020
    kcorr = 5.0/6.0
    con = constitutive.isoFSDTStiffness(rho_2024, E_2024, nu, kcorr,
                                        ys_2024, t, dvNum, tMin, tMax)
    scale = [100.0]
    return con, scale

FEASolver.createTACSAssembler(conCallBack)

FEASolver.writeDVVisualization('dv_visual.f5')
# --------------- Add Functions -------------------------
# Mass Functions
FEASolver.addFunction('mass', functions.StructuralMass)
FEASolver.addFunction('uSkin', functions.StructuralMass, include='U_SKIN')
FEASolver.addFunction('lSkin', functions.StructuralMass, include='L_SKIN')
FEASolver.addFunction('leSpar', functions.StructuralMass, include=['SPAR.00'])
FEASolver.addFunction('teSpar', functions.StructuralMass, include=['SPAR.09'])
FEASolver.addFunction('ribs', functions.StructuralMass, include=['RIBS'])

# KS Functions
loadFactor = 2.5
KSWeight = 80.0
ks0 = FEASolver.addFunction('ks0', functions.AverageKSFailure, KSWeight=KSWeight,
                            include=['RIBS','SPARS'], loadFactor=loadFactor)
ks1 = FEASolver.addFunction('ks1', functions.AverageKSFailure,  KSWeight=KSWeight,
                            include=['U_SKIN','U_STRING'], loadFactor=loadFactor)
ks2 = FEASolver.addFunction('ks2', functions.AverageKSFailure, KSWeight=KSWeight,
                            include=['L_SKING','L_STRING'], loadFactor=loadFactor)

FEASolver.addFunction('max0',functions.MaxFailure, include=ks0, loadFactor=loadFactor)
FEASolver.addFunction('max1',functions.MaxFailure, include=ks1, loadFactor=loadFactor)
FEASolver.addFunction('max2',functions.MaxFailure, include=ks2, loadFactor=loadFactor)

FEASolver(sp)
funcs = {}
FEASolver.evalFunctions(sp, funcs)
print funcs
# Write the final solution
FEASolver.writeOutputFile(sp.name + '_final.f5')
