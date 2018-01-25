# ======================================================================
#         Import modules
# ======================================================================
import os
import argparse
import numpy
import sys
from mpi4py import MPI
from baseclasses import *
from tacs import *
from tripan import TRIPAN
from adflow import ADFLOW
from pywarp import *
from pygeo import *
from pyspline import *
from multipoint import *
from pyaerostructure import *
from repostate import *
from pyoptsparse import Optimization, OPT
# ======================================================================
#         Input Information
# ======================================================================
# Use Python's built-in Argument parser to get commandline options
parser = argparse.ArgumentParser()
parser.add_argument("--solver", help="solver to use: adflow or tripan",
                    type=str, default='adflow')
parser.add_argument("--mode", help="rans or euler. adflow solver only",
                   type=str, default='euler')
parser.add_argument("--output", help='Output directory', type=str,
                    default='./')
parser.add_argument("--shape", help='Use shape variables', type=int,
                    default=0)
parser.add_argument("--opt", help="optimizer to use", type=str, default='snopt')
parser.add_argument('--optOptions', type=str, help="Options for the optimizer.", default="{}")# Specify options \
#like this: --optOptions="{'name':value}"", default="{}"')
# parser.parse_args() must be called
args = parser.parse_args()
# This "executes" the optimization options to get a dictionary
exec('optOptions=%s'% args.optOptions)

outputDirectory = args.output
saveRepositoryInfo(outputDirectory)

triFile = '../INPUT/mdo_tutorial.tripan'
wakeFile = '../INPUT/mdo_tutorial.wake'
edgeFile = '../INPUT/mdo_tutorial.edge'
eulerFile = '../INPUT/euler_grid.cgns'
ransFile = '../INPUT/rans_grid_l2.cgns'
FFDFile = '../INPUT/mdo_tutorial_ffd.fmt'
bdfFile = '../INPUT/mdo_tutorial.bdf'
nTwist = 6
nGroup = 1
nProcPerGroup = 4

loadFactor = 2.5
KSWeight = 80.0
M_ref = (121000/2.20/2)*9.81 # 121,000 lb MTOW  -> half wing N
BETA = 2.0

# Set Processor group sizes
npStruct = 1
npAero = MPI.COMM_WORLD.size - npStruct

# Setup cruise aeroProblems
mach = [.78, 0.80, 0.82]
cruiseProblems = [] # List of cruise AeroStruct problem objects
nCruiseCases = 1 # Override the number to use
CRUISE_LIFT_STAR = {} # The target phsyical lift 

for j in xrange(nCruiseCases):
    ap = AeroProblem(name='cruise%d'%j, mach=mach[j], altitude=10000,
                     areaRef=45.5, alpha=2.0, chordRef=3.25,
                     evalFuncs=['lift', 'drag'])
    ap.addDV('alpha', lower=0, upper=10.0, scale=0.1)
    sp = StructProblem(ap.name, evalFuncs=['mass'])
    cruiseProblems.append(AeroStructProblem(ap, sp))
    CRUISE_LIFT_STAR[ap.name] = M_ref

# Setup maneuver aeroProblems
mach = [.78]
maneuverProblems = [] # List of maneuver AeroStruct problem objects
nManeuverCases = 1 # Override number to use
MANEUVER_LIFT_STAR = {} # The target physical lift constraint vals
for j in xrange(nManeuverCases):
    ap = AeroProblem(name='maneuver%d'%j, mach=mach[j], altitude=5000,
                     areaRef=45.5, alpha=2.0, chordRef=3.25,
                     evalFuncs=['lift'])
    ap.addDV('alpha', lower=0, upper=10.0, scale=0.1)
    sp = StructProblem(ap.name, evalFuncs=['ks0', 'ks1', 'ks2'])
    maneuverProblems.append(AeroStructProblem(ap, sp))
    MANEUVER_LIFT_STAR[ap.name] = M_ref*2.5

# Set all the Solver options here:
structOptions = {
    'transferDirection':[0, 0, 1]}

