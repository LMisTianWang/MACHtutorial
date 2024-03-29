.. _intro:

#############
MACH Tutorial
#############

Introduction
================================================================================
The `MDOlab <http://mdolab.engin.umich.edu>`_ at the University of Michigan has developed the MDO of Aircraft Configurations with High-fidelity (MACH) framework).
This tutorial was written to help new users become familiar with the tools and workflow of MACH and the common practices of more experienced users.
Most of the tools in the MACH framework are written with Python, although many of the tools incorporate Fortran code to handle operations that require speed.
The user does not need to know Fortran to complete this tutorial, but if Python is not your strong suit, we recommend a refresher with one of the many online Python tutorials.
Be forewarned that ignorance of Python will be cured by any lengthy interaction with the MDOlab. :)

This tutorial starts from scratch and leads the user through the steps necessary to conduct aerostructural optimization of a B717 wing.
The tutorial files are located on `GitHub <https://github.com/mdolab/MACHtutorial/>`_.
The scripts referenced in the tutorial can be found in the tutorial directory, organized according to section.
Although these scripts should be executable without any modifications, **we highly recommend that you create a separate directory and type out the lines of code by yourself.**
As you do this, ask yourself, "Do I understand why the code is written this way?"
This will result in a much deeper understanding of how to use the tools and eventually will help you develop code in a consistent manner.
To make this easier for you, we provide a basic script that will create the directory structure in your desired location so that all you have to do is create the files themselves.
To run this script, go to the MACHtutorial root folder and run the following:
::

    python make_tutorial_directory.py my_tutorial

where ``my_tutorial`` is the name of the folder in which you will build your scripts.
The directory structures for each section of the tutorial, including all files, are displayed at the beginning of each section.
Throughout the tutorial, we will refer to the location of your developing tutorial as ``my_tutorial``, so if you chose a different name make sure to adjust your commands accordingly.

Before continuing with the tutorial, make sure that the MDOLab framework is already installed on your machine.
If you set up your machine using an MDOLab iso, then the required packages should already be installed.
If not, follow the instructions for installing the MDOLab framework from `scratch <http://mdolab.engin.umich.edu/docs/installInstructions/installFromScratch.html>`_.

Table of Contents
================================================================================

.. toctree::
   :maxdepth: 2
   :titlesonly:

   aero_overview
   struct_overview
   aerostruct_overview
   opt_overview
   airfoilopt_overview
   overset_overview

Required Software
================================================================================

Made in the MDOlab
------------------
* `ADflow <https://github.com/mdolab/adflow>`_
* `pyGeo <https://github.com/mdolab/pygeo>`_
* `pySpline <https://github.com/mdolab/pyspline>`_
* `pyHyp <https://github.com/mdolab/pyhyp>`_
* `IDWarp <https://github.com/mdolab/idwarp>`_
* `pyLayout <https://github.com/mdolab/pylayout>`_
* `TACS <https://github.com/mdolab/tacs_orig>`_
* `pyOptSparse <https://github.com/mdolab/pyoptsparse>`_
* `cgnsUtilities <https://github.com/mdolab/cgnsutilities>`_
* `baseclasses <https://github.com/mdolab/baseclasses>`_
* `pyAeroStructure <https://github.com/mdolab/pyaerostructure>`_
* `multipoint <https://github.com/mdolab/multipoint.git>`_

Note: These links take you to the GitHub repositories.
To see their documentation instead, go back to the main documentation `page <http://mdolab.engin.umich.edu/docs/index.html>`_.

External Software
-----------------
* ICEM CFD
* Tecplot (for visualization)

Documentation strategy
================================================================================
The tutorial resides on `GitHub <https://github.com/mdolab/MACHtutorial/>`_, but it is a living tutorial, which means that it is constantly updated with corrections and improvements.
We invite you, especially as a new user, to take notes of the parts that you find confusing and bring them to the attention of an admin to the tutorial repository so that changes can be made.

The rst files in the doc directory contain direct links to the python scripts in the tutorial directory to avoid code duplication.
This is done using the ``start-after`` and ``end-before`` options of Sphinx's native ``literalinclude`` directive.
We adopt the convention of using ``#rst <section subject>`` as the marker for the start and end of each ``literalinclude`` section, like so:
::

    #rst Simple addition (begin)
    a = 2
    b = 3
    c = a + b
    #rst Simple addition (end)

Please adopt this same convention for any future developments to the tutorial.

Future Work
================================================================================
Add explanation of pyOptSparse and OptView.
