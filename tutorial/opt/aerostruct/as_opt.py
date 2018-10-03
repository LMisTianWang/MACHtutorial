# ==============================================================================
# Import modules
# ==============================================================================
from __future__ import print_function
import os
import argparse
import numpy
import sys
from pprint import pprint
from mpi4py import MPI
from baseclasses import *
from tacs import *
from adflow import ADFLOW
from pywarp import *
from pygeo import *
from pyspline import *
from multipoint import *
from pyaerostructure import *
from repostate import *
from pyoptsparse import Optimization, OPT
# ==============================================================================
# Input Information
# ==============================================================================
# Use Python's built-in Argument parser to get commandline options
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=str, default='.')
parser.add_argument("--shape", type=int, default=0)
parser.add_argument("--npcruise", type=int, default=2)
parser.add_argument("--npmaneuver", type=int, default=2)
args = parser.parse_args()

outputDirectory = args.output
saveRepositoryInfo(outputDirectory)
gridFile = 'wing_vol.cgns'

# ==============================================================================
# Aircraft Data
# ==============================================================================
TOW = 121000    # Aircraft takeoff weight in lbs
Mref = TOW / 2.20462 / 2 * 9.81   # half body mass in Newtons
Sref = 45.5     # half-wing in m^2
chordRef = 3.25 # meters

# ==============================================================================
# Processor allocation
# ==============================================================================
#  Create multipoint communication object
MP = multiPointSparse(MPI.COMM_WORLD)
MP.addProcessorSet('cruise', nMembers=1, memberSizes=args.npcruise)
MP.addProcessorSet('maneuver', nMembers=1, memberSizes=args.npmaneuver)
comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()
setName = MP.getSetName()
ptDirs = MP.createDirectories(args.output)

# Create a directory for all standard output
stdoutDir = os.path.join(args.output, 'stdout')
if MP.gcomm.rank == 0:
    os.system('mkdir -p %s'%stdoutDir)
MP.gcomm.barrier()
if comm.rank == 0:
    fName = os.path.join(stdoutDir, '%s_%d.out'%(setName, ptID))
    outFile = open(fName, 'w', buffering=0)
    redirectIO(outFile)

# ==============================================================================
# Set up case problems
# ==============================================================================
# Setup cruise problems
cruiseProblems = []
ap = AeroProblem(name='cruise', mach=0.8, altitude=10000, areaRef=Sref,
    alpha=2.0, chordRef=chordRef, evalFuncs=['lift', 'drag'])
ap.addDV('alpha', lower=0, upper=10.0, scale=0.1)
sp = StructProblem(ap.name, evalFuncs=['mass'])
cruiseProblems.append(AeroStructProblem(ap, sp))

# Setup maneuver problems
maneuverProblems = [] # List of maneuver AeroStruct problem objects
ap = AeroProblem(name='maneuver', mach=0.75, altitude=5000, areaRef=Sref,
    alpha=2.0, chordRef=chordRef, evalFuncs=['lift'])
ap.addDV('alpha', lower=0, upper=10.0, scale=0.1)
sp = StructProblem(ap.name, evalFuncs=['ks0', 'ks1', 'ks2'], loadFactor=2.5)
maneuverProblems.append(AeroStructProblem(ap, sp))

# ==============================================================================
# Geometric Design Variable Set-up
# ==============================================================================
execfile('INPUT/setup_geometry.py')

# ==============================================================================
# Set up aerodynamic analysis
# ==============================================================================
aeroOptions = {
    # I/O Parameters
    'gridFile':gridFile,
    'outputDirectory': ptDirs[setName][ptID],
    'monitorvariables':['resrho','cl','cd'],
    'setMonitor':False,
    'printTiming':False,
    'printIterations':False,
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
    'ankmaxiter':80,
    'anklinearsolvetol':0.05,
    'ankpcilufill':2,
    'ankasmoverlap':2,
    'ankcflexponent':0.5,

    # NK Solver Parameters
    'useNKSolver':True,
    'nkswitchtol':1e-4,

    # Termination Criteria
    'L2Convergence':1e-10,
    'L2ConvergenceCoarse':1e-2,
    'L2ConvergenceRel':1e-1,
    'nCycles':1000,

    # Adjoint Parameters
    'adjointL2Convergence':1e-6,
    'adjointMaxIter': 2000,
}

meshOptions = {
    'gridFile':gridFile,
    'warpType':'algebraic',
    }

# Create solver
CFDSolver = ADFLOW(options=aeroOptions, comm=comm)

# Set up mesh warping
mesh = MBMesh(options=meshOptions, comm=comm)
CFDSolver.setMesh(mesh)
CFDSolver.setDVGeo(DVGeo)

# ==============================================================================
# Set up structural analysis
# ==============================================================================
structOptions = {
    'gravityVector':[0, -9.81, 0],
    'projectVector':[0, 1, 0],     # normal to planform
}

# Set up TACS on the struct proc
FEASolver = pytacs.pyTACS('wingbox.bdf', comm=comm, options=structOptions)
FEASolver.setDVGeo(DVGeo)
execfile('INPUT/setup_structure.py')


