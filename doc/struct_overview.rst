
.. centered::
   :ref:`intro` | :ref:`struct_geo`

.. _struct_overview:

###########################
Part 2: Structural Analysis
###########################

Overview
================================================================================
TACS (Toolkit for the Analysis of Composite Structures)
TACS is a Toolkit for Analysis of Composite Structures written in C++. This tutorial will help you use pyTACS the python interface of TACS. This toolkit is based on a parallelized FEA Solver:
    * Solution types: linear static, Nonlinear static, Buckling, ...
    * Elements: beams, shells, volumes

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
* sx0, sy0, sxy0, sxz0, sxy0: Stress resultants, () (force/length)
* sx1, sy1, sxy1: Moment resultants, (moment/length)
* lambda, buckling: Failure and buckling constraints (>1 => Violated)

.. centered::
   :ref:`Previous: ADflow <ADFLOW>` | :ref:`Summary <SUMMARY>`