mdOptions = {
    # Tolerances
    'relTol':1e-5,
    'adjointRelTol':1e-5,
    
    # Output Options
    'outputDir':args.output,
    'saveIterations':True,
      
    # Solution Options
    'damp0':.5,
    'nMDIter':25,
    'MDSolver':'GS',
    'MDSubSpaceSize':40,

    # Adjoint optoins
    'adjointSolver':'KSP',
   
    # Monitor Options
    'monitorVars':['cl', 'cd', 'lift', 'norm_u', 'damp'],
    }

transferOptions = {}

if args.solver == 'tripan':
    AEROSOLVER = TRIPAN
    aeroOptions = {'outputDirectory':args.output,
                   'writeSolution':True,
                   'dragMethod':'total',
                   'useSymmetry':True,
                   'nWakeCells':1,
                   'printIterations':False,
                   'numberSolutions':True,
                   'wakeLength':455.0,
                   'tripanFile':triFile,
                   'wakeFile':wakeFile,
                   'edgeFileList':[edgeFile]}
else:
    AEROSOLVER = ADFLOW
    if args.mode == 'euler':
        gridFile = eulerFile
        CFL=1.2
        MGCYCLE = '3w'
        MGSTART = -1
        useNK = True
    else:
        gridFile = ransFile
        CFL=3.0
        MGCYCLE = '2w'
        MGSTART = 1
        useNK = False
       
    aeroOptions = {
        # Common Parameters
        'gridFile':gridFile,
        'outputDirectory':args.output,

        # Physics Parameters
        'equationType':args.mode,

        # Common Parameters
        'CFL':CFL,
        'CFLCoarse':CFL,
        'MGCycle':MGCYCLE,
        'MGStartLevel':MGSTART,
        'nCyclesCoarse':250,
        'nCycles':50,
        'monitorvariables':['resrho','cl','cd'],
        'nsubiterturb':3,
        'printTiming':False,
        'printIterations':False,

        # Convergence Parameters
        'L2Convergence':1e-12,
        'L2ConvergenceCoarse':1e-2,
        'L2ConvergenceRel':1e-1,
        'useNKSolver':useNK,

        # Adjoint Parameters
        'setMonitor':False,
        'applyadjointpcsubspacesize':15,
        'adjointL2Convergence':1e-8,
        'ADPC':True,
        'adjointMaxIter': 500,
        'adjointSubspaceSize':150, 
        'ILUFill':2,
        'ASMOverlap':1,
        'outerPreconIts':3,
        }

    meshOptions = {
        'gridFile':gridFile,
        'warpType':'algebraic',
        }

#  Create multipoint communication object
MP = multiPointSparse(MPI.COMM_WORLD)
MP.addProcessorSet('combined', nMembers=nGroup, memberSizes=nProcPerGroup)
gcomm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()

# Create aero/structural comms from the 'gcomm' returned from the MP
# object. The 'flags' is used to determine which processor we are
# on. flags[aeroID] will be true on a aero proc, and flags[structID]
# will be true on a structure process. 
comm, flags = createGroups([npStruct, npAero], comm=gcomm)
aeroID = 1
structID = 0

# Setup Geometry
execfile('../common_files/setup_geometry.py')

# Create discipline solvers
if flags[aeroID]:
    CFDSolver = AEROSOLVER(options=aeroOptions, comm=comm)
    CFDSolver.setDVGeo(DVGeo)

    if args.solver == 'adflow':
        mesh = MBMesh(options=meshOptions, comm=comm)
        CFDSolver.setMesh(mesh)
    FEASolver = None
    
elif flags[structID]:
    execfile('../common_files/setup_structure.py')
    FEASolver.setDVGeo(DVGeo)
    CFDSolver = None

# Setup Constraints
if flags[aeroID]:
    execfile('../common_files/setup_constraints.py')

# Create the final aerostructural solver
transfer = TACSLDTransfer(CFDSolver, FEASolver, gcomm, options=transferOptions)
AS = AeroStruct(CFDSolver, FEASolver,transfer, gcomm, options=mdOptions)

