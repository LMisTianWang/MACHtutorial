
.. centered::
   :ref:`intro` | :ref:`overset_geom`

.. _overset_overview:

#####################################################
Part 6: Analysis and Optimization with Overset Meshes
#####################################################


Overview
================================================================================
In this part of the tutorial, we will look at a tandem-wing case to learn how to generate overset meshes and carry out aerodynamic optimizations with multiple surfaces and FFDs.

.. image:: images/overset_cp.png
   :scale: 25

Here are a few of the items we will cover in the following pages:

    - Generate geometry and multiple volume meshes for a tandem-wing case

    - Generate a background mesh and combine the meshes

    - Check the overset mesh

    - Run an aerodynamic analysis

    - Generate FFD grids

    - Run an aerodynamic optimization

Table of Contents
================================================================================

.. toctree::
   :maxdepth: 1

   overset_geom
   overset_volume_meshes
   overset_ihcc
   overset_analysis
   overset_ffds
   overset_opt

Directory Structure
================================================================================
::

    oversetopt
    |-- geometry
    |   |-- generate_wing.py
    |   |-- NACA642A015.dat
    |   |-- wing.dat
    |   |-- wing.tin
    |-- mesh
    |   |-- surface
    |       |-- wing.cgns
    |       |-- icem_proj_files
    |   |-- volume
    |       |-- wing.cgns
    |       |-- run_pyhyp.py
    |       |-- wing_vol_front.cgns
    |       |-- wing_vol_back.cgns
    |       |-- wing_vol_front_c.cgns
    |       |-- wing_vol_back_c.cgns
    |       |-- wing_vol_back_c_t.cgns
    |       |-- wing_vols_combined.cgns
    |       |-- generate_overset.py
    |       |-- overset_combined.cgns
    |-- ihc_check
    |   |-- ihc_check.py
    |   |-- overset_combined.cgns
    |-- analysis
    |   |-- aero_tandem.py
    |   |-- overset_combined.cgns
    |-- ffd
    |   |-- tandem_ffds.py
    |   |-- ffd_front_wing.xyz
    |   |-- ffd_back_wing.xyz
    |   |-- ffd_global.xyz
    |-- opt
    |   |-- aero_opt_tandem.py
    |   |-- overset_combined.cgns
    |   |-- ffd_front_wing.xyz
    |   |-- ffd_back_wing.xyz
    |   |-- ffd_global.xyz

.. centered::
    :ref:`intro` | :ref:`overset_geom`
