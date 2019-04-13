
.. centered::
    :ref:`overset_ihcc` | :ref:`overset_ffds`

.. _overset_analysis:

********************
Analysis with ADflow
********************

Introduction
================================================================================
He we will run a flow simulation with ADflow.

Files
================================================================================
Navigate to the directory ``overset_tutorial/analysis`` in your tutorial folder.
Copy the following files from the volume meshing directory:
::

    $ cp ../volume/overset_combined.cgns .

Create the following empty runscript in the current directory:

- ``aero_tandem.py``


Dissecting the ADflow runscript
================================================================================
Open the file ``aero_tandem.py`` with your favorite text editor.
Then copy the following into this file.


.. literalinclude:: ../tutorial/overset_tutorial/analysis/aero_tandem.py
   :start-after: #rst start
   :end-before: #rst end


Run it yourself!
================================================================================
Run the script:
::

    $ mpirun -np 4 python aero_tandem.py


.. centered::
    :ref:`overset_ihcc` | :ref:`overset_ffds`
