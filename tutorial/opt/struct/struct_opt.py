# ======================================================================
#         Import modules
# ======================================================================
import numpy
import argparse
from mpi4py import MPI
from baseclasses import *
from tacs import *
from repostate import *
from pyoptsparse import *

# ================================================================
#       Define load case with StructProblem
# ================================================================
sp = StructProblem('lc0', loadFile='../../struct/loading/forces.txt', loadFactor=2.5,
                     evalFuncs=['mass','ks0', 'ks1', 'ks2'])

# ================================================================
#       Setup structural solver
# ================================================================
structOptions = {
     'transferGaussOrder':3,
     'gravityVector':[0, -9.81, 0],
}
bdfFile = '../../struct/meshing/wingbox.bdf'
FEASolver = pytacs.pyTACS(bdfFile, options=structOptions)

# ================================================================
#       Set up DV Groups
# ================================================================
# Ribs (19 total ribs)
for i in xrange(19):
    FEASolver.addDVGroup('RIBS', include='RIB.%2.2d'%i)

# Spars (each with 9 spanwise sections)
FEASolver.addDVGroup('SPARS', include='SPAR.00', nGroup=9)  # front spar
FEASolver.addDVGroup('SPARS', include='SPAR.09', nGroup=9)  # rear spar

# Stringers (each with 18 spanwise sections)
groups = [['L_STRING.01', 'L_STRING.02', 'L_STRING.03'],    # front 3
          ['L_STRING.04', 'L_STRING.05'],                   # middle 2
          ['L_STRING.06', 'L_STRING.07', 'L_STRING.08']]    # rear 3

for group in groups:
    FEASolver.addDVGroup('STRINGERS', include=group, nGroup=9)

groups = [['U_STRING.01', 'U_STRING.02', 'U_STRING.03'],
          ['U_STRING.04', 'U_STRING.05'],
          ['U_STRING.06', 'U_STRING.07', 'U_STRING.08']]

for group in groups:
    FEASolver.addDVGroup('STRINGERS', include=group, nGroup=9)

# Skins (group skins in sections split by every other rib)
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

# ================================================================
#       Set-up constitutive properties for each DVGroup
# ================================================================
def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):
    rho_2024 = 2780 #kg/m^3
    E_2024 = 73.1e9 #Pa
    ys_2024 = 324e6 #Pa
    nu = 0.33
    t = .02 #m
    tMin = 0.0016 # 1/16"
    tMax = 0.020 #m
    kcorr = 5.0/6.0
    con = constitutive.isoFSDTStiffness(rho_2024, E_2024, nu, kcorr,
                                        ys_2024, t, dvNum, tMin, tMax)
    scale = [100.0]
    return con, scale

FEASolver.createTACSAssembler(conCallBack)
# Write output file to visualize design variable groups
FEASolver.writeDVVisualization('DV_groups.f5')
# ================================================================
#       Add functions
# ================================================================
safetyFactor = 1.5
KSWeight = 80.0
# Mass Functions
FEASolver.addFunction('mass', functions.StructuralMass)
FEASolver.addFunction('uSkin', functions.StructuralMass, include='U_SKIN')
FEASolver.addFunction('lSkin', functions.StructuralMass, include='L_SKIN')
FEASolver.addFunction('leSpar', functions.StructuralMass, include=['SPAR.00'])
FEASolver.addFunction('teSpar', functions.StructuralMass, include=['SPAR.09'])
FEASolver.addFunction('ribs', functions.StructuralMass, include=['RIBS'])

# KS Failure Functions
ks0 = FEASolver.addFunction('ks0', functions.AverageKSFailure, KSWeight=KSWeight,
                            include=['RIBS','SPARS'], loadFactor=safetyFactor)
ks1 = FEASolver.addFunction('ks1', functions.AverageKSFailure,  KSWeight=KSWeight,
                            include=['U_SKIN','U_STRING'], loadFactor=safetyFactor)
ks2 = FEASolver.addFunction('ks2', functions.AverageKSFailure, KSWeight=KSWeight,
                            include=['L_SKIN','L_STRING'], loadFactor=safetyFactor)

# ================================================================
#       Add loads
# ================================================================
FEASolver.addInertialLoad(sp)

# ================================================================
#       Set up optimization
# ================================================================
def obj(x):
    funcs = {}
    FEASolver.setDesignVars(x)
    FEASolver(sp)
    FEASolver.evalFunctions(sp, funcs)
    if MPI.COMM_WORLD.rank == 0:
        print funcs
    return funcs

def sens(x, funcs):
    funcsSens = {}
    FEASolver.evalFunctionsSens(sp, funcsSens)
    return funcsSens

# Set up the optimization problem
optProb = Optimization('Mass minimization', obj)
optProb.addObj('lc0_mass')
FEASolver.addVariablesPyOpt(optProb)

for i in range(3):
    optProb.addCon('%s_ks%d'% (sp.name, i), upper=1.0)

if MPI.COMM_WORLD.rank == 0:
    print optProb
optProb.printSparsity()

optOptions = {}
opt = OPT('snopt', options=optOptions)
sol = opt(optProb, sens=sens, storeHistory='struct.hst')

# Write the final solution
FEASolver.writeOutputFile('final.f5')
