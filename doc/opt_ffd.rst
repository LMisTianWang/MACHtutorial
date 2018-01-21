
.. centered::
   :ref:`opt_pyopt` | :ref:`opt_aero`

.. _opt_ffd:

*************************
Geometric Parametrization
*************************

Content
=======
*Free-Form Deformation*  is based on a box composed of control points also know as local design variables. By changing a control point position, the box shape changes and the substance/volume inside moves along and adapt itself in order to fit inside the deformed box. The idea is kind of similar to a Jelly block. By modifying the jelly shape the molecules inside (volume mesh nodes) will move along.

.. _OPTIM_GENERATION_FFD:


How to generate a ffd
=====================
The input python file for generating an FFD (A box formed of control points) is dived in 4 steps:

#. Edit a python file inside the FFD directory and import some basic libraries.
#. Define the box boundaries.
#. Define the control points coordinates.
#. Save the control points in the data file.

Each one of these points is explained and illustrated for the wing example. In order to make your own python file follow each step and adapt the code for your case by modifying the geometric values and file names.

Edit file.py and include libraries
-------------------------------------
Open a new python file and import the fundamental package for scientific computing numpy and the division from future library `describe here <https://docs.python.org/2/library/__future__.html>`_.
::
	from __future__ import division
	import numpy

Define the wing box
-------------------
In order to create the *Free-Form* box, you need to define the box boundaries. For a wing use the root and the tip domains with some adjustment in order to set the wing within the box. Then define the control points coordinates on the box upper and lower sides . These control points are called local design variables and are used for deforming the wing. Here we want to build two grills for the wing. One on the upper side and one on the lower side. Each grills is composed of 6 (nX: X direction) x 8 (nZ: Z direction or spanwise) design variables.
::
	x_root_range = [-1.0E-01, 5.5]
	y_root_range = [-1.0    , 1.0]
	z_root = -1.0E-03

	x_tip_range = [6.0, 8.0]
	y_tip_range = [0.0, 2.0]
	z_tip = 12.6

	nX = 6
	nY = 2
	nZ = 8

Repartition of the design variables
-----------------------------------
As the interaction between the fuselage and the wing is not our priority, we don't want to deform this part. Therefore we want to have more design variables near the tip in order to deform, twist, bend and rotate in every possible way the wing tip. To support and control this kind of deformations, we define a sinusoidal or curved distribution of design variables.
First, a vector of size nZ uniformly distributed and has values in [0, pi/2] is defined. Then, the sinus values of the vector are computed. This new vector has its value in [0, 1].
::
	linear_dist = numpy.linspace(0, numpy.pi/2, nZ)
	section_dist = numpy.sin(linear_dist)
	z_sections = section_dist*(z_tip - z_root) + z_root

	x_te = section_dist*(x_tip_range[0] - x_root_range[0]) + x_root_range[0]
	x_le = section_dist*(x_tip_range[1] - x_root_range[1]) + x_root_range[1]
	#Stack arrays in sequence vertically (row wise).
	y_coords = numpy.vstack((section_dist*(y_tip_range[0] - y_root_range[0]) + y_root_range[0], section_dist*(y_tip_range[1] - y_root_range[1]) + y_root_range[1]))

Once the design variables defined, initialize 3 zeros matrix  of size (nY*nZ, nX) and fill them with the design variable coordinates.
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

Write an FFD file
-----------------
Finally, the design variables are written in a file as a tuple (a sequence of immutable Python objects).
::
	filename = "filename.fmt"
	f = open(filename, 'w')
	f.write('\t\t1\n')
	f.write('\t\t%d\t\t%d\t\t%d\n' % (nX, nY, nZ))
	for set in [X,Y,Z]:
		for row in set:
			vals = tuple(row)
			f.write('\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\n' % vals)

	f.close()

Now that the python input file is finished, run it with the command:
::
	$ python python_filename.py



How to deform a FFD
===================

.. _OPTIM_DEFORMATION_FFD:

FFD deformation
---------------
Here, we are interested in a simple case of twist deformation. A twist deformation is seen as a global design variable which will affect the local design variables on the FFD box. In order to twist a wing with a global design parameter, it is required to define an axis. This axis is a reference for the local design variables. They will move relative to the reference axis. In order to perform a deformation, the geometric design variable class DVGeo and its functions are used. A description of the class is available `here <http://mdolab.engin.umich.edu/doc/packages/pygeo/doc/DVGeometry.html>`_.

First, add the libraries and load the FFD file.
::
	import numpy
	from pygeo import pyBlock, DVGeometry
	from pyspline import pySpline
	from pyoptsparse import SqliteDict
	from pywarpustruct import USMesh
	import warnings
	warnings.filterwarnings("ignore")

	FFDFile = 'filename.fmt'
	DVGeo = DVGeometry(FFDFile)

Then the starting/ending points of the segment used as the reference axis is defined such as:
* For the *x* coordinates we used the chord/4 position.
* For the *y* coordinates the leading edge position is used.
* For the *z* coordinates the root and tip spanwize position (a bit wider)
::

	x = [0.0+5.41/4.0 , 6.24+1.29/4.0]
	y = [0.0     , 1.16]
	z = [-1.0E-03, 12.6]


This axis is called wing and is composed of 5 nodes uniformly distributed. By moving the nodes on the axis, the design variables associated to each one of them will also change position.
::
	nTwist = 5
	tmp = pySpline.Curve(x=x, y=y, z=z, k=2)
	X = tmp(numpy.linspace(0, 1, nTwist+1))
	c1 = pySpline.Curve(X=X, k=2)
	DVGeo.addRefAxis('wing', c1)

Once the reference axis added to the DVGeo dictionary/object, we define the twist function. This function takes 2 arguments: the vector with the twist values, the matrix of movement to apply to the local DV (design variables). It is applied on each local design variable: once for the design variables on the upper grill, once for the lower grill for each array of design variables along the span wise direction. As we don’t want to modify the root array, we fix then design variables at the root by starting at i+1 inside geo.rot_z with i going from 0 to 4 (1 to 5).
::
	def twist(val, geo):
		for i in xrange(nTwist):
			geo.rot_z['wing'].coef[i+1] = val[i]

After adding the twist function to the DVGeo object. A constraint function is defined in order to restrain its range of application. For instance the twist can go from -50 degrees to 50 degrees. This function is useful when coupling with an optimizer in order to fix some boundary values. Also, the scaling makes possible to return a value inside [-1,1] in order to keep the same magnitude for each design variable.
::
	DVGeo.addGeoDVGlobal('twist', 0*numpy.ones(nTwist), twist,lower=-50, upper=50, scale=0.20)

To perform a twist on the local design variables, get a copy of the DVgeo current design variables coordinates. Then, modify the copy values with the twist function using an array of size ntwist with progressive values in [0, 50] degrees. Finally, set the new design variables values in DVGeo.
::
	dvDict = DVGeo.getValues()
	dvDict['twist'] = numpy.linspace(0, 50, nTwist)
	DVGeo.setDesignVars(dvDict)

.. OPTIM_DEFORMATION_FFD_MESH:

Mesh deformation
----------------
Now that the FFD has been modified, upgrade the mesh associated. First, define the name and caracteristics of the mesh , then upload it.
::
	gridFile = 'wing_mvol2.cgns'
	meshOptions = {'gridFile':gridFile,'warpType':'unstructured'}
	mesh = USMesh(options=meshOptions)

Then determine the surface mesh coordinates, copy them  into a new object and add the object "coords" to the DVGeo class in order to apply the twist on it.
::
	coords0 = mesh.getSurfaceCoordinates()
	coords = coords0.copy()
	DVGeo.addPointSet(coords, 'coords')

Upload the surface mesh coordinates with a call to the DVGeo "coords" object. Warp the volume mesh, write the new FFD and geometry into a file.
::
	mesh.setSurfaceCoordinates(DVGeo.update('coords'))
	mesh.warpMesh()
	DVGeo.writePlot3d('modifiedFFD.fmt')
	mesh.writeGrid('postwarp-twist.cgns')


Comparaison between the orignal FFD/wing and a 50 degrees twisted FFD/wing
==========================================================================
On Figure 1, we display a comparison between the reference wing box in red and the deformed one in black after a twist of 50 deg. in the spanwise direction for Z>2.8. The spheres symbols correspond to the local design variables.

.. figure:: Pic/Optim/FFD/fig1-ffd.png
   :width: 500px
   :align: center
   :height: 400px
   :alt: alternate text
   :figclass: align-center

   Figure 1: comparison between a 50 degrees twisted FFD and the reference FFD.

Here, we display the wing associated with each wing box. The reference wing is plotted in red and the deformed wing (twist of 50 deg for a spanwise z>2.8) in black.


.. figure:: Pic/Optim/FFD/fig2-ffd.png
   :width: 400px
   :align: center
   :height: 400px
   :alt: alternate text
   :figclass: align-center

   Figure 2: comparison between a 50 degrees twisted wing and the reference wing.

How to plot a cngs and fmt files with Tecplot
=============================================
In order to plot with Tecplot a geometry and the local design variables associated like on Figure 3 follow the instructions.

#. Open Tecplot (tec360), then load the cgns file.

#. Load the ".fmt" file:
	File -> Load data → advance option  → plot3D loader xyz → open → add files → select ".fmt" → Ok.

#. Once the file loaded, select/active the “.fmt” file if they are not displayed on the screen:
	Zone style → surface.

Active the translucency, the mesh and the scatter options on the left side (above zone style). Then deselect the scatter option for the cgns files:
	Zone style → scatter.
	For the scatter symbol pick the sphere shape with a size of 1%.

#. Pick the color for the meshes, shades, scatters and wings.

.. figure:: Pic/Optim/FFD/figure3.png
   :align: center

   Figure 3: output options for the Nastran solver.


.. centered::
    :ref:`opt_pyopt` | :ref:`opt_aero`
