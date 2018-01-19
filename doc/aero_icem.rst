
.. centered::
    :ref:`aero_pygeo` | :ref:`aero_pyhyp`

.. _aero_icem:

***************
Surface Meshing
***************

Introduction
================================================================================
The objective of this section is to familiarize the user with the ICEM CFD software and to create a surface mesh.
ICEM CFD is a meshing software with advanced CAD/geometry readers and repairs tools.
It allows the user to produce volume or surface meshes.
At times ICEM may test your patience, however, it offers a lot of functionality and is quite handy once you get to know its quirks.

.. warning:: Make sure you save your work often when using ICEM. It is known to crash at the worst possible moments. We also recommend saving instances of a single project in different locations just in case you need to go back to a previous state.

Files
================================================================================
Navigate to the directory ``aero/meshing/surface`` in your tutorial folder.
Copy the following files from the the ``geometry`` directory:
::

    $ cp ../../geometry/wing.tin .

Basic ICEM Usage
================================================================================
This section contains some general usage information that will helpful in becoming familiar with ICEM.
The actual tutorial starts with :ref:`surface_meshing`.

Opening ICEM
------------
First determine where the ICEM executable is located
::

    $ which icemcfd
    /usr/ansys_inc/v150/icemcfd/linux64_amd/bin/icemcfd

Then run the executable with superuser privileges
::

    $ sudo /usr/ansys_inc/v150/icemcfd/linux64_amd/bin/icemcfd

File Types
----------
ICEM uses several native file types with the following extensions:

.prj
    Project file. Contains references to the geometry and blocking files of the same name.

.tin
    Geometry file. Contains a geometry definition made up of points, lines, and surfaces.

.blk
    Blocking file. Contains the definition of the geometry and parameters used to generate the mesh.

Navigating in ICEM
------------------
To adjust your view of the geometry in ICEM the following functions are possible with the mouse:

- Hold down left button while dragging mouse: Rotate the view in 3D space
- Hold down middle button while dragging mouse: Translate view in viewing plane
- Scroll middle button: Slow zoom in/out
- Hold down right button
    - Drag mouse up/down: Fast zoom
    - Drag mouse left/right: Rotate view in viewing plane

Changing the appearance of the geometry
---------------------------------------
.. image:: images/icem_AppearanceButtons.png
   :scale: 80

The two buttons outlined in red can be used to view the geometry as a wire frame (left button) or a collection of opaque surfaces (right button).

.. _surface_meshing:

Creating a surface mesh
================================================================================

Load the geometry
-----------------
In ICEM, select ``File`` → ``Geometry`` → ``Open Geometry``.

Navigate to the surface meshing folder and open ``wing.tin``.

ICEM will prompt you to create a project called ``wing.prj``. Select Yes.

Rename Parts
------------
You will see in the model tree that there are 5 different parts with arbitrary names.
We want to redefine a single part that contains all wing geometry and call it WING.

.. image:: images/icem_ModelTree1.png
   :scale: 80

Right-click on ``Parts`` in the model tree and select ``Create Part``.
The options for creating a new part will appear in the lower left-hand pane as shown below.
Change the name from "PART.1" to "WING".
We want to create the "WING" part by selecting objects in the viewing pane.
To do this, select the arrow to the left of the ``Entities`` box (outlined in red) and then drag a box (with the left mouse button) over all the wing surfaces in the viewing pane.
All of the selected geometry should become highlighted.
Now click the center mouse button to verify the operation.
All of the selected components should become the same color, and a new part called "WING" should appear in the model tree under ``Parts``.
To refresh the model tree, deselect and then reselect the checkbox next to the "WING" part.
This should make all of the other parts go away.

.. image:: images/icem_CreatePart.png
   :scale: 80

Auxiliary Geometry
------------------
Before actually creating the mesh, it is helpful to create some additional geometric features to use as references for the mesh.
All geometry creation and manipulation is done under the ``Geometry`` tab, outlined in red in the image below.

.. image:: images/icem_TabGeometry.png
   :scale: 80

1. Extract curves from surfaces. (or repair geometry)

    You will notice that the geometry section of the model tree contains only Subsets and Surfaces.
    We want to see the curves and points that define the boundaries of these surfaces.
    This can be done with the

2. Create guide curves for leading edge

    The mesh block that covers the leading edge region of the wing will extend...
    First create points at 2% of the upper and lower surfaces of the wing at the root and at the tip.

Blocking
--------

1. Create 3D blocking with bounding box

    The best way to create the blocking is to first create a 3-D bounding box and to then convert that blocking from 3-D to 2-D.
    This approach is preferred as it helps ICEM understand the topology, often preventing future issues.

    To do this, under the ``Blocking`` tab, select the first icon, ``Create Block`` shown here:

    .. image:: images/icem_BlockingMenu.png
        :scale: 80

    This opens a menu in the lower left corner of the window.
    With the default options, click the button next to the input box for the entities (if it was not automatically selected).
    This button allows you to select the entities you want to create a blocking for from the CAD model.
    Directions for selecting entities are found in red text at the bottom of the CAD window.
    To create a bounding box around the entire wing, select all of the wing entities.

    .. image:: images/icem_CreateBlock.png
        :scale: 80

2. Convert 3D blocking to 2D blocking

    Now the 3-D bounding box needs to be converted to a 2-D blocking (as we only want a surface mesh output from ICEM).
    To do this, select the fifth icon in the ``Create Block`` menu (shown below).

    .. image:: images/CreateBlockIcons.png

    After selecting the fifth icon, select OK or Apply at the bottom of the Create Block menu.
    If the conversion was successful, in the dialog box there will be a message reading "...Blocking successfully converted to 2D..."

    Remove block on symmetry plane.

3. Associate blocking to geometry

4. Create Pre-Mesh

5. Define edge properties

6. Split and adjust edges

7. Check mesh quality

8. Ensure correct block orientation

9. Convert to MultiBlock Mesh

10. Export the mesh

.. centered::
    :ref:`aero_pygeo` | :ref:`aero_pyhyp`
