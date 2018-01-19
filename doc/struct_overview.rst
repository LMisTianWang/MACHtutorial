
.. centered::
   :ref:`Previous: ADflow <ADFLOW>` | :ref:`Summary <SUMMARY>`

.. _Struct:

###########################
Part 2: Structural Analysis
###########################

*A Structure is a system of connected parts used to support a load as seen on the left side of Figure 1. Structural analysis is the determination of the effects of loads on the physical structure and its components. TTo evaluate the effects of loads on the wing structure you need to solve for each node of a structural mesh the structural problem (Figure 1 right side). By using TACS (Toolkit Analysis for Composite Structures) based on a finite element analysis solver, we will be able to simulate the shell strains, stress, failure, and buckling constraints.*

.. figure:: Pic/Struc/Process/img_p1.png
   :align: center

   **Figure 1: structural analysis problem**

TACS is a Toolkit for Analysis of Composite Structures written in C++. This tutorial will help you use pyTACS the python interface of TACS. This toolkit is based on a parallelized FEA Solver:
    * Solution types: linear static, Nonlinear static, Buckling, ...
    * Elements: beams, shells, volumes

We display on Figure 2 the steps to solve the structural analysis problem.

.. blockdiag::
   :align: center

   blockdiag {

   pyBDF.py [shape = ellipse];
   Setup_struct.py [shape = ellipse];
   Struct_run.py [shape = ellipse];
   pyFoce.py [shape = ellipse];
   ICEM [shape = ellipse];

   "Geometry (PYGEO)" -> pyBDF.py -> Structure -> ICEM -> "Nastran mesh" -> Setup_struct.py
   "RANS (ADFLOW)" -> pyFoce.py -> Force.txt
   Force.txt ->  Setup_struct.py -> Struct_run.py -> "f5 file"

   group {
   color = gold;
   label = "Step 1";
   "Geometry (PYGEO)" ,pyBDF.py ,Structure ,ICEM ,"Nastran mesh"
   }

   group {
   color = blue;
   label = "Step 2";
   "RANS (ADFLOW)" ,pyFoce.py ,Force.txt
   }

   group {
   color = green;
   label = "Step 3";
   Setup_struct.py
   }

   group {
   color = red;
   label = "Step 4";
   Struct_run.py ,"f5 file"
   }

   }

.. centered::
   **Figure 2: diagram of the structural problem solving steps**

Table of Contents
================================================================================

.. toctree::
   :maxdepth: 1

   struct_pylayout
   struct_force
   struct_tacs

.. _Struct_step1:

Preliminar
==========
Creat a directory in TUTORIAL called STRUC like on the :ref:`diagram <DIAGRAM>`. Then inside create the BDF, FORCE and TACS directory.

Step 1: create a BDF
====================
A BFD file is a standard Nastran input file. It is possible to make one with most of the commercial meshing software: ICEM, Patran, etc. It Holds nodal information, element connections, and boundary conditions needed to initialize pyTACS.

.. blockdiag::
   :align: center

   blockdiag {

   pyBDF.py [shape = ellipse];
   ICEM [shape = ellipse];

   "Geometry (PYGEO)" -> pyBDF.py -> Structure -> ICEM -> "Nastran mesh"

   group {
   color = gold;
   label = "Step 1";
   "Geometry (PYGEO)" ,pyBDF.py ,Structure ,ICEM ,"Nastran mesh"
   }
   }

.. centered::
   **Figure 3: step 1, BDF file**

In order to create a BDF file follow the instructions of the :ref:`BDF tutorial <BDF>`
It is divided into two subsections (elliptical forms on Figure 3):

#. Edit pyBDF.py then run it in the terminal in order to get the structural wing geometry.
#. Open the ".tin" file generated with ICEM (icemcfd) and save a BDF file (get the structural wing mesh).

.. _Struct_step2:

Step 2: force/load file
=======================
Each structural problem is based on a specific load case. So you need to solve an aerodynamic problem (Figure 4, gray rectangle) beforehand in order to obtain the load file:
 .. centered:: **X, Y, Z, Fx, Fy, Fz**.

If you don't have a force file associated with the current geometry studying follow the instructions of the  in :ref:`load/force tutorial <FORCE>`. The tutorial will help you modify your RANS (ADflow) python file in order to generate the load/force file (Figure 7, step 2).

.. blockdiag::
   :align: center

   blockdiag {

   pyFoce.py [shape = ellipse];
   "RANS (ADFLOW)" -> pyFoce.py -> Force.txt

   group {
   color = blue;
   label = "Step 2";
   "RANS (ADFLOW)" ,pyFoce.py ,Force.txt
   }

   }

.. centered::
   **Figure 4: step 2, load file**

.. _Struct_step3:

