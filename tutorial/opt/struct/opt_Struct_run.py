

import numpy
from mpi4py import MPI
from baseclasses import *
from tacs import *
from repostate import *
import argparse
from pyoptsparse import *
Setup_structure = 'Setup_structure.py'
outputDirectory =  './output_files.d/'
comm=MPI.COMM_WORLD

SPs = [StructProblem('lc0', loadFile='forces.txt',evalFuncs=['mass','ks0'])]
numLoadCases = len(SPs)

execfile(Setup_structure)

def obj(x):
	'''Evaluate the objective and constraints'''
	funcs = {}
	FEASolver.setDesignVars(x)
	for i in range(numLoadCases):
		FEASolver(SPs[i])
		FEASolver.evalFunctions(SPs[i], funcs)
	if comm.rank == 0:
		print funcs
	return funcs, False

def sens(x, funcs):
	funcsSens = {}
	for i in range(numLoadCases):
		FEASolver.evalFunctionsSens(SPs[i], funcsSens)
	return funcsSens, False

optProb = Optimization('Mass min', obj)
optProb.addObj('lc0_mass')
FEASolver.addVariablesPyOpt(optProb)

for i in range(numLoadCases):
	for j in xrange(1):
		optProb.addCon('%s_ks%d'% (SPs[i].name, j), upper=1.0)

if comm.rank == 0:
	print optProb
optProb.printSparsity()


optOptions = {'Major iterations limit':100,
        'Minor iterations limit':1500000000,
        'Iterations limit':1000000000,
        'Major step limit':2.0,
        'Major feasibility tolerance':1.0e-6,
        'Major optimality tolerance':1.0e-6,
        'Minor feasibility tolerance':1.0e-6,
        'Print file':'SNOPT_print.out',
        'Summary file':'SNOPT_summary.out'}

opt = OPT('snopt', options=optOptions)

'snopt_hist.hst'
sol = opt(optProb, sens=sens, storeHistory='snopt_hist.hst')


# Write the final solution
FEASolver.writeOutputFile('output.f5')

