

.. centered::
    :ref:`aero_pyhyp` | :ref:`aero_adflow`

.. _aero_cgnsutils:

***********************
Mesh Manipulation Tools
***********************

Introduction
================================================================================
There are several simple meshing operations that can be done easily enough from the command line.
For example, creating a 3D cartesian block of a given size with a specified uniform cell size only requires 4 parameters.
We have developed a suite of functions called `cgnsUtilities <https://bitbucket.org/mdolab/cgnsutilities>`_ that can be called from the command line to perform simple, repeatable tasks like this.

Files
================================================================================
Navigate to the directory ``aero/surface/volume`` in your tutorial folder.
We will perform operations on the file ``wing_vol.cgns``.

cgnsUtilities Operations
================================================================================
To get a list of all of the operations available with cgnsUtilities, run the command:
::

    $ cgns_utils -h

Coarsening a volume mesh
------------------------
Although our volume mesh is already very coarse, we can coarsen it even further.
This function is more useful in instances where we start with a very fine mesh.
To coarsen a mesh, run the command:

::

    $ cgns_utils coarsen wing_vol.cgns wing_vol_coarsened.cgns

.. centered::
    :ref:`aero_pyhyp` | :ref:`aero_adflow`
