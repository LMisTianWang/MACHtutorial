
.. centered::
    :ref:`setup_structure` | :ref:`aerostruct_analysis`

.. _aerostruct_analysis_split:

******************************************
Aerostructural analysis - split processors
******************************************

Introduction
================================================================================
This tutorial introduces the setup for a basic aerostructural analysis.
This builds on the aerodynamic and structural analyses completed in previous tutorials and 
uses the "setup_structure.py" script from the previous section. 
This aerostructural model is setup with separate processor groups for the aerodynamic and structural
analyses.

Files
================================================================================
Navigate to the directory ``aerostruct`` in your tutorial folder.
Copy the following files to this directory:
::

    $ cp ../aero/meshing/volume/wing_vol.cgns .
    $ cp ../struct/meshing/wingbox.bdf .

Create the following empty runscript in the current directory:

- ``as_run.py``


Dissecting the aerostructural runscript
================================================================================
Open the file ``as_run.py`` with your favorite text editor.
Then copy the code from each of the following sections into this file.

Import libraries
----------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst Imports (begin)
   :end-before: #rst Imports (end)

Set mesh files
--------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst Imports (end)
   :end-before: #rst comms (begin)

Setup MPI communicators
-----------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst comms (begin)
   :end-before: #rst comms (end)

Setup aerostructural problem
----------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst problems (start)
   :end-before: #rst problems (end)

Setup aerodynamic options
-------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst aeroOptions (start)
   :end-before: #rst aeroOptions (end)

Setup aerodynamic solver
------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst aeroOptions (end)
   :end-before: #rst aerosolver (end)

Setup structural options
------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst structopt (start)
   :end-before: #rst structopt (end)

Setup structural solver
------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst structopt (end)
   :end-before: #rst feaSolver (end)


Setup aerostructural options
----------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst AS options (start)
   :end-before: #rst AS options (end)

Setup transfer object
---------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst AS options (end)
   :end-before: #rst transfer (end)

Setup aerostructural solver
---------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst transfer (end)
   :end-before: #rst ASSetup (end)

Solve the aerostructural system
-------------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst ASSolve
   :end-before: #rst ASSolve (end)

Compute the aerostructural gradients
------------------------------------
.. literalinclude:: ../tutorial/aerostruct/as_run.py
   :start-after: #rst ASSolve (end)
   :end-before: #rst ASAdjoint (end)

Run it yourself!
================================================================================
First make the output directory and then run the script:
::

    $ mkdir output
    $ mpirun -np 4 python as_run.py

.. centered::
    :ref:`setup_structure` | :ref:`aerostruct_analysis`
