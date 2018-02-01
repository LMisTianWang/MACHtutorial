
.. centered::
    :ref:`aerostruct_overview` | :ref:`intro`

.. _aerostruct_analysis:

***********************
Aerostructural analysis
***********************

Introduction
================================================================================


Files
================================================================================
Navigate to the directory ``aerostruct`` in your tutorial folder.
Copy the following files to this directory:
::

    $ cp ../opt/ffd/ffd.xyz .
    $ cp ../aero/meshing/volume/wing_vol.cgns .
    $ cp ../struct/meshing/wingbox.bdf .

Create the following empty runscript in the current directory:

- ``as_run.py``


Dissecting the ADflow runscript
================================================================================
Open the file ``as_run.py`` with your favorite text editor.
Then copy the code from each of the following sections into this file.


Run it yourself!
================================================================================
First make the output directory and then run the script:
::

    $ mkdir output
    $ mpirun -np 4 python as_run.py

.. centered::
    :ref:`aerostruct_overview` | :ref:`intro`
