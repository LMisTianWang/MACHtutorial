
.. centered::
   :ref:`struct_mesh` | :ref:`struct_tacs`

.. _struct_load:

*****************
Aerodynamic Loads
*****************

Introduction
================================================================================
Many times we want to apply aerodynamic loads to the structure without going through the trouble of setting up the aerostructural solver.
This can be done by exporting the loads from a CFD solution and applying these static loads in TACS.
In this section, we will show how to obtain a CFD solution for a specific load case and then export the aerodynamic loads to be used in the next section.

Files
================================================================================
Navigate to the directory ``struct/loading`` in your tutorial folder.
Copy the following files from the MACHtutorial repository:
::

    $ cp ../../aero/volume/wing_vol.cgns .

Create the following empty runscript in the current directory:

- ``cl_solve.py``

How to do a |CL| solve
================================================================================
.. literalinclude:: ../tutorial/struct/loading/cl_solve.py

The function to do a |CL| solve is ``CFDSolver.solveCL``.
All you need to do is provide the desired |CL| value and ADflow will do a secant search to find the corresponding angle of attack.
Once this is done, the aerodynamic forces can be exported using ``CFDSolver.writeForceFile``.

Run it yourself!
================================================================================
::

    $ mpirun -np 4 python cl_solve.py

.. centered::
    :ref:`struct_mesh` | :ref:`struct_tacs`

.. |CL| replace:: C\ :sub:`L`