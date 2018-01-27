
.. centered::
    :ref:`opt_struct` | :ref:`opt_aerostruct`

.. _opt_struct:

***********************
Structural Optimization
***********************
Content
=======

Preliminary
===========
In order to solve a structural optimization problem you need to make a copy of all the input files from TUTORIAL/STRUC/TACS into TUTORIAL/OPTIM/OPT_STRUC (if you haven't created the directory before, now it's the time to make it). Then rename "Struct_run.py" into "opt_Struct_run.py" and complete the file by following the tutorial.

Input file
==========
Libraries
---------
First, you need to had argparse and pyoptsparse libraries to the file and define the MPI parameter: "comm=MPI.COMM_WORLD"
::
	import argparse
	from pyoptsparse import *

	comm=MPI.COMM_WORLD

**Then delete the code lines after "execfile(Setup_structure)" and add the code from the next sections by following the rest of the tutorial.**

Objective function
------------------
The main inputs for solving a structural optimization problem is quite similar to the aerodynamic problem. To define the objective function and its sensibility, you need to set first the value of the design variable for the structural problem with a call to setDesignVars. Then the FEA solver is called in order to solve the new structural problem. Once the problem solved, the objective value is return.
::
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

Optimization problem
--------------------
The optimization problem we want to solve is a mass (lc0_mass) minimization problem with a ks failure constraints (failure if maximum value is egal or above 1). The optimization option are available `here <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/api/optimization.html>`_.
::
	optProb = Optimization('Mass min', obj)
	optProb.addObj('lc0_mass')
	FEASolver.addVariablesPyOpt(optProb)

	for i in range(numLoadCases):
    	for j in xrange(1):
        	optProb.addCon('%s_ks%d'% (SPs[i].name, j), upper=1.0)
	if comm.rank == 0:
    	print optProb
	optProb.printSparsity()

Now we define the optimizer solver and its options. You can take the same options that the ones used for the aerodynamic optimization problem.
::
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

	sol = opt(optProb, sens=sens, storeHistory='snopt_hist.hst')

	# Write the final solution
	FEASolver.writeOutputFile('final.f5')

Now you can perform the run of the opt_Struct_run.py file with the command (nProc= nGroup (= 1) x nProcPerGroup (= 4) = 4):
::
	$ mpirun -n nProc python opt_Struct_run.py

Post-processing
===============
For post-processing the optimization file a tool called pyOptview.py is available. Follow the instruction on the `post-processing documentation <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/postprocessing.html>`_.

.. centered::
    :ref:`opt_struct` | :ref:`opt_aerostruct`
