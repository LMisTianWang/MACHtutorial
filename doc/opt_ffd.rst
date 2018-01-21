
.. centered::
   :ref:`opt_pyopt` | :ref:`opt_aero`

.. _opt_ffd:

*************************
Geometric Parametrization
*************************

Introduction
================================================================================
In order to optimize the shape of a geometry such as an airfoil or a wing, we need some way to translate design variables into actual changes in the shape.
We use the Free-form deformation (FFD) technique, popularized by Tom Sederberg in the world of computer-aided graphic design, as our parametrization method.
The FFD is a mapping of a region in 2D or 3D that is bounded by a set of B-splines.
Every point with the region is mapped to a new location based on the deformation of the bounding B-spline curves.
The B-splines themselves are defined by control points, so by adjusting the positions of these control points, we can have a great deal of control over any points embedded in the FFD volume.
Since both our CFD meshes and finite element models are point-based, we can embed them in the FFD and give the optimizer control over their shape.

The actual implementation of the FFD method is housed in the pyGeo repository, which we were already introduced in the very beginning of the tutorial.
The specific file to look for is ``pygeo/DVGeometry.py``.
Before diving into the parametrization, however, we need to generate an FFD, which is basically a 3D grid in the plot3d format.

Files
================================================================================
Navigate to the directory ``opt/parametrization`` in your tutorial folder.
Copy the following files from the MACHtutorial repository:
::

    $ cp ~/hg/machtutorial/tutorial/opt/ffd/simple_ffd.py .

Create the following empty runscript in the current directory:

- ``parametrize.py``

Creating an FFD volume
================================================================================
As mentioned above, the actual definition of an FFD volume is simply a 3D grid of points.
We can create this by hand in a meshing software like ICEM, or for very simple cases, we can generate it with a script.
For this tutorial, we are dealing with a relatively simple wing geometry---straight edges, no kink, no dihedral---so we will just use the script approach.
This script is not very generalizable though, so it is not part of the MACH library.
I will explain briefly how it works, but I won't give it the same attention as the other scripts we use in this tutorial.

Open the script ``simple_ffd.py`` in your favorite text editor.


Setting up a geometric parametrization with DVGeometry
================================================================================


.. centered::
    :ref:`opt_pyopt` | :ref:`opt_aero`
