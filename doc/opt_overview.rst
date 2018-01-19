
.. centered::
   :ref:`Previous: Structural Analysis <Struct>` | :ref:`Summary <SUMMARY>` | :ref:`Next: FFD <OPTIM_ffd>`

.. _OPTIM:

####################
Part 3: optimization
####################

Content
=======
This part is based on "part 1: aerodynamic analysis" and "part 2: structure analysis". All the inputs for solving an optimization problem on the wing come from these parts.

Table of Contents
================================================================================

.. toctree::
   :maxdepth: 1

   opt_ffd
   opt_aero
   opt_struct

Aerodynamic Shape Optimization Tutorial
=======================================
For the aerodynamic shape optimization, we used the same inputs than for part 1, ADflow. We only adapt the rans.py file by adding the optimizer functions.

Example of problem to solve
---------------------------
For a given aerodynamic configuration and lift, find the geometry which minimizes the drag.

Structural Shape Optimization Tutorial
======================================
For the structural shape optimization, we used the same inputs than with TACS. Again, only the struct_run  changes. We add the optimizer functions.

Example of problem to solve
---------------------------
For a given topology, find the lightest truss that can carry a given load.

Preliminary work
=================
Create inside the TUTORIAL directory the next directory and sub-directories:

* OPTIM
	* FFD
	* OPT_AERO
	* OPT_STRUC



.. centered::
   ref:`Previous: Structural Analysis <Struct>` | :ref:`Summary <SUMMARY>` | :ref:`Next: FFD <OPTIM_ffd>`
