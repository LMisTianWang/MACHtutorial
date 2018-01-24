# ======================================================================
#         Import modules
# ======================================================================
import numpy
from mpi4py import MPI
from baseclasses import *
from tacs import *
from repostate import *

# ================================================================
#                   INPUT INFORMATION
# ================================================================

outputDirectory =  './'
bdfFile = '../meshing/wingbox.bdf'
gcomm = comm = MPI.COMM_WORLD

# ================================================================
#       Define load case with StructProblem
# ================================================================
sp = StructProblem('lc0', loadFile='../loading/forces.txt', loadFactor=2.5,
                     evalFuncs=['mass','ks0', 'ks1', 'ks2'])]

# ================================================================
#       Setup structural solver
# ================================================================
structOptions = {
     'transferGaussOrder':3,
     'gravityVector':[0, -9.81, 0],
     'FamilySeparator':'..',
}
FEASolver = pytacs.pyTACS(bdfFile, comm=comm, options=structOptions)

# ================================================================
#       Set up DV Groups
# ================================================================
# Ribs
for i in xrange(19):
    FEASolver.addDVGroup('RIBS', include='RIB.%2.2d'%i)

# Spars
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
safetyFactor = 2.5
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
                            include=['L_SKING','L_STRING'], loadFactor=safetyFactor)

FEASolver.addFunction('max0', functions.MaxFailure, include=ks0, loadFactor=safetyFactor)
FEASolver.addFunction('max1', functions.MaxFailure, include=ks1, loadFactor=safetyFactor)
FEASolver.addFunction('max2', functions.MaxFailure, include=ks2, loadFactor=safetyFactor)

# ================================================================
#       Add loads
# ================================================================
# Different ways of setting loads
F = numpy.array([0.0, 3E5, 0.0]) #N
pt = numpy.array([8.0208, -0.0885, 14.000])
# add point load to wing tip
#FEASolver.addPointLoads(sp, pt, F)
# add distributed load to tip rib
#FEASolver.addLoadToComponents(sp, FEASolver.selectCompIDs(['RIB.18']), F=F)
# add pressure load (100 kPa) to upper skin of the wing
#FEASolver.addPressureLoad(sp, 100E3, include='U_SKIN')
# add inertial (gravity) loads
FEASolver.addInertialLoad(sp)

# ================================================================
#       Evaluate functions
# ================================================================
funcs = {}
FEASolver(sp)
FEASolver.evalFunctions(sp, funcs)
if comm.rank == 0:
    print funcs

# Write the solution
FEASolver.writeOutputFile('output.f5')
