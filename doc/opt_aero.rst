
.. centered::
    :ref:`opt_ffd` | :ref:`opt_struct`

.. _opt_aero:

************************
Aerodynamic Optimization
************************

Content
=======
In this chapter, we explain how to create the input files to solve a basic optimization problem: minimisation of the drag with a lift constraint. The aerodynamic variable is the angle of incidence and the geometric design variable is the twist.

* :ref:`Import modules <OPTIM_AERO_Import>`
* :ref:`Multipoint object <OPTIM_AERO_MCO>`
* :ref:`RANS <OPTIM_AERO_RANS>`
* :ref:`Aerodynamic design variables <OPTIM_AERO_ADV>`
* :ref:`FFD <OPTIM_AERO_FFD>`
* :ref:`Geometric and aerodynamic functions <OPTIM_AERO_GAF>`
* :ref:`Optimization problem set-up <OPTIM_AERO_OPSU>`
* :ref:`Post-processing <OPTIM_AERO_PP>`

.. _OPTIM_AERO_Import:

Import modules
==============
Edit a new file called opt_rans.py inside TUTORIAL/OPTIM/OPT_AERO and import the library necessary for parallel computing, basic environment manipulation and operation, geometry generation and mesh deformation, RANS simulation, and optimization.
::
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

.. _OPTIM_AERO_MCO:

Multipoint communication object
===============================
The MultiPoint library is made to facilitate optimization problems with different computations and all occurring in parallel. It hides the required MPI communication from the user and makes the python files more readable. Functions and class descriptions are available on the `reference page <http://mdolab.engin.umich.edu/doc/packages/multipoint/doc/reference.html>`_ and there is also this `tutorial <http://mdolab.engin.umich.edu/doc/packages/multipoint/doc/tutorial.html>`_ with an example. Here we use one group with only 4 processors as we run it on the personal computer.
::
	nGroup = 1
	nProcPerGroup = 4
	MP = multiPointSparse(MPI.COMM_WORLD)
	MP.addProcessorSet('cruise', nMembers=nGroup, memberSizes=nProcPerGroup)
	comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()

.. _OPTIM_AERO_RANS:

