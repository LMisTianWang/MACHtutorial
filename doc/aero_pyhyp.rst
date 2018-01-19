
.. centered::
    :ref:`aero_icem` | :ref:`aero_cgnsutils`


.. _aero_pyhyp:

**************
Volume Meshing
**************

Content
=======
The objective of this chapter is to create a volume mesh using pyhyp meshing software. pyhyp is based on a hyperbolic grid generation scheme. Compared to elliptic grid generation methods the speed of the scheme remains one to two orders of magnitude faster than typical.

Documentation for the tutorial
==============================
The python file created for pyHyp in this tutorial is based on the `pyhyp doc <http://mdolab.engin.umich.edu/doc/packages/pyhyp/doc/index.html>`_ . The section of interest is called ‘usage with Plot3d Files’. It contains a well-detailed example for a sphere where each input parameter is explained. It may also be useful later to read “Usage with CGNS Files”. If you want to have a better understand of the code, you may want to read the theoretical article of Chan and Steger available in the reference directory:
::
	$ cd ~/hg/pyhyp/references

If you are in need later of a specific option, you may want to take a look also at the python code file:
::
	$ gedit ~hg/pyhyp/python/pyHyp.py

Look for 'class pyHyp(object)' with ctrl+g. All the options available and default parameters are commented within the pyHyp class.

Generation of the input python file
===================================
Open the file pymesh.py with your favorite text editor.
::
	$ cd PYHYP
	$ gedit pymesh.py

Before copying from  `pyhyp documentation <http://mdolab.engin.umich.edu/doc/packages/pyhyp/doc/index.html>`_  the first block of code in ‘usage with Plot3d Files’ inside pymesh.py, read the ‘usage with Plot3d Files’ section.
As you saw in ‘usage with Plot3d Files’ the python file is dived in 3 parts:

#. Import
#. Options
#. Generation and writing (call to pyHyp and write CGNS functions)

You can almost use the copy as it is.  However, a few input parameters values need to be changed beforehand.

Import section
--------------
No changes are needed

Options
-------
* Change the inputFile name to the wing mesh you created under ICEM (CGNS file).
* We use a CGNS mesh file. Correct  'Plot3d' to 'cgns' .
* If you remember we didn't define any boundary conditions for the symmetric wall with ICEM software.  We left  the mesh open on the root. As the mesh edges on the wing's root are not connected to anything, you must define them now as part of the symmetric plan by adding the option 'unattachedEdgesAreSymmetry':True.

* Define the far-field with 'outerFaceBC': 'farfield'.
* As you build a multiblock mesh you want to add the connection between each block: 'AutoConnect': 'True'

Grid Parameters
****************
* Adjust the number of layer to 90.
* Fix the tickness of the first layer to 1e-5.
* Put the far-field distance at 20*wingspan (around 20m): 'marchDist':20.0*20

Pseudo Grid parameters
**********************
Putting a negative value for the next two parameters implies the mesh generator will automatically determine the best value.

* ps0=-1
* pGridRatio=-1
* Delete 'rMin option.

Smoothing parameters
********************
* epsE= 2.0
* epsI= 4.0
* theta= 2.0

Solution parameters
*******************
* Delete the 'preConLag' option.

Generation and writing
**********************
* In hyp.writeCGNS('sphere.cgns') you want to change the name in order to be more explicit that you work on a wing ( for instance 'wing_mvol.cgns').

Run ADflow
==========
Once your python file is finished you can run it with python in the terminal:
::
	$ python pymesh.py

.. centered::
    :ref:`aero_icem` | :ref:`aero_cgnsutils`
