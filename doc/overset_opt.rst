
.. centered::
    :ref:`overset_ffds` | :ref:`intro`

.. _overset_opt:

************************
Optimization with ADflow
************************

Introduction
================================================================================
He we will set up a twist and shape optimization case for both wings with ADflow.

Files
================================================================================
Navigate to the directory ``overset_tutorial/opt`` in your tutorial folder.
Copy the following files from the volume meshing directory:
::

    $ cp ../volume/overset_combined.cgns .

Create the following empty runscript in the current directory:

- ``aero_opt_tandem.py``


Dissecting the ADflow runscript
================================================================================
Open the file ``aero_opt_tandem.py`` with your favorite text editor.
Then copy the following into this file.

Initial options

.. literalinclude:: ../tutorial/overset_tutorial/opt/aero_opt_tandem.py
   :start-after: #rst start
   :end-before: #rst initial
   
Instantiate DVgeos

.. literalinclude:: ../tutorial/overset_tutorial/opt/aero_opt_tandem.py
   :start-after: #rst initial
   :end-before: #rst dvgeos

Design vars

.. literalinclude:: ../tutorial/overset_tutorial/opt/aero_opt_tandem.py
   :start-after: #rst dvgeos
   :end-before: #rst dvs

constraints

.. literalinclude:: ../tutorial/overset_tutorial/opt/aero_opt_tandem.py
  :start-after: #rst dvs
  :end-before: #rst dvcons

Opt setup

.. literalinclude:: ../tutorial/overset_tutorial/opt/aero_opt_tandem.py
  :start-after: #rst dvcon
  :end-before: #rst end

Run it yourself!
================================================================================
Run the script:
::

    $ mpirun -np 4 python aero_opt_tandem.py

This will probably take over a day to run on a 4 core desktop computer.

.. centered::
    :ref:`overset_ffds` | :ref:`intro`
