
.. centered::
    :ref:`aero_cgnsutils` | :ref:`intro`


.. _aero_adflow:

********************
Analysis with ADflow
********************

Content
=======
It this chapter we show how to generate an input file for ADflow and how to run a simulation. ADflow is a is a multi-block parallel structured flow solver which is capable of solving the compressible RANS equations.

Documentation for the tutorial
==============================
You will found a complete introduction of tADflow solver on `ADflow doc introduction <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/introduction.html>`_ . In order to create your input file, you need to use `ADflow doc tutorial <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/tutorial.html>`_. An explanation step by step of a basic script is presented. For the aeroOptions function, you will found a description of all the arguments inside `ADflow doc options <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/options.html>`_ . In the future, you will probably need a specific function, so you may also want to have a look at `ADflow doc pyADflow <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/pyADflow.html>`_ .

Generation of the ADflow input file
===================================
First, create a new directory called ADFLOW inside TUTORIAL/AERO.
::
	$ mkdir ADFLOW

Then copy inside ADFLOW directory the cgns volume mesh files generated in the previous chapter.
::
	$ cp -r CGNS/*.cgns ADFLOW

Edit an input python file for ADflow:
::
	$ cd ADFLOW
	$ gedit rans.py

Before copying the basic run script (first block of code) from the  `ADflow doc tutorial <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/tutorial.html>`_ You may want to read it and have a basic understanding of the functions called.

As you saw, the file is divided into three major parts:

#. Import modules
#. Input informations
#. Solution and function evaluation

In order to run the wing  case, you need to modify section 2. and 3. As you go through the editing process of section 2. (input information), you can have a basic understanding of each parameter by checking the `ADflow doc options <http://mdolab.engin.umich.edu/doc/packages/adflow/doc/options.html>`_

Import modules
--------------
Nothing to change.

Input informations
------------------
Change the grid name ('gridFile'). Then for MGCycle use the number of time the mesh has been coarse with CGNS utils. For instance, if you coarse the mesh 2 times, you define MGCycle = '2w'.

Flight cruise conditions are used for the simulation:

* alpha = 1.5
* mach = 0.82
* altitude = 10000
* CLstar (no CL needed)
* fixedCL (no CL needed)

In physics parameter sub-section add:
* 'smoother':'dadi'.

Geometrical information about the wing used for dimensioning:

* bRef= the spanwise of the wing
* chordRef = areaRef/bRef
* areaRef = the area of the projected wing.

The area of the wing is determined by a two-step process:

#. :ref:`Compute the FFD box <ADFLOW_FFD1>`
#. :ref:`Compute area ref <ADFLOW_FFD2>`

These two steps are discussed in :ref:`Ffd <OPTIM_FFD>`. As for now, we give the basic instruction to compute areaRef.

.. _ADFLOW_FFD1:

AREAREF: FFD box
****************
Open the following file: TUTORIAL/AERO/ADFLOW/FFD/ffd.py
The objective is to determine a box around the wing composed of control points or local design variables in order to do the projection at next step. To adapt the code, you need mainly to modify next variables:

* x_root_range
* y_root_range
* z_root
* x_tip_range
* y_tip_range
* z_tip

They are use to define a close box which contains the wing. In case your spanwise direction is not the Z axis adapt the code.

Import the librabry:
::

	from __future__ import division
	import numpy

Create a box around the wing. Use the the wing root and tip positions + epsilon. Be careful, the wing need to be totally inside the box.
::
	x_root_range = [-0. , 5.5]
	y_root_range = [-2.5, 2.5]
	z_root = -1.0E-3

	x_tip_range = [ 6.0 , 8.0]
	y_tip_range = [-2.0 , 2.0]
	z_tip = 12.5

Now state the number of control points on the box. Here we define a 6x8 grid on the wing upper face and lower face.
::
	nX = 6
	nY = 2
	nZ = 8

Name the output file.
::
	filename = "FFD.fmt"
	f = open(filename, 'w')
	f.write('\t\t1\n')
	f.write('\t\t%d\t\t%d\t\t%d\n' % (nX, nY, nZ))

Define a sinusoidal weighting (tighter spacing at wingtip) by creating a vector from 0 to pi/2, of dimension nZ.
::
	linear_dist = numpy.linspace(0, numpy.pi/2, nZ)

Take the sinus of the vector.
::
	section_dist = numpy.sin(linear_dist)

Define the x,y,z coordinates range for control points.
::
	z_sections = section_dist*(z_tip - z_root) + z_root
	x_te = section_dist*(x_tip_range[0] - x_root_range[0]) + x_root_range[0]
	x_le = section_dist*(x_tip_range[1] - x_root_range[1]) + x_root_range[1]
    # vstack take a sequence of arrays and stack them vertically to make a single array.
	y_coords = numpy.vstack((section_dist*(y_tip_range[0] - y_root_range[0]) + y_root_range[0], section_dist*(y_tip_range[1] - y_root_range[1]) + y_root_range[1]))

Initialize the X,Y,Z matrices. Then, fill them up with the control points coordinates.
::
	X = numpy.zeros((nY*nZ, nX))
	Y = numpy.zeros((nY*nZ, nX))
	Z = numpy.zeros((nY*nZ, nX))

	row = 0
	for k in range(nZ):
    	for j in range(nY):
        	X[row,:] = numpy.linspace(x_te[k], x_le[k], nX)
        	Y[row,:] = numpy.ones(nX)*y_coords[j,k]
        	Z[row,:] = numpy.ones(nX)*z_sections[k]
        	row += 1

	for set in [X,Y,Z]:
    	for row in set:
        	vals = tuple(row)
       	 f.write('\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\n' % vals)

	f.close()

Save the file and run it with the command:
::
	$ python ffd.py

.. _ADFLOW_FFD2:

AREAREF: compute
****************
Open the file TUTORIAL/AERO/ADFLOW/FFD/ffd2.py.

Import the library:
::
	import numpy
	from pygeo import *
	from adflow import *

	# Ignore deprecation warnings
	import warnings
	warnings.filterwarnings("ignore")

Edit the gridFile name by replacing the name with one of the coarse mesh generated with CGNS utils (don't forget that MGCycle depends on the mesh.) .
::
	gridFile = 'wing_mvol2.cgns.cgns'
	FFDFile = 'FFD.fmt'

	aeroOptions = {'gridFile': gridFile}
	CFDSolver = ADFLOW(options=aeroOptions)
	DVGeo = DVGeometry(FFDFile)
	DVCon = DVConstraints()
	DVCon.setDVGeo(DVGeo)
	DVCon.setSurface(CFDSolver.getTriangulatedMeshSurface())

Choose the axis for the projection: (X^Vect(wingspan direction))
::
	DVCon.addProjectedAreaConstraint(name='projy', scaled=False, axis='y')
	area1 = DVCon.constraints['projAreaCon']['projy'].X0

	print 'Original area:', area1

Save the file and run it with the command:
::
	$ python ffd2.py > output.

Look for the word 'Original area' inside the output file in order to get the value of areaREF.

Solution and function evaluation
---------------------------------
Add "CFDSolver = ADFLOW(options=aeroOptions)" after the input parameters.
Also, for this case we want to extract the lift distribution for 150 slices uniformly distributed over the wing span wise. Add the next code line:
::
	CFDSolver.addLiftDistribution(150, 'y'), groupName='all')

With this changes, the python file is now complete. In order to run ADflow, execute the next command. This command is used to run a parallel simulation over NB processors. If you launch it on your local computer, NB should be 2 or 4 (check it in system settings -> details)
::
	$ mpirun -np NB python rans.py  2>&1 | tee output.txt

.. centered::
    :ref:`aero_cgnsutils` | :ref:`intro`
