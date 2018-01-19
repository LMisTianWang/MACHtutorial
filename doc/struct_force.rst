
.. centered::  
   :ref:`Previous: step 2 <Struct_step2>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 3 <Struct_step3>`

.. _FORCE:

**********
Force file
**********

Content
=======
Each structural problem is based on a specific load case. In order to obtain the load (a force file: X, Y,Z, Fx, Fy, Fz) for a structural geometry an aerodynamic problem need to be solved (RANS computation) on the  case studied. In the ADflow input file extract describes here,  we suppose that the aerodynamic problem is already solved and we only want to create a force file.

Preliminary
===========
Copy from TUTORIAL/AERO/ADFLOW into the TUTORIAL/STRUC/FORCE directory the next files:

* rans.py
* wing_mvol2.cgns (volume mesh)
* fc_000_vol.cgns (solution)

Rename rans.py into rans_force.py.

How to create a force/load file
===============================
In order to write your force.txt you need to import a few complementary modules and mpi parameter in your ADFlow input file (rans_force.py) if they are not already called:
::
	from pywarpustruct import USMesh 
	from pywarp import * 
	comm=MPI.COMM_WORLD

Once these modules imported, choose between loading a previous solution if there is one, or solve a new CFD problem. In the first case, you only want to write a force.txt based on the existing solution. In order to restart from a previous solution, add these options in aeroOptions (**dont forget to put "nCycles"=0 in aeroOptions, otherwise you will run a full RANS simulation**):
::
	# Restart parameters from a previous volume solution: 
	'restartFile':'fc_000_vol.cgns', 
	'solRestart':True, 

After the “Aerodynamic problem description” and ”Create solver” sections, call the “Structured Warping” functions if they are not already in the input file:
::
	meshOptions = {'gridFile':gridFile, 'warpType':'algebraic',} 	
	mesh = MBMesh(options=meshOptions, comm=comm) 

The MultiBlockMesh (MBMesh) module is used for interacting with a structured multi-block mesh typically used in a 3D CFD program. Then add the mesh warping object to the CFD solver:
::
	CFDSolver.setMesh(mesh) 

After solving the CFD problem (call of CFDSolver), write the force.txt by adding to file: 
::
	CFDSolver.writeForceFile('forces.txt') 

“writeForceFile” collects all the forces and locations and writes them to a file. This file can now be used for setting a structural load problem. 
The force.txt is defined such as:

+-------------+-------------+
|Num. of nodes|Num. of cells| 
+=============+=============+
| Nodes       | Force       |
+-------------+-------------+
| X1 Y1 Z1    | Fx1 Fy1 Fz1 |
+-------------+-------------+
| Xn Yn Zn    | Fxn Fyn Fzn |
+-------------+-------------+
| Connectivity information  |
+-------------+-------------+



.. centered::  
   :ref:`Previous: step 2 <Struct_step2>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 3 <Struct_step3>`


