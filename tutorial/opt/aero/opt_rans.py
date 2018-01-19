#1. IMPORT MODULES
#==============================
from mpi4py import MPI
from multipoint import *
import numpy
from baseclasses import *
from pyspline import *
from repostate import *
from pygeo import *
from pywarpustruct import USMesh
from pywarp import *
from adflow import ADFLOW
from pyoptsparse import Optimization, OPT


# Ignore deprecation warnings
import warnings
warnings.filterwarnings("ignore")



#2. MULTIPOINT
#==============================
nGroup = 1
nProcPerGroup = 3
MP = multiPointSparse(MPI.COMM_WORLD)
MP.addProcessorSet('cruise', nMembers=nGroup, memberSizes=nProcPerGroup)
comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()



#3. RANS CONDITIONS AND PROBLEM DEFINITION
#==============================
#ADFLOW
outputDirectory = './output.d/'
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
'CFL':0.5,
'CFLCoarse':0.05,
'MGCycle':MGCycle,
'MGStartLevel':-1,
'nCyclesCoarse':250,
'nCycles':100,
'monitorvariables':['resrho','cl','cd'],
'useNKSolver':False,

# Convergence Parameters
'L2Convergence':1e-6,
'L2ConvergenceCoarse':1e-2,
#Convergence Parameters: 
'adjointL2Convergence':1e-10
}

# Aerodynamic problem description
CFDSolver = ADFLOW(options=aeroOptions, comm=MPI.COMM_WORLD)
CFDSolver.addLiftDistribution(200, 'z')

#4. AERODYNAMIC DESIGN VARIABLES
#==============================
ap = AeroProblem(name=name, alpha=alpha, mach=mach, altitude=altitude, areaRef=areaRef, chordRef=chordRef, evalFuncs=['cl','cd'])
ap.addDV('alpha', value=1.5, lower=0., upper=10.0, scale=1.0)

#5. FFD
#==============================
# ffd deformation
FFDFile = 'ffd.fmt'
DVGeo = DVGeometry(FFDFile)

x = [0.0+5.41/4.0 , 6.24+1.29/4.0]
y = [0.0     , 1.16]
z = [-1.0E-03, 12.6]

nTwist = 5
tmp = pySpline.Curve(x=x, y=y, z=z, k=2)
X = tmp(numpy.linspace(0, 1, nTwist+1))
c1 = pySpline.Curve(X=X, k=2)
DVGeo.addRefAxis('wing', c1)

def twist(val, geo):
        for i in xrange(nTwist):
                geo.rot_z['wing'].coef[i+1] = val[i]

DVGeo.addGeoDVGlobal('twist', 0*numpy.ones(nTwist), twist,lower=-50, upper=50, scale=0.2)

dvDict = DVGeo.getValues()
dvDict['twist'] = numpy.linspace(0, 50, nTwist)
DVGeo.setDesignVars(dvDict)

CFDSolver.setDVGeo(DVGeo)
meshOptions = {'gridFile':gridFile,'warpType':'algebraic',}
mesh = MBMesh(options=meshOptions, comm=MPI.COMM_WORLD)
CFDSolver.setMesh(mesh)

#6. Geometric and aerodynamic functions
#==============================
def cruiseFuncs(x):
        if MPI.COMM_WORLD.rank == 0:
                print x
        funcs = {}
        DVGeo.setDesignVars(x)
        ap.setDesignVars(x)
        CFDSolver(ap)
        CFDSolver.evalFunctions(ap, funcs)
        if MPI.COMM_WORLD.rank == 0:
                print funcs
        return funcs

def cruiseFuncsSens(x, funcs):
        funcsSens = {}
        CFDSolver.evalFunctionsSens(ap, funcsSens)
        if MPI.COMM_WORLD.rank == 0:
                print funcsSens
        return funcsSens

#7. Optimization problem set-up
#==============================
CLstar = 0.5
def objCon(funcs, printOK):
        funcs['obj'] = 0.0
        funcs['obj'] += funcs[ap['cd']]
        funcs['cl_con_'+ap.name] = funcs[ap['cl']] - CLstar
        if printOK:
                print 'funcs in obj:', funcs
        return funcs

optProb = Optimization('opt', MP.obj, comm=MPI.COMM_WORLD)
ap.addVariablesPyOpt(optProb)
DVGeo.addVariablesPyOpt(optProb)

optProb.addObj('obj', scale=1e4)
optProb.addCon('cl_con_'+ap.name, lower=0.0, upper=0.0, scale=1.0)

MP.setProcSetObjFunc('cruise', cruiseFuncs)
MP.setProcSetSensFunc('cruise', cruiseFuncsSens)
MP.setObjCon(objCon)
MP.setOptProb(optProb)

optProb.printSparsity()

outputDirectory = './output.d/'
optOptions = {'Major iterations limit':100,
          'Minor iterations limit':1500000000,
          'Iterations limit':1000000000,
          'Major step limit':2.0,
          'Major feasibility tolerance':1.0e-6,
          'Major optimality tolerance':1.0e-6,
          'Minor feasibility tolerance':1.0e-6,
          'Print file': outputDirectory + 'SNOPT_print.out',
          'Summary file': outputDirectory + 'SNOPT_summary.out'}

opt = OPT('snopt', options=optOptions)

histFile ='./output.d/snopt_hist.hst'
sol = opt(optProb, MP.sens, storeHistory=histFile)
if MPI.COMM_WORLD.rank == 0:
        print sol




