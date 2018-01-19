import numpy
from mpi4py import MPI
from baseclasses import *
from tacs import *
from repostate import *

Setup_structure = 'Setup_structure.py'
outputDirectory =  './output_files.d/'

SPs = [StructProblem('lc0', loadFile='forces.txt',evalFuncs=['mass','ks0'])]
numLoadCases = len(SPs)

F = numpy.array([0.0, 3E5, 0.0])
pt = numpy.array([8.0208, -0.0885, 14.000])

execfile(Setup_structure)

funcs = {}
for i in range(numLoadCases):
	FEASolver(SPs[i])
	FEASolver.evalFunctions(SPs[i], funcs)

FEASolver.writeOutputFile(outputDirectory+'output.f5')
