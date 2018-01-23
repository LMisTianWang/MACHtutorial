# ======================================================================
#         Import modules
# ======================================================================
import numpy
from mpi4py import MPI
from baseclasses import *
from adflow import ADFLOW
from pygeo import *
from pyspline import *
from repostate import *
from pyoptsparse import Optimization, OPT
from pywarp import *
from multipoint import *

# ======================================================================
#         Files/Directories
# ======================================================================
gridFile = 'wing_vol.cgns'
outputDirectory = './output/'

# ======================================================================
#         Create multipoint communication object
# ======================================================================
MP = multiPointSparse(MPI.COMM_WORLD)
MP.addProcessorSet('cruise', nMembers=1, memberSizes=4)
comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()

# ======================================================================
#         ADflow Set-up
# ======================================================================

aeroOptions = {
    # I/O Parameters
    'gridFile':gridFile,
    'outputDirectory':'output',
    'monitorvariables':['resrho','cl','cd'],
    'writeTecplotSurfaceSolution':True,

    # Physics Parameters
    'equationType':'RANS',

    # Solver Parameters
    'smoother':'dadi',
    'CFL':1.5,
    'CFLCoarse':1.25,
    'MGCycle':'3w',
    'MGStartLevel':-1,
    'nCyclesCoarse':250,

    # ANK Solver Parameters
    'useANKSolver':True,
    'ankswitchtol':1e-1,

    # NK Solver Parameters
    'useNKSolver':True,
    'nkswitchtol':1e-4,

    # Termination Criteria
    'L2Convergence':1e-8,
    'L2ConvergenceCoarse':1e-2,
    'nCycles':1000,

    # Adjoint Parameters
    'adjointL2Convergence':1e-8,
}

# Create solver
CFDSolver = ADFLOW(options=aeroOptions, comm=comm)
CFDSolver.addLiftDistribution(200, 'z')

# ======================================================================
#         Set up flow conditions with AeroProblem
# ======================================================================
ap = AeroProblem(name='fc', alpha=1.5, mach=0.82, altitude=10000,
                 areaRef=45.5, chordRef=3.25, evalFuncs=['cl','cd'])

# Add angle of attack variable
ap.addDV('alpha', value=1.5, lower=0, upper=10.0, scale=1.0)

# ======================================================================
#         Geometric Design Variable Set-up
# ======================================================================
# Create DVGeometry object
FFDFile = 'mdo_tutorial_ffd.fmt'
DVGeo = DVGeometry(FFDFile)

# Create reference axis
nRefAxPts = DVGeo.addRefAxis('wing', xFraction=0.25, alignIndex='k')
nTwist = nRefAxPts - 1

# Set up global design variables
def twist(val, geo):
    for i in xrange(1, nRefAxPts):
        geo.rot_z['wing'].coef[i] = val[i-1]

DVGeo.addGeoDVGlobal(dvName='twist', value=[0]*nTwist, func=twist,
                    lower=-10, upper=10, scale=1)

# Set up local design variables
DVGeo.addGeoDVLocal('local', lower=-0.5, upper=0.5, axis='y', scale=1)

# Add DVGeo object to CFD solver
CFDSolver.setDVGeo(DVGeo)

# ======================================================================
#         Mesh Warping Set-up
# ======================================================================
meshOptions = {'gridFile':gridFile, 'warpType':'algebraic',}
mesh = MBMesh(options=meshOptions, comm=comm)

# Add mesh warping object to CFD solver
CFDSolver.setMesh(mesh)

# ======================================================================
#         Functions:
# ======================================================================
def cruiseFuncs(x):
    if MPI.COMM_WORLD.rank == 0:
        print x
    funcs = {}
    DVGeo.setDesignVars(x)
    ap.setDesignVars(x)
    CFDSolver(ap)
    CFDSolver.evalFunctions(ap, funcs)
    CFDSolver.checkSolutionFailure(ap, funcs)
    if MPI.COMM_WORLD.rank == 0:
        print funcs
    return funcs

def cruiseFuncsSens(x, funcs):
    funcsSens = {}
    CFDSolver.evalFunctionsSens(ap, funcsSens)
    if MPI.COMM_WORLD.rank == 0:
        print funcsSens
    return funcsSens

def objCon(funcs, printOK):
    # Assemble the objective and any additional constraints:
    funcs['obj'] = funcs[ap['cd']]
    funcs['cl_con_'+ap.name] = funcs[ap['cl']] - 0.5
    if printOK:
       print 'funcs in obj:', funcs
    return funcs

# ======================================================================
#         Optimization Problem Set-up
# ======================================================================
# Create optimization problem
optProb = Optimization('opt', MP.obj, comm=MPI.COMM_WORLD)

# Add objective
optProb.addObj('obj', scale=1e4)

# Add variables from each AeroProblem
ap.addVariablesPyOpt(optProb)

# Add DVGeo variables
DVGeo.addVariablesPyOpt(optProb)

# Add constraints
optProb.addCon('cl_con_'+ap.name, lower=0.0, upper=0.0, scale=1.0)

# The MP object needs the 'obj' and 'sens' function for each proc set,
# the optimization problem and what the objcon function is:
MP.setProcSetObjFunc('cruise', cruiseFuncs)
MP.setProcSetSensFunc('cruise', cruiseFuncsSens)
MP.setObjCon(objCon)
MP.setOptProb(optProb)
optProb.printSparsity()

# Set up optimizer
optOptions = {
    'Major iterations limit':200,
    'Major step limit':2.0,
    'Major feasibility tolerance':1.0e-6,
    'Major optimality tolerance':1.0e-6,
}
opt = OPT('snopt', options=optOptions)

# Run Optimization
sol = opt(optProb, MP.sens, storeHistory='opt.hst')
if MPI.COMM_WORLD.rank == 0:
   print sol
