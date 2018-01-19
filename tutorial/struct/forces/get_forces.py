# This is a template that should be used for setting up
# RANS analysis scripts

# ======================================================================
#         Import modules
# ======================================================================
import numpy
from mpi4py import MPI
from baseclasses import *
from sumb import SUMB
from pywarpustruct import USMesh
from pywarp import *
# ======================================================================
#         Input Information -- Modify accordingly!
# ======================================================================
outputDirectory = './'
gridFile = 'e170_L2.cgns'
alpha = 1.5 # deg
mach = 0.82
areaRef = 37.16 # m2 (semi-area because we use symmetry plane)
chordRef = 3.41 # m
bRef = 12.53
MGCycle = '2w'
altitude = 10000 # m
name = 'fc'
CLstar = 0.5
fixedCL = False

aeroOptions = {
    # Common Parameters
    'gridFile':gridFile,
    'outputDirectory':outputDirectory,
        
    # Physics Parameters
    'equationType':'RANS',
    'smoother':'dadi',
    
    # Common Parameters
    'CFL':1.5,
    'CFLCoarse':1.25,
    'MGCycle':MGCycle, 
    'MGStartLevel':-1,
    'nCyclesCoarse':25,
    'nCycles':1,
    'monitorvariables':['resrho','cl','cd'],
    'useNKSolver':True,

    # Convergence Parameters
    'L2Convergence':1e-6,
    'L2ConvergenceCoarse':1e-2,
    }




# Aerodynamic problem description
ap = AeroProblem(name=name, alpha=alpha, mach=mach, altitude=altitude,
                 areaRef=areaRef, chordRef=chordRef,
                 evalFuncs=['cl','cd'])

# Create solver
CFDSolver = SUMB(options=aeroOptions)

# Add slices and lift distributions
CFDSolver.addLiftDistribution(150, 'y')#, groupName='all')

slice_pos = numpy.array([0.1050, 0.1150, 0.1250, 0.1306,
                         0.2009, 0.2828, 0.3430, 0.3700,
                         0.3971, 0.5024, 0.6028, 0.7268,
                         0.8456, 0.9500, 0.9700, 0.9900])*bRef*0.5
CFDSolver.addSlices('y', slice_pos)
############################
##  SET UP FOR FORCE FILE ##
############################
# Structured Warping
meshOptions = {'gridFile':gridFile,
               'warpType':'algebraic',}
mesh = MBMesh(options=meshOptions)

# Add mesh warping object to CFD solver
CFDSolver.setMesh(mesh)
############################
##       END SET UP       ##
############################

 
# Solve and evaluate functions
funcs = {}

if fixedCL:
    # Use this for fixed CL
    CFDSolver.solveCL(aeroProblem=ap, CLStar=CLstar, alpha0=ap.alpha, \
                      delta=0.1, tol=0.0001, autoReset=False, \
                      CLalphaGuess=0.1449353937, maxIter=5, nReset = 250)
else:
    # Use this for fixed alpha
    CFDSolver(ap)
 
CFDSolver.evalFunctions(ap, funcs)
 



# Post-traitment
# Get the forces...these are the sumb forces:
forces = CFDSolver.getForces()
forces = MPI.COMM_WORLD.allreduce(numpy.sum(forces), MPI.SUM)
CFDSolver.writeForceFile('forces.txt')


###############################
###############################
#print funcs
if MPI.COMM_WORLD.rank == 0:
    print funcs 
 
