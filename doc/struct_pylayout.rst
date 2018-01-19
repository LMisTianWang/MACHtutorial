
.. centered::
   :ref:`Previous: step 1 <Struct_step1>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 2 <Struct_step2>`


.. _BDF:

***
BDF
***

Content
=======
A BDF is a standard input file used by Nastran the structural finite element solver developed by NASA. The BDF can be generated with most commercial meshing software like ICEM. It contains a mesh (nodes, edges, elements) of a structure. Therefore, in order to used pyTACS toolbox based on Nastran solver for analyzing the structural geometry, we need to generate a BDF. Here, we will describe how to generate the structural wing and its mesh.

Aerodynamic vs structural geometry
==================================
A comparison of the aerodynamic wing and the structural wing of the ”MDO tutorial wing” case is presented on Figure 1a & 1b. The cut made at Z=1 of both wing and displayed on Figure 1b show the common surfaces and how the structural wing fit inside the aerodynamic wing.

.. figure:: Pic/Struc/Bdf/figure1a.png
   :width: 600px
   :align: center
   :height: 300px
   :alt: alternate text
   :figclass: align-center

   Figure 1a: 3d comparison of the aerodynamic wing geometry and the structural wing geometry (or box).

.. figure:: Pic/Struc/Bdf/figure1b.png
   :width: 600px
   :align: center
   :height: 300px
   :alt: alternate text
   :figclass: align-center

   Figure 1b: comparison cut made at Z=1 of the aerodynamic wing and the structural wing

pyGeo
=====

Open the file TUTORIAL/STRUC/BDF/pyBDF.py. In the following subsections, we highlight some changes you need to make and explain some of the main functions called.

Standard Python modules
-----------------------
You need to create or import the geometry made with pyGeo in the aerodynamic analysis part. The edit a new file call pyBDF.py.
Import the libraries underneath and also create a string variable with the name of the geometry created with pyGeo.
::
	import argparse
	import numpy
	from pygeo import *
	from pyspline import *
	from pylayout import *

	surfFile = 'wing.igs'
	geo = pyGeo('iges', fileName=surfFile)
	layoutGeo = pyLayoutGeo.LayoutGeo(geo, h=.15, rightWing=True, prefix='WING')
	layoutGeo.addDomain(surf, offset=5)
	eSize = 0.2

Domain generation
-----------------
First, we define the projection direction. For this case, X define "the chord direction", Z the spanwise direction. Y is the projection direction.
::
	surf = 'y'

Then the projection plan used by the program to project all the element inside. The offset value needs to be carefully chosen when there are multiple objects (wings, etc) with different orientation directions. Otherwise, it doesn't affect the projection.
::
	layoutGeo.addDomain(surf, offset=5)

Spar Generation
---------------
Define a couple of points localized at the leading edge representative of the wing spanwise ”evolution”. For these points determine the chord of each airfoil (intersection between the wing and a Z=k plane).
::
	leRoot   =  numpy.array([0.00, 0.00,  0.00])
	leBreak  =  numpy.array([2.28, 0.43,  4.60])
	leTip    =  numpy.array([6.24, 1.16, 12.43])

	rootChord  =5.41
	breakChord =3.13
	tipChord   =1.29

Use this information for building the leading/trailing edge spars (between 10% chord at the root and 35% chord at the tip).
::
	lep0 = leRoot    + [0.10*rootChord  , 0.00, 0.00]
	lep1 = leBreak   + [0.10*breakChord , 0.00, 0.00]
	lep2 = leTip     + [0.35*tipChord   , 0.00, 0.00]

	tep0 = leRoot    + [0.60*rootChord  , 0.00, 0.00]
	tep1 = leBreak   + [0.60*breakChord , 0.00, 0.00]
	tep2 = leTip     + [0.60*tipChord   , 0.00, 0.00]


Add the leading edge and trailing edge spar to the geometry.
::
	layoutGeo.addComponent('spar', [ lep0, lep1, lep2], tag='le_spar', elemSize=eSize, nSeg=10)
	layoutGeo.addComponent('spar', [ tep0, tep1, tep2], tag='te_spar', elemSize=eSize, nSeg=10)


Rib generation
--------------
There is two possibilities for picking the rib axis or plane direction:

#. Choose the flow direction x-axis.
#. The normal to the leading edge.

Here, we define the vector x direction.
::
	xaxis = numpy.array([1.0, 0, 0])

As you can see on Figure 1a, the wing is divided into two parts:

#. From the root to the kink.
#. From the kink to the tip

We have 4 ribs (N=4) spanwise, in the x-axis direction, from the root to the kink.
::

	basePt = lep0
	i=0
	print "base point i=%d coord:" %(i)
	print basePt
	layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis,bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)

	N = 4
	for i in range(1,N-1):
		basePt = lep0 + (float(i)/(N-1))*(lep1 - lep0)
		print "base point i=%d coord:" %(i)
		print basePt
		layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis, bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)

	basePt = lep1
	print "base point i=%d coord:" %(N-1)
	print basePt

	layoutGeo.addComponent('rib', basePt=basePt, bidirectional=True, direction=xaxis, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)

From the kink until reaching the tip we add 9 ribs spanwise in x-axis direction or Vector ribDirection. where Vect ribDirection is defined such as the vector perpendicular to the leading edge. Copy/paste and adapt the precedent code block in order to add the 9 ribs.
::
	N = 10
	for i in range(1,N-1):
		basePt = lep1 + (float(i)/(N-1))*(lep2 - lep1)
		print "base point i=%d coord:" %(i)
		print basePt
		layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis, bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize, leRib=False)

A final rib is added parallel to the flow at the wing tip:
::
	basePt = lep2
	print "base point tip coord:"
	print basePt
	layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis,bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'],elemSize=eSize, leRib=False)