def cruiseObj(x):
    funcs = {}
    DVGeo.setDesignVars(x)
    if flags[aeroID]:
        DVCon.evalFunctions(funcs)
    if flags[structID]:
        FEASolver.setDesignVars(x)
    for i in range(nCruiseCases):
        if i%nGroup == ptID:
            cruiseProblems[i].setDesignVars(x)
            AS(cruiseProblems[i])
            AS.evalFunctions(cruiseProblems[i], funcs)
            AS.checkSolutionFailure(cruiseProblems[i], funcs)
    if MPI.COMM_WORLD.rank == 0:
        print x, funcs
    return funcs

def cruiseSens(x, funcs):
    funcsSens = {}
    for i in range(nCruiseCases):
        if i%nGroup == ptID:
            AS.evalFunctionsSens(cruiseProblems[i], funcsSens)
    if flags[aeroID]:
        DVCon.evalFunctionsSens(funcsSens)
    return funcsSens

def maneuverObj(x):
    funcs = {}
    for i in range(nManeuverCases):
        if i%nGroup == ptID:
            maneuverProblems[i].setDesignVars(x)
            AS(maneuverProblems[i])
            AS.evalFunctions(maneuverProblems[i], funcs)
            AS.checkSolutionFailure(maneuverProblems[i], funcs)
    if MPI.COMM_WORLD.rank == 0:
        print funcs

    return funcs

def maneuverSens(x, funcs):
    funcsSens = {}
    for i in range(nManeuverCases):
        if i%nGroup == ptID:
            AS.evalFunctionsSens(maneuverProblems[i], funcsSens)
    return funcsSens

def objCon(funcs):
    # Assemble the uniformly weighted objective
    funcs['obj'] = 0.0
    for asp in cruiseProblems:
        funcs['obj'] += (funcs[asp['drag']] * BETA + funcs['cruise0_mass']*2)/nCruiseCases
        funcs['cruise_lift_con_'+asp.name] = funcs[asp['lift']] - CRUISE_LIFT_STAR[asp.name]
    for asp in maneuverProblems:
        funcs['maneuver_lift_con_'+asp.name] = funcs[asp['lift']] - MANEUVER_LIFT_STAR[asp.name]
    if MPI.COMM_WORLD.rank == 0:
        print funcs
    return funcs

# Setup Optimization Problem
optProb = Optimization('Basic Aero-Structural Optimization', MP.obj)

# ---------- Design Variables/Constraints ------------
DVGeo.addVariablesPyOpt(optProb)
if flags[structID]:
    FEASolver.addVariablesPyOpt(optProb)

if flags[aeroID]:
    DVCon.addConstraintsPyOpt(optProb)

for asp in cruiseProblems:
    asp.addVariablesPyOpt(optProb)
    optProb.addCon('cruise_lift_con_'+asp.name, lower=0.0, upper=0.0,
                   scale=1.0/M_ref)

for asp in maneuverProblems:
    asp.addVariablesPyOpt(optProb)
    optProb.addCon('maneuver_lift_con_'+asp.name, lower=0.0, upper=0.0,
                   scale=1.0/M_ref)
    for j in xrange(3):
        optProb.addCon('%s_ks%d'% (asp.name, j), upper=1.0)

# Objective:
optProb.addObj('obj')

# The MP object needs the 'obj' and 'sens' function for each proc set,
# the optimization problem and what the objcon function is:
MP.addProcSetObjFunc('combined', cruiseObj)
MP.addProcSetSensFunc('combined',cruiseSens)
MP.addProcSetObjFunc('combined', maneuverObj)
MP.addProcSetSensFunc('combined',maneuverSens)
MP.setObjCon(objCon)
MP.setOptProb(optProb)

# Create optimizer
opt = OPT(args.opt, options=optOptions)

# Load the optimized structural variables
#optProb.setDVsFromHistory('struct.hst')

# Print Optimization Problem and sparsity
if MPI.COMM_WORLD.rank == 0:
    print optProb
optProb.printSparsity()

# Run Optimization
histFile = os.path.join(outputDirectory, 'opt_hist')
opt(optProb, MP.sens, storeHistory=histFile)
