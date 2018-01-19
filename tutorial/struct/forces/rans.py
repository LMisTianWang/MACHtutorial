# This is a template that should be used for setting up
# RANS analysis scripts

# ======================================================================
#         Import modules
# ======================================================================
import numpy
from mpi4py import MPI
from baseclasses import *
from adflow import ADFLOW

# ======================================================================
#         Input Information -- Modify accordingly!
# ======================================================================
outputDirectory = './output.d'
gridFile = 'wing_mvol2.cgns'
alpha = 1.5
mach = 0.82
bRef =12.53
areaRef = 37.1982321487
chordRef = 2.96
MGCycle = '2w'
altitude = 10000
name = 'fc'

aeroOptions = {
# Common Parameters
'gridFile':gridFile,
'outputDirectory':outputDirectory,

# Physics Parameters
'equationType':'RANS',
'smoother':'dadi',

# Common Parameters
'CFL':5.0,
'CFLCoarse':1.25,
'MGCycle':MGCycle,
'MGStartLevel':-1,
'nCyclesCoarse':250,
'nCycles':100000,
'monitorvariables':['resrho','cl','cd'],
'useNKSolver':False,

# Convergence Parameters
'L2Convergence':1e-6,
'L2ConvergenceCoarse':1e-2,
}


# Aerodynamic problem description
ap = AeroProblem(name=name, alpha=alpha, mach=mach, altitude=altitude, areaRef=areaRef, chordRef=chordRef,evalFuncs=['cl','cd'])

# Create solver
CFDSolver = ADFLOW(options=aeroOptions)
CFDSolver.addLiftDistribution(150, 'y')
# Solve and evaluate functions
funcs = {}
CFDSolver(ap)
CFDSolver.evalFunctions(ap, funcs)


# Print the evaluatd functions
if MPI.COMM_WORLD.rank == 0:
    print funcs
