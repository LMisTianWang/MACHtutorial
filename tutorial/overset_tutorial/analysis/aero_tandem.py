from __future__ import print_function
from mpi4py import MPI
from baseclasses import AeroProblem
from adflow import ADFLOW

gridFile = 'overset_combined.cgns'

aeroOptions = {
    # I/O Parameters
    'gridFile':gridFile,
    'outputDirectory':'.',
    'monitorvariables':['resrho','cl','cd','cpu','resturb'],
    'writeTecplotSurfaceSolution':True,
    
    # Solver Parameters
    'MGCycle':'sg',

    # Physics Parameters
    'equationType':'RANS',

    # ANK Solver Parameters
    'useANKSolver':True,
    'ankswitchtol':1e5,
    'anksecondordswitchtol':1e-4,
    'ankcoupledswitchtol':1e-5,

    # NK Solver Parameters
    'useNKSolver':True,
    'nkswitchtol':1e-6,

    # Termination Criteria
    'L2Convergence':1e-6,
    'nCycles':10000,
    'usezippermesh':True
}

# Create solver
CFDSolver = ADFLOW(options=aeroOptions)

# save the lift distribution for the front wing
CFDSolver.addLiftDistribution(200, 'z', groupName='wing_front')
# save the lift distribution for the back wing
CFDSolver.addLiftDistribution(200, 'z', groupName='wing_back')
# save the total lift distribution
CFDSolver.addLiftDistribution(200, 'z')

ap = AeroProblem(name='fc', mach=0.3, altitude=1000, areaRef=0.64*0.24*2, alpha=3., chordRef=0.24, evalFuncs = ['cl', 'cd'])
CFDSolver(ap)

funcs = {}
CFDSolver.evalFunctions(ap, funcs)
# Print the evaluated functions
if MPI.COMM_WORLD.rank == 0:
    print(funcs)
