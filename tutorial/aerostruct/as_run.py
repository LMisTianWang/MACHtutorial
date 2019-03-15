# ==============================================================================
#         Import modules
# ==============================================================================
from __future__ import print_function
import numpy
from mpi4py import MPI
from baseclasses import *
from tacs_orig import *
from adflow import *
from pywarp import *
from multipoint import *
from pyaerostructure import *
from repostate import *
saveRepositoryInfo()

gridFile = 'wing_vol.cgns'
gcomm = MPI.COMM_WORLD

# Set 1 processor for TACS, the rest go to ADflow
npStruct = 1
npAero = gcomm.size - npStruct

# Create aero/structural comms
comm, flags = createGroups([npStruct, npAero], comm=gcomm)
structID = 0    # zeroth group is structure
aeroID = 1      # first group is aero
# ==============================================================================
#         Set up case problems
# ==============================================================================
# Set up aerodynamic problem
ap = AeroProblem(name='cruise', mach=0.8, altitude=10000,
                 areaRef=45.5, alpha=2.0, chordRef=3.25,
                 evalFuncs=['lift', 'drag'])

# Set up structural problem
sp = StructProblem(ap.name, evalFuncs=['mass'])

# Create aerostructural problem
asp = AeroStructProblem(ap, sp)

# ==============================================================================
#         Set up aerodynamic analysis
# ==============================================================================
aeroOptions = {
    # I/O Parameters
    'gridFile':gridFile,
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

# Set up ADFLOW on the aero procs
if flags[aeroID]:
    # Create solver
    CFDSolver = ADFLOW(options=aeroOptions, comm=comm)

    # Set up mesh warping
    mesh = MBMesh(options=meshOptions, comm=comm)
    CFDSolver.setMesh(mesh)

    # Do not set up TACS on these procs
    FEASolver = None

# ==============================================================================
#         Set up structural analysis
# ==============================================================================
structOptions = {
    'gravityVector':[0, -9.81, 0],
    'projectVector':[0, 1, 0],     # normal to planform
}

# Set up TACS on the struct proc
if flags[structID]:
    FEASolver = pytacs.pyTACS('wingbox.bdf', comm=comm, options=structOptions)
    execfile('setup_structure.py')
    CFDSolver = None

# ==============================================================================
#         Set up aerostructural analysis
# ==============================================================================
mdOptions = {
    # Tolerances
    'relTol':1e-5,
    'adjointRelTol':1e-5,

    # Output Options
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
transfer = TACSLDTransfer(CFDSolver, FEASolver, gcomm, options=transferOptions)

# Create the final aerostructural solver
AS = AeroStruct(CFDSolver, FEASolver, transfer, gcomm, options=mdOptions)

# ==============================================================================
#         Solve!
# ==============================================================================
# Solve the aerostructural problem
funcs = {}
AS(asp)
AS.evalFunctions(asp, funcs)
if gcomm.rank == 0:
    print(funcs)

# Also solve adjoints
funcsSens = {}
AS.evalFunctionsSens(asp, funcsSens)
if gcomm.rank == 0:
    print(funcsSens)
