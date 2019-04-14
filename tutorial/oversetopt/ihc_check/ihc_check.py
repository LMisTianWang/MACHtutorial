#rst start
import numpy
import argparse
from baseclasses import *
from adflow import ADFLOW
from mpi4py import MPI
import shutil
import collections

# ======================================================================
#         Input Information
# ======================================================================
parser = argparse.ArgumentParser()
parser.add_argument('gridfile', type=str)
args = parser.parse_args()
outputDirectory = './'

# Common aerodynamic problem description and design variables
ap = AeroProblem(name='ihc_check', mach=0.3, altitude=1000, areaRef=0.24*0.64*2,
                chordRef=0.24)

# dictionary with name of the zone as a key and a factor to multiply it with.
oversetpriority = {}

aeroOptions = {
    # Common Parameters
    'gridFile':args.gridfile,
    'outputDirectory':outputDirectory,
    'mgcycle':'sg',
    'volumevariables':['blank'],
    'surfacevariables':['blank'],

    # Physics Parameters
    'equationType':'rans',

    # Debugging parameters
    'debugzipper':False,
    'usezippermesh':False,
    'nrefine':10, # number of times to run IHC cycle
    'nearwalldist':0.1,
    'oversetpriority':oversetpriority
}

# Create solver
CFDSolver = ADFLOW(options=aeroOptions, debug=False)

# Uncoment this if just want to check flooding
CFDSolver.setAeroProblem(ap)

name = '.'.join(args.gridfile.split('.')[0:-1])
CFDSolver.writeVolumeSolutionFile(name + '_IHC.cgns', writeGrid=True)
#rst end