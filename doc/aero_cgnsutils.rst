

.. centered::
    :ref:`aero_pyhyp` | :ref:`aero_adflow`

.. _aero_cgnsutils:

***********************
Mesh Manipulation Tools
***********************

Content
=======


Process
=======
Open the file TUTORIAL/AERO/CGNS/coarsen.sh.

::
  cgns_utils symmzero wing_mvol.cgns z wing_mvol0.cgns
  cgns_utils coarsen wing_mvol0.cgns wing_mvol1.cgns
  cgns_utils coarsen wing_mvol1.cgns ../ADflow/wing_mvol2.cgns

There are three steps in the file:
# Define the symetric plan ("symmzero").
# Coarse the mesh one time ("coarsen").
# Coarse the mesh one time ("coarsen").

Run the coarsen.sh file with the command "bash":
::
	$ bash coarsen.sh

.. centered::
    :ref:`aero_pyhyp` | :ref:`aero_adflow`
