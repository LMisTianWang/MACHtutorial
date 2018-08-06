
.. centered::
   :ref:`struct_overview` | :ref:`struct_mesh`

.. _struct_geo:

****************
Wingbox Geometry
****************

Introduction
================================================================================
The purpose of pyLayout is to generate a surface representation of a conventional wingbox geometry that conforms to the shape and size of the desired wing.
This surface representation can then be meshed in pyLayout or in ICEM, depending on preference and the complexity of the wingbox structure.

Files
================================================================================
Navigate to the directory ``aero/geometry`` in your tutorial folder.
Copy the following files from the MACHtutorial repository:
::

    $ cp ~/hg/machtutorial/tutorial/aero/geometry/wing.igs .

Create the following empty runscript in the current directory:

- ``generate_wingbox.py``

Dissecting the pyLayout script
================================================================================
To begin, we need to import a few modules.

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :lines: 1-6

The bulk of the script is devoted to creating data to initialize the creation of the wingbox geometry.
It will make more sense if we start at the end of the script to see what we need to provide.

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :linenos:
    :lines: 76-

The first parameter required to initialize pyLayout is a pyGeo object.
The pyGeo object provides a surface representation of the wing outer mold line (OML) which will be used to ensure that the wingbox fits the wing.

Wingbox Layout
--------------
The rest of the information provided to pyLayout determine the placement of the ribs, spars, and stringers within the wing OML.
Conveniently, the conventional wingbox is basically arranged like a grid, with ribs intersecting spars and stringers at basically perpendicular junctions.
These intersections between ribs, spars, and stringers are provided to pyLayout in the ``X`` parameter, which is a 3D array of shape ncols x nrows x 3.
The columns (of ncols) are aligned with the ribs, whereas the rows (of nrows) are aligned with the spars and stringers.
The upper and lower skins conform to the wing OML and cover the extent of the rib/spar structure.

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :linenos:
    :lines: 50-74


With no further information given, pyLayout would create a grid structure with ribs at every column and spars along every row.
We can blank out certain rows and columns to remove ribs, spars, and stringers using the blanking arrays.
These arrays contain a 1 if the structure should be created a certain location in the grid or a 0 if not.
For example, the ``ribBlank`` array:

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :linenos:
    :lines: 29-31

This array contains a 1 for every cell of the grid except those in the first column, which tells pyLayout not to place a rib at the wing root.
The other blanking arrays stipulate spars only on the first and last row, and stringers on every other row.

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :linenos:
    :lines: 33-48

Mesh Refinement
---------------
The number of elements created from this surface representation is determined by the ``ribSpace``, ``spanSpace``, ``vSpace``, ``stringerSpace``, and ``ribStiffenerSpace`` parameters.
These parameters dictate how many elements should be created from each cell of the ``X`` matrix along each of the topological axes.
The stringer height parameters can be used to control the maximum and minimum heights of the stringers.

.. literalinclude:: ../tutorial/struct/geometry/generate_wingbox.py
    :linenos:
    :lines: 19-24

File output
-----------
pyLayout can output bdf files and tecplot files for easy visualization

Run it yourself!
================================================================================
::

    $ python generate_wingbox.py

.. centered::
    :ref:`struct_overview` | :ref:`struct_mesh`
