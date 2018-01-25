# ======================================================================
#         Import modules
# ======================================================================
import os
import argparse
import numpy
from mpi4py import MPI
from baseclasses import *
from tacs import *
from adflow import *
from pywarp import *
from pygeo import *
from pyspline import *
from multipoint import *
from pyaerostructure import *
from repostate import *
# ======================================================================
#         Input Information
# ======================================================================
parser = argparse.ArgumentParser()
parser.add_argument("--output", help='Output directory', type=str,
                    default='./')
parser.add_argument("--shape", help='Use shape variables', type=int,
                    default=0)
args = parser.parse_args()
outputDirectory = args.output
saveRepositoryInfo(outputDirectory)

gridFile = 'wing_vol.cgns'
FFDFile = 'ffd.xyz'
bdfFile = 'wingbox.bdf'
gcomm = MPI.COMM_WORLD

# Set Processor group sizes
npStruct = 1
npAero = gcomm.size - npStruct

# Setup cruise aeroProblems
ap = AeroProblem(name='cruise', mach=0.78, altitude=10000,
                 areaRef=45.5, alpha=2.0, chordRef=3.25,
                 evalFuncs=['lift', 'drag'])
ap.addDV('alpha', lower=0, upper=10.0, scale=0.1)
sp = StructProblem(ap.name, evalFuncs=['mass'])
asp = AeroStructProblem(ap, sp)

# Setup all options
structOptions = {
    'transferDirection':[0, 0, 1]
}

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
    'nadjointiter':15,
    # Monitor Options
    'monitorVars':['cl', 'cd', 'lift', 'norm_u', 'damp'],
    }

aeroOptions = {
    # Common Parameters
    'gridFile':gridFile,
    'outputDirectory':args.output,

    # Physics Parameters
    'equationType':'rans',

    # Common Parameters
    'CFL':3.0,
    'CFLCoarse':3.0,
    'MGCycle':'2w',
    'MGStartLevel':1,
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
    'useNKSolver':True,

    # Adjoint Parameters
    'setMonitor':False,
    'applyadjointpcsubspacesize':10,
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

# Create aero/structural comms
comm, flags = createGroups([npStruct, npAero], comm=gcomm)
aeroID = 1
structID = 0

# Setup Geometry
execfile('INPUT/setup_geometry.py')

# Create discipline solvers
if flags[aeroID]:
    # Create solver
    CFDSolver = ADFLOW(options=aeroOptions, comm=comm)
    CFDSolver.setDVGeo(DVGeo)

    mesh = MBMesh(options=meshOptions, comm=comm)
    CFDSolver.setMesh(mesh)
    FEASolver = None

if flags[structID]:
    execfile('INPUT/setup_structure.py')
    FEASolver.setDVGeo(DVGeo)
    CFDSolver = None

# Setup Constraints
if flags[aeroID]:
    execfile('INPUT/setup_constraints.py')

# Create the final aerostructural solver
transferOptions = {}
transfer = TACSLDTransfer(CFDSolver, FEASolver, gcomm, options=transferOptions)
AS = AeroStruct(CFDSolver, FEASolver, transfer, gcomm, options=mdOptions)

# Solve each aero Problem
funcs = {}
AS(asp)
AS.evalFunctions(asp, funcs)
if gcomm.rank == 0:
    print funcs

# Also solve adjoints
funcsSens = {}
AS.evalFunctionsSens(asp, funcsSens)
if gcomm.rank == 0:
    print funcsSens