Step 3: structure setup
=======================
In this step, we explain how to create the python file defining the structure geometry and properties (Figure 5, blue rectangle). Follow the structure setup tutorial in :ref:`Structure setup <Step3-chapt>`.

.. blockdiag::
   :align: center

   blockdiag {

   pyBDF.py [shape = ellipse];
   Setup_struct.py [shape = ellipse];
   pyFoce.py [shape = ellipse];
   ICEM [shape = ellipse];

   "Geometry (PYGEO)" -> pyBDF.py -> Structure -> ICEM -> "Nastran mesh" -> Setup_struct.py
   "RANS (ADFLOW)" -> pyFoce.py -> Force.txt
   Force.txt ->  Setup_struct.py

   group {
   color = none;
   label = "Step 1";
   "Geometry (PYGEO)" ,pyBDF.py ,Structure ,ICEM ,"Nastran mesh"
   }

   group {
   color = none;
   label = "Step 2";
   "RANS (ADFLOW)" ,pyFoce.py ,Force.txt
   }

   group {
   color = green;
   label = "Step 3";
   Setup_struct.py
   }

   }

.. centered::
   **Figure 5: step 3, geometry setup**

.. _Struct_step4:

Step 4: TACS solver
===================
In step 4 displayed in Figure 6,  we build the "main" python file. It contains the pytACS functions defining the load problem/boundary conditions and a call to the structure setup generated in step 3. By running this file with pyTACS, the structural problem will be solved and the output files for the analysis will be written.

.. blockdiag::
   :align: center

   blockdiag {

   pyBDF.py [shape = ellipse];
   Setup_struct.py [shape = ellipse];
   Struct_run.py [shape = ellipse];
   pyFoce.py [shape = ellipse];
   ICEM [shape = ellipse];

   "Geometry (PYGEO)" -> pyBDF.py -> Structure -> ICEM -> "Nastran mesh" -> Setup_struct.py
   "RANS (ADFLOW)" -> pyFoce.py -> Force.txt
   Force.txt ->  Setup_struct.py -> Struct_run.py -> "f5 file"

   group {
   color = none;
   label = "Step 1";
   "Geometry (PYGEO)" ,pyBDF.py ,Structure ,ICEM ,"Nastran mesh"
   }

   group {
   color = none;
   label = "Step 2";
   "RANS (ADFLOW)" ,pyFoce.py ,Force.txt
   }

   group {
   color = none;
   label = "Step 3";
   Setup_struct.py
   }

   group {
   color = red;
   label = "Step 4";
   Struct_run.py ,"f5 file"
   }

   }

.. centered::
  **Figure 6: description of step 4: solving the structural problem**

Open the file TUTORIAL/STRUC/TACS/Struct_run.py.

Defining the inputs and completting the structural problem
----------------------------------------------------------

First, Import the libraries for running tacs and defining the problem
::
	import numpy
	from mpi4py import MPI
	from baseclasses import *
	from tacs import *
	from repostate import *

Then define the path of the structural geometry properties setup python file, and the output directory.
::
	Setup_structure = 'Setup_structure.py'
	outputDirectory =  './output_files/'

Add the python object that holds information specific to each load case:  name, loads (force file), user requested functions, load factor, etc.
::
	SPs = [StructProblem('lc0', loadFile='forces.txt', evalFuncs=['mass','ks0'])]
	numLoadCases = len(SPs)

Define the ways you want to set the loads.
::
	F = numpy.array([0.0, 3E5, 0.0])
	pt = numpy.array([8.0208, -0.0885, 14.000])

Transfert (execute) inside the main file, the python file defined in step 3 in order to set up the properties and geometry information of the structure
::
	 execfile(Setup_structure)

Solve the problem with TACS
---------------------------
Each structural problem (SP) is solved by calling FEASolver(SP), the pyTACS instance. Then, the requested functions are evaluated with a call to evalFuncs(). The output 'f5 file' (solution) can be written with a call to writeOutputFile().
::
	funcs = {}
	for i in range(numLoadCases):
		FEASolver(SPs[i])
		FEASolver.evalFunctions(SPs[i], funcs)

	FEASolver.writeOutputFile(outputDirectory+'output.f5')

Output file
-----------
To visualize the solution, the .f5 file must be converted to a .plt (Tecplot file). Use the "f5totec" command in the terminal.

What outputs are in the file?

* u0, v0, w0, rotx, roty, roty: 6 DOF displacements at each node
* ex0, ey0, exy0, exz0, eyz0: Mid-plane shell strains
* ex1, ey1, exy1:  Through thickness shell curvature
* sx0, sy0, sxy0, sxz0, sxy0: Stress resultants, () (force/length)
* sx1, sy1, sxy1: Moment resultants, (moment/length)
* lambda, buckling: Failure and buckling constraints (>1 => Violated)

.. centered::
   :ref:`Previous: ADflow <ADFLOW>` | :ref:`Summary <SUMMARY>`
