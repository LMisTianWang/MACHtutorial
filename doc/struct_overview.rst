
.. centered::
   :ref:`intro` | :ref:`struct_geo`

.. _struct_overview:

###########################
Part 2: Structural Analysis
###########################

Overview
================================================================================
TACS is the Toolkit for Analysis of Composite Structures written in C++.
This tutorial will help you use pyTACS, the python interface of TACS.

    - Solution types: linear static, nonlinear static, buckling
    - Elements: beams, shells, volumes

TACS supports structural model data in the Nastran Bulk Data File (BDF) format.
A typical BDF file contains grid points, elements, element properties, boundary conditions, and load conditions.
The MeshLoader class in TACS will read in data for grid points, elements, and boundary conditions, but the element properties and load conditions must be formulated in the Python runscript.

Elements are the most basic functional group in TACS.
Each element is linked to its neighbors via the connectivity matrix.
Each element belongs to a component as well.

Components are made up of groups of elements that have the same property ID (PID) in the BDF file.

Table of Contents
================================================================================

.. toctree::
   :maxdepth: 1

   struct_pylayout
   struct_meshing
   struct_load
   struct_tacs

Directory Structure
================================================================================
::

    struct
    |-- geometry
    |   |-- generate_wingbox.py
    |-- meshing
    |   |-- wingbox.bdf
    |-- loading
    |   |-- aero_run.py
    |-- analysis
        |-- aero_run.py

Output file
-----------
To visualize the solution, the .f5 file must be converted to a .plt (Tecplot file). Use the "f5totec" command in the terminal.

What outputs are in the file?

* u0, v0, w0, rotx, roty, roty: 6 DOF displacements at each node
* ex0, ey0, exy0, exz0, eyz0: Mid-plane shell strains
* ex1, ey1, exy1:  Through thickness shell curvature
* sx0, sy0, sxy0, sxz0, sxy0: Stress resultants, (force/length)
* sx1, sy1, sxy1: Moment resultants, (moment/length)
* lambda, buckling: Failure and buckling constraints (>1 => Violated)

.. centered::
   :ref:`intro` | :ref:`struct_geo`
