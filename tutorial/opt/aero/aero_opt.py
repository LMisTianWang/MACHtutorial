# ======================================================================
#         Import modules
# ======================================================================
#rst Imports (beg)
from __future__ import print_function
from mpi4py import MPI
from baseclasses import AeroProblem
from adflow import ADFLOW
from pygeo import DVGeometry, DVConstraints
from pyoptsparse import Optimization, OPT
from pywarp import MBMesh
from multipoint import multiPointSparse
#rst Imports (end)
# ======================================================================
#         Create multipoint communication object
# ======================================================================
#rst multipoint (beg)
MP = multiPointSparse(MPI.COMM_WORLD)
MP.addProcessorSet('cruise', nMembers=1, memberSizes=4)
comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()
#rst multipoint (end)
# ======================================================================
#         ADflow Set-up
# ======================================================================
#rst adflow (beg)
gridFile = 'wing_vol.cgns'
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
#rst adflow (end)
# ======================================================================
#         Set up flow conditions with AeroProblem
# ======================================================================
#rst aeroproblem (beg)
ap = AeroProblem(name='fc', alpha=1.5, mach=0.8, altitude=10000,
                 areaRef=45.5, chordRef=3.25, evalFuncs=['cl','cd'])

# Add angle of attack variable
ap.addDV('alpha', value=1.5, lower=0, upper=10.0, scale=0.1)
#rst aeroproblem (end)
# ======================================================================
#         Geometric Design Variable Set-up
# ======================================================================
#rst dvgeo (beg)
# Create DVGeometry object
FFDFile = 'ffd.xyz'
DVGeo = DVGeometry(FFDFile)

# Create reference axis
nRefAxPts = DVGeo.addRefAxis('wing', xFraction=0.25, alignIndex='k')
nTwist = nRefAxPts - 1

# Set up global design variables
def twist(val, geo):
    for i in range(1, nRefAxPts):
        geo.rot_z['wing'].coef[i] = val[i-1]

DVGeo.addGeoDVGlobal(dvName='twist', value=[0]*nTwist, func=twist,
                    lower=-10, upper=10, scale=0.01)

# Set up local design variables
DVGeo.addGeoDVLocal('local', lower=-0.5, upper=0.5, axis='y', scale=1)

# Add DVGeo object to CFD solver
CFDSolver.setDVGeo(DVGeo)
#rst dvgeo (end)
# ======================================================================
#         DVConstraint Setup
# ======================================================================
#rst dvcon (beg)
DVCon = DVConstraints()
DVCon.setDVGeo(DVGeo)

# Only ADflow has the getTriangulatedSurface Function
DVCon.setSurface(CFDSolver.getTriangulatedMeshSurface())

# Volume constraints
leList = [[0.1, 0, 0.001], [0.1+7.5, 0, 14]]
teList = [[4.2, 0, 0.001], [8.5, 0, 14]]
DVCon.addVolumeConstraint(leList, teList, 20, 20, lower=1.0)

# Thickness constraints
DVCon.addThicknessConstraints2D(leList, teList, 10, 10, lower=1.0)

# Le/Te constraints
DVCon.addLeTeConstraints(0, 'iLow')
DVCon.addLeTeConstraints(0, 'iHigh')

if comm.rank == 0:
    DVCon.writeTecplot('constraints.dat')
#rst dvcon (end)
# ======================================================================
#         Mesh Warping Set-up
# ======================================================================
#rst warp (beg)
meshOptions = {'gridFile':gridFile, 'warpType':'algebraic',}
mesh = MBMesh(options=meshOptions, comm=comm)
CFDSolver.setMesh(mesh)
#rst warp (end)
# ======================================================================
#         Functions:
# ======================================================================
#rst funcs (beg)
def cruiseFuncs(x):
    if comm.rank == 0:
        print(x)
    # Set design vars
    DVGeo.setDesignVars(x)
    ap.setDesignVars(x)
    # Run CFD
    CFDSolver(ap)
    # Evaluate functions
    funcs = {}
    DVCon.evalFunctions(funcs)
    CFDSolver.evalFunctions(ap, funcs)
    CFDSolver.checkSolutionFailure(ap, funcs)
    if comm.rank == 0:
        print(funcs)
    return funcs

def cruiseFuncsSens(x, funcs):
    funcsSens = {}
    DVCon.evalFunctionsSens(funcsSens)
    CFDSolver.evalFunctionsSens(ap, funcsSens)
    if comm.rank == 0:
        print(funcsSens)
    return funcsSens

def objCon(funcs, printOK):
    # Assemble the objective and any additional constraints:
    funcs['obj'] = funcs[ap['cd']]
    funcs['cl_con_'+ap.name] = funcs[ap['cl']] - 0.5
    if printOK:
       print('funcs in obj:', funcs)
    return funcs
#rst funcs (end)
# ======================================================================
#         Optimization Problem Set-up
# ======================================================================
#rst optprob (beg)
# Create optimization problem
optProb = Optimization('opt', MP.obj, comm=comm)

# Add objective
optProb.addObj('obj', scale=1e2)

# Add variables from the AeroProblem
ap.addVariablesPyOpt(optProb)

# Add DVGeo variables
DVGeo.addVariablesPyOpt(optProb)

# Add constraints
DVCon.addConstraintsPyOpt(optProb)
optProb.addCon('cl_con_'+ap.name, lower=0.0, upper=0.0, scale=10.0)

# The MP object needs the 'obj' and 'sens' function for each proc set,
# the optimization problem and what the objcon function is:
MP.setProcSetObjFunc('cruise', cruiseFuncs)
MP.setProcSetSensFunc('cruise', cruiseFuncsSens)
MP.setObjCon(objCon)
MP.setOptProb(optProb)
optProb.printSparsity()
#rst optprob (end)
#rst optimizer
# Set up optimizer
optOptions = {
    'Major iterations limit':200,
    'Major step limit':2.0,
    'Major feasibility tolerance':1.0e-4,
    'Major optimality tolerance':5.0e-4,
}
opt = OPT('snopt', options=optOptions)

# Run Optimization
sol = opt(optProb, MP.sens, storeHistory='opt.hst')
if comm.rank == 0:
   print(sol)