# ==============================================================================
# Set up aerostructural analysis
# ==============================================================================
mdOptions = {
    # Tolerances
    'relTol':1e-5,
    'adjointRelTol':1e-5,

    # Output Options
    'outputDir':ptDirs[setName][ptID],
    'saveIterations':True,

    # Solution Options
    'damp0':.5,
    'nMDIter':25,
    'MDSolver':'GS',
    'MDSubSpaceSize':40,

    # Adjoint optoins
    'adjointSolver':'KSP',
    'nadjointiter':15,
    # Monitor Options
    'monitorVars':['cl', 'cd', 'lift', 'norm_u', 'damp'],
    }

transferOptions = {}

# Create transfer object
transfer = TACSLDTransfer(CFDSolver, FEASolver, comm, options=transferOptions)

# Create the final aerostructural solver
AS = AeroStruct(CFDSolver, FEASolver, transfer, comm, options=mdOptions)

# ==============================================================================
# DVConstraint Setup
# ==============================================================================
execfile('INPUT/setup_constraints.py')

# ==============================================================================
# Analysis and Sensitivity Functions
# ==============================================================================
def cruiseObj(x):
    if comm.rank == 0:
        print('Design Variables')
        pprint(x)
    funcs = {}
    DVGeo.setDesignVars(x)
    DVCon.evalFunctions(funcs)
    FEASolver.setDesignVars(x)
    cp = cruiseProblems[0]
    cp.setDesignVars(x)
    AS(cp)
    AS.evalFunctions(cp, funcs)
    AS.checkSolutionFailure(cp, funcs)
    if comm.rank == 0:
        print('Cruise functions')
        pprint(funcs)
    return funcs

def cruiseSens(x, funcs):
    funcsSens = {}
    cp = cruiseProblems[0]
    AS.evalFunctionsSens(cp, funcsSens)
    DVCon.evalFunctionsSens(funcsSens)
    return funcsSens

def maneuverObj(x):
    if comm.rank == 0:
        print('Design Variables')
        pprint(x)
    funcs = {}
    DVGeo.setDesignVars(x)
    FEASolver.setDesignVars(x)
    mp = maneuverProblems[0]
    mp.setDesignVars(x)
    AS(mp)
    AS.evalFunctions(mp, funcs)
    AS.checkSolutionFailure(mp, funcs)
    if comm.rank == 0:
        print('Maneuver functions')
        pprint(funcs)
    return funcs

def maneuverSens(x, funcs):
    funcsSens = {}
    mp = maneuverProblems[0]
    AS.evalFunctionsSens(mp, funcsSens)
    return funcsSens

def objCon(funcs, printOK):
    funcs['obj'] = funcs['cruise_drag'] + funcs['cruise_mass'] * 2
    funcs['cruise_lift_con'] = funcs['cruise_lift'] - Mref
    funcs['maneuver_lift_con'] = funcs['maneuver_lift'] - Mref * 2.5
    if printOK:
        pprint(funcs)
    return funcs

# ==============================================================================
# Optimization Problem Setup
# ==============================================================================
# Setup Optimization Problem
optProb = Optimization('Basic Aero-Structural Optimization', MP.obj)

# Add variables
DVGeo.addVariablesPyOpt(optProb)
FEASolver.addVariablesPyOpt(optProb)
cruiseProblems[0].addVariablesPyOpt(optProb)
maneuverProblems[0].addVariablesPyOpt(optProb)
geoVars = DVGeo.getValues().keys()

# Add constraints
DVCon.addConstraintsPyOpt(optProb)
FEASolver.addConstraintsPyOpt(optProb)
optProb.addCon('cruise_lift_con', lower=0.0, upper=0.0, scale=1.0/Mref,
    wrt=['struct', 'alpha_cruise'] + geoVars)
optProb.addCon('maneuver_lift_con', lower=0.0, upper=0.0, scale=1.0/Mref,
    wrt=['struct', 'alpha_maneuver'] + geoVars)
for j in xrange(3):
    optProb.addCon('maneuver_ks%d'%j, upper=1.0,
    wrt=['struct', 'alpha_maneuver'] + geoVars)

# Objective:
optProb.addObj('obj')

# The MP object needs the 'obj' and 'sens' function for each proc set,
# the optimization problem and what the objcon function is:
MP.addProcSetObjFunc('cruise', cruiseObj)
MP.addProcSetSensFunc('cruise',cruiseSens)
MP.addProcSetObjFunc('maneuver', maneuverObj)
MP.addProcSetSensFunc('maneuver',maneuverSens)
MP.setObjCon(objCon)
MP.setOptProb(optProb)

# ==============================================================================
# Run optimization
# ==============================================================================
# Create optimizer
optOptions = {
    'Function precision':1e-4,
    'Major feasibility tolerance':1.0e-4,
    'Major optimality tolerance':1.0e-4,
    'Difference interval':1e-3,
    'Print file':os.path.join(outputDirectory, 'SNOPT_print.out'),
    'Summary file':os.path.join(outputDirectory, 'SNOPT_summary.out'),
}
opt = OPT('snopt', options=optOptions)

# Load the optimized structural variables
optProb.setDVsFromHistory('struct.hst')

# Print Optimization Problem and sparsity
if comm.rank == 0:
    print(optProb)
optProb.printSparsity()

# Run Optimization
histFile = os.path.join(outputDirectory, 'opt_hist.hst')
MP.gcomm.barrier()
sol = opt(optProb, MP.sens, storeHistory=histFile)
if comm.rank == 0:
   print(sol)