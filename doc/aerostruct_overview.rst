
.. centered::
    :ref:`intro` | :ref:`setup_structure`

.. _aerostruct_overview:

###############################
Part 3: Aerostructural Analysis
###############################

Overview
================================================================================
The aerostructural analysis scripts in MACH use both the aerodynamics and structures
modules. 
Therefore, it is assumed that you have completed both the aerodynamics and structures
single discipline tutorial prior to completing this multidisciplinary tutorial.
There are three main sections to this tutorial.
We start with a brief review of the structural setup procedure. 
Unlike in the structural analysis tutorial, we split the structural setup out into a separate
file and include the relevant commands though an "exec" call. 
The remaining two sections contain aerostructual analysis examples.
The first is setup with the aerodynamic and structural analyses setup on separate processor groups,
while the second example shows the setup for having the aerodynamic and structural analysis stacked on the same set
of processors.
Currently, our best practice is to follow the second example, where the aerodynamic and structural analyses are stacked on the same processors.
This tends to make it easier to load balance the problem.


Table of Contents
================================================================================

.. toctree::
   :maxdepth: 1

   setup_structure
   aerostruct_analysis_split
   aerostruct_analysis
   

Directory Structure
================================================================================
::

    aerostruct
    |-- as_run.py
    |-- as_run_nosplit.py
    |-- setup_structure.py
    

.. centered::
    :ref:`intro` | :ref:`setup_structure`
