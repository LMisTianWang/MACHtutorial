
.. centered::
    :ref:`aerostruct_analysis_split` | :ref:`intro`

.. _aerostruct_analysis:

*********************************************
Aerostructural analysis - stacked processsors
*********************************************

Introduction
================================================================================
This tutorial introduces the setup for a basic aerostructural analysis.
This builds on the aerodynamic and structural analyses completed in previous tutorials and 
uses the "setup_structure.py" script from the previous section. 
This aerostructural model is setup with the aerodynamic and structural analyses stacked on the same 
set of processors.

Files
================================================================================
Navigate to the directory ``aerostruct`` in your tutorial folder.
Copy the following files to this directory:
::

    $ cp ../aero/meshing/volume/wing_vol.cgns .
    $ cp ../struct/meshing/wingbox.bdf .

Create the following empty runscript in the current directory:

- ``as_run_nosplit.py``


Dissecting the aerostructural runscript
================================================================================
Open the file ``as_run_nosplit.py`` with your favorite text editor.
Then copy the code from each of the following sections into this file.

Import libraries
----------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst Imports (beg)
   :end-before: #rst Imports (end)

Set mesh files
--------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst Imports (end)
   :end-before: #rst comm (start)

Setup MPI communicators
-----------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst comm (start)
   :end-before: #rst comm (end)

Setup aerostructural problem
----------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst ASP (start)
   :end-before: #rst ASP (end)

Setup solver options
-------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst options (start)
   :end-before: #rst options (end)

Setup aerodynamic solver
------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst options (end)
   :end-before: #rst aerosolver (end)

Setup structural solver
------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst feaSolver (start)
   :end-before: #rst feaSolver (end)

Setup transfer object
---------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst transfer object (start)
   :end-before: #rst transfer object (end)

Setup aerostructural solver
---------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst transfer object (end)
   :end-before: #rst AS object (end)

Solve the aerostructural system
-------------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst ASSolve (start)
   :end-before: #rst ASSolve (end)

Compute the aerostructural gradients
------------------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run_nosplit.py
   :start-after: #rst ASSolve (end)
   :end-before: #rst ASAdjoint (end)

Run it yourself!
================================================================================
First make the output directory and then run the script:
::

    $ mkdir output
    $ mpirun -np 4 python as_run_nosplit.py

.. centered::
    :ref:`aerostruct_analysis_split` | :ref:`intro`