Skin Generation
---------------
Now that the wing skeleton is defined, we add the skin.
::
	layoutGeo.addSkins(elemSize=eSize)

Write .tin File
---------------
To finish this section, write the wing structure in an ICEM friendly format.
::
	layoutGeo.writeTinFile('wing_box.tin')


Mesh the wing box
=================
In section 3. you will work with the mesh software ICEM. Open a new terminal. Create a new folder inside STRUC/BDF called ICEM and copy wing_box.tin inside. Then run inside "icemcfd wing_box.tin" and create a new project:
::
	$ mkdir ICEM
	$ cp wing_box.tin ICEM/wing_box.tin
	$ cd ICEM
	$ icemcfd wing_box.tin


Check if the skin is attached to the ribs
-----------------------------------------
Select the geometry label: repair tools button (Figure 2.a) → build diagnostic. Set the tolerance 0.02 see Figure 2.b (up to you to choose the tolerance but you need to be careful on pieces like the wing tip where the geometry get thinner and sharper).

.. figure:: Pic/Struc/Bdf/BDF_step-1.png
   :width: 400px
   :align: center
   :height: 50px
   :alt: alternate text
   :figclass: align-center

   Figure 2.a: geometry repair tools

.. figure:: Pic/Struc/Bdf/BDF_step-1b.png
   :width: 400px
   :align: center
   :height: 400px
   :alt: alternate text
   :figclass: align-center

   Figure 2.b: build diagnostic

You can see two different types of lightened segments(geometry curves) on Figure 3:

#. The red ones are connected to 2 pieces (spar/spar, spar/rib, spar/skin or skin/skin)
#. The blue ones are connected to 3 pieces (skin/rib/skin or spar/rib/skin).

If a rib, spar or skin is not well connected change the tolerance value.

If you haven't done it before, try to use the solid simple display.

.. figure:: Pic/Struc/Bdf/figure2.png
   :width: 400px
   :align: center
   :height: 200px
   :alt: alternate text
   :figclass: align-center

   Figure 3 : connectivity between elements of the structural wing. Blue segments: 3 intersections. Red segments: 2 intersections

Verify the normal orientation
-----------------------------
On the tree (left side of ICEM window):
Select Geometry → Surfaces →  Show normals → Normal using color (Figure 4).

.. figure:: Pic/Struc/Bdf/surface_normal_color.png
   :width: 200px
   :align: center
   :height: 400px
   :alt: alternate text
   :figclass: align-center

   Figure 4: Normal using color

The normals to the skin are well oriented if they point outside the wing. The skin color should be gray on the outside like in Figure 6b. Otherwise, you will have a different skin color like on Figure 6a. In order to correct it, you need to reverse the orientation:
Geometry → Repair geometry → Modify normal → Reverse normal (Figure 5)

.. figure:: Pic/Struc/Bdf/BDF_step-2.png
   :width: 400px
   :align: center
   :height: 200px
   :alt: alternate text
   :figclass: align-center

   Figure 5: modify the normals

.. figure:: Pic/Struc/Bdf/normal.png
   :width: 300px
   :align: center
   :height: 300px
   :alt: alternate text
   :figclass: align-center

   Figure 6: cartography of the skin normals orientation. a) Skin normals oriented in different directions. b) Skin normals oriented to the outside domain.

Mesh setup
----------
Mesh → Global Mesh setup → Shell Meshing parameters (Figure 7a):
In option, select all quad for the mesh type.

.. figure:: Pic/Struc/Bdf/shell_mesh.png
   :width: 200px
   :align: center
   :height: 500px
   :alt: alternate text
   :figclass: align-center

   Figure 7a: shell mesh option

Mesh → Global Mesh setup → Compute Mesh → Surface mesh only (Figure 7b):
Compute.

.. figure:: Pic/Struc/Bdf/global_mesh.png
   :width: 200px
   :align: center
   :height: 200px
   :alt: alternate text
   :figclass: align-center

   Figure 7b: global mesh

Verification of the mesh quality
--------------------------------
Mesh →  Part Mesh Setup:
All elements need to have the same maximum size (Figure 8). If not, click on maximum size in the table, correct the value and re-compute the mesh.

.. figure:: Pic/Struc/Bdf/figure4.png
   :width: 600px
   :align: center
   :height: 400px
   :alt: alternate text
   :figclass: align-center

   Figure 8: element size table for the structural mesh.

Boundaries constrains
---------------------
Constrains → Create constrains
Options:

* SPC type: constraint only
* Entity type: create constraint/displacement on surface
* Wing part inside the fuselage: Ux=0, … RotZ=0 (not taken into account for this tutorial, so skip this constrain)
* Root: Uy=0 (for the part connect to the fuselage normaly)
* Leading edge (LE_SPAR): Ux=0 (Figure 9).

.. figure:: Pic/Struc/Bdf/constrain-normal.png
   :align: center

   Figure 9: leading edge constrain (LE_SPAR): Ux=0


Output files
------------
Solve-Options → Write/View Input File:
Check if Solver is NASTRAN and apply.

Output → Select Solver:
Option:

* Output Solver: Nastran
* Common Structural Solver: Nastran

Write input:

* Follow the instructions of ICEM (if you are asked to select a solver, pick Nastran)
* Nastran options (Figure 10):

	* Large or small field format : Large
	* Write volume elements: None
	* Write elements elements: All
	* Write bar elements: None


.. figure:: Pic/Struc/Bdf/save.png
   :width: 250px
   :align: center
   :height: 200px
   :alt: alternate text
   :figclass: align-center

   Figure 10: output options for the Nastran solver.

.. centered::
   :ref:`Previous: step 1 <Struct_step1>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 2 <Struct_step2>`