RANS conditions and problem definition
======================================
In this section, we define the RANS parameters. This section is similar to the one already explain in :ref:`Aerodynamic analysis: ADflow <ADFLOW>` for rans.py; for the aeroOptions list the only change is the add of the convergence parameter for the adjoint (don't forget to define an output directory, Mach number, altitude,...). Adding the adjoint convergence parameters is to ensure the good convergence of the adjoint matrix used as a sensibility parameter by the optimizer. Use the aeroOptions function defined in :ref:`Aerodynamic analysis: ADflow <ADFLOW>` and add the adjoint parameters. Then define the solver. Like in :ref:`Aerodynamic analysis: ADflow <ADFLOW>` we ask for a 200 spanwise lift section distribution output.
::
	gridFile = 'wing_mvol2.cgns'
	#Modify the aeroOptions of :ref:`Aerodynamic analysis: ADflow <ADFLOW>`.
	#Common Parameters:
	#Physics Parameters,
	#Common Parameters,
	#Add the section: #Convergence Parameters: 'adjointL2Convergence':1e-10

	CFDSolver = ADFLOW(options=aeroOptions, comm=comm)
	CFDSolver.addLiftDistribution(200, 'z')

.. _OPTIM_AERO_ADV:

Aerodynamic design variables
============================
Aeroproblem is a class used for communicating/interacting with the CFDsolver. All the information relative to an aerodynamic problem are described inside and can be used by the optimizer as design variables. Here, we will see a case where the optimizer used:

* the angle of attack as a design variable.
* The cost function to minimize is dependant of cl (lift) & cd (drag) determined by the RANS solver ADflow.

The Aeroproblem function is explained on the `pyAero_problem documentation <http://mdolab.engin.umich.edu/doc/packages/baseclasses/doc/pyAero_problem.html>`_.
::
	ap = AeroProblem(name=name, alpha=alpha, mach=mach, altitude=altitude, areaRef=areaRef, chordRef=chordRef, evalFuncs=['cl','cd'])

the AeroProblem functions are defined in the application program interface (API) `documentation <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/api/optimization.html>`_. Here we define the angle of attack alpha as a design variable:
::
	ap.addDV('alpha', value=1.5, lower=0, upper=10.0, scale=1.0)

.. _OPTIM_AERO_FFD:

FFD
===
In this part, we define the geometric variables for the optimization problem. Here we are interested in a simple case of a twist deformation. In order to take into account the twist of the wing as a single design variable, it is required to define an axis. This axis will be used as a global design variable which will affect many control points (FFD, local design variables) of the geometry FFD. This part is similar to the one already explained in :ref:`FFD & FFD deformation <OPTIM_DEFORMATION_FFD>` (Don't forget to change the path of the FFDFile).
The mesh deformation performed in :ref:`FFD & FFD deformation <OPTIM_DEFORMATION_FFD>` is not made explicit here. The mesh wrapping is done internally by ADflow (CFDsolver). First, set the DVGeometry class inside the CFD solver in order to perform the geometric deformations. Then, define the mesh warping options and objects for a multi-block mesh and set the mesh inside the CFD solver. Descriptions of the mesh warping functions and class are available on `pywarp API documentation  <http://mdolab.engin.umich.edu/doc/packages/pywarp/doc/API.html>`_.
::
	CFDSolver.setDVGeo(DVGeo)
	meshOptions = {'gridFile':gridFile,'warpType':'algebraic',}
	mesh = MBMesh(options=meshOptions, comm=comm)
	CFDSolver.setMesh(mesh)

.. _OPTIM_AERO_GAF:

Geometric and aerodynamic functions
===================================
We specify the cruiseFuncs and its sensibility. Inside cruiseFuncs, the objective geometric and aerodynamic variables are defined with a call to setDesignVars(x). After the new CFD problem is solved, the function returns the aerodynamics values such as drag and lift.
::
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

.. _OPTIM_AERO_OPSU:

Optimization problem set-up
===========================
In order to solve an optimization problem, the pyOptSparse class is used. It is designed to solve general, constrained nonlinear optimization problems. An advance presentation of the class is available at the `pyoptsparse documentation guide <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/guide.html>`_. Here we define the cost function to minimize and its constraints. The objective function 'obj' is used to minimize the drag and constrain the lift to a value equal to CLstar as the angle of attack is a design variable (CLstar = 0.5). After defining the objCon object, the optimization problem is described with the respective class. It contains all information about the minimization problem to solve. Also, In order to add the aerodynamic design variables or geometric design variables addVariablesPyOpt function is used. It contains all information about the minimization problem to solve. Also, In order to add the aerodynamic design variables or geometric design variables addVariablesPyOpt function is used.
This function is described in the `optimization API documentation <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/api/optimization.html>`_.
::
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

Then we add the obj function and constraints to the optimization class.
::
	optProb.addObj('obj', scale=1e4)
	optProb.addCon('cl_con_'+ap.name, lower=0.0, upper=0.0, scale=1.0)

Before calling the MP multipoint object, the optimization problem needs to be fully declared. Only after that, you can set to the MP multipoint class, the objective functions, and optimization problem for each proc with.
::
	MP.setProcSetObjFunc('cruise', cruiseFuncs)
	MP.setProcSetSensFunc('cruise', cruiseFuncsSens)
	MP.setObjCon(objCon)
	MP.setOptProb(optProb)

	optProb.printSparsity()

PrintSparsity helps the user visualize what pyOptSparse has been given and ensure it is what the user expected. In order to verify that the optimization problem is set up correctly, you should always make a call to this function.
Information for the function are available `here <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/api/optimization.html>`_.

To solve the optimization problem the SNOPT optimizer is selected. SNOPT is a sparse nonlinear optimizer that is useful for solving constrained problems with smooth objective functions and constraints. A description of the different optimizer available are given in `the optimizer API documentation <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/api/optimizer.html>`_ .
::
	outputDirectory = './output_files.d/'
	optOptions = {
		'Major iterations limit':100,
		'Minor iterations limit':1500000000,
		'Iterations limit':1000000000,
		'Major step limit':2.0,
		'Major feasibility tolerance':1.0e-6,
		'Major optimality tolerance':1.0e-6,
		'Minor feasibility tolerance':1.0e-6,
		'Print file': outputDirectory + 'SNOPT_print.out',
		'Summary file': outputDirectory + 'SNOPT_summary.out'
		}

	opt = OPT('snopt', options=optOptions)

	histFile = outputDirectory + 'snopt_hist.hst'
	sol = opt(optProb, MP.sens, storeHistory=histFile)
	if MPI.COMM_WORLD.rank == 0:
		print sol

Now you can perform the run of the opt_rans.py file with the command (nProc= nGroup (= 1) x nProcPerGroup (= 4) = 4):
::
	$ mpirun -n nProc python opt_rans.py

.. _OPTIM_AERO_PP:

Post-processing
===============
For post-processing the optimization file a tool called pyOptview.py is available. Follow the instruction on the `post-processing documentation <http://mdolab.engin.umich.edu/doc/packages/pyoptsparse/doc/postprocessing.html>`_.

.. centered::
    :ref:`opt_ffd` | :ref:`opt_struct`
