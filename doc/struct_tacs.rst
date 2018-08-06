
.. centered::
   :ref:`struct_load` | :ref:`intro`

.. _struct_tacs:

*****************************
Structural analysis with TACS
*****************************

Introduction
================================================================================
We now have a structural mesh and a set of loads that we want to apply to the structure.
How do we actually run the simulation and obtain the desired output information (stresses, deflections, etc.)?

Files
================================================================================
Navigate to the directory ``struct/analysis`` in your tutorial folder.
Copy the following files from the MACHtutorial repository:
::

    $ cp ../geometry/wingbox.bdf .
    $ cp ../loading/forces.txt .

Create the following empty runscript in the current directory:

- ``struct_run.py``

Dissecting the TACS runscript
================================================================================
Instantiate TACS
----------------
All that is necessary to initialize TACS is a bdf file.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 14-19

Set up design variables
-----------------------
Even though we are not optimizing the structure here, we need to set up design variable groups so that we can specify the thickness of each element.
The element properties are added by way of the ``conCallBack`` function, which creates a constitutive object for each design variable group.
The following code creates 18 rib dvgroups, 18 spar dvgroups, 54 stringer groups, and 18 skin dvgroups.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 24-72

The ``conCallBack`` function has a specific signature that must be followed in order for pyTACS to call it correctly.
The material properties as well as the element thickness can be specified uniformally for all elements (as done here), or individually based on the ``compDescripts`` and ``userDescript`` keywords.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 77-95

Add functions
-------------
The user can create output functions for different groupings of the components using the ``include`` keyword argument.
Some of the available functions include ``StructuralMass``, ``AverageKSFailure``, and ``MaxFailure``.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 100-121

Set up load case
----------------
Just like the aerodynamic flow conditions are set in the AeroProblem, the load case for the structure is set in the StructProblem.
For this case, we have a ``loadFile`` exported from ADflow for a 2.5g maneuver.
Since we want the inertial loads of the structure to match the aerodynamic loading,
we specify a ``loadFactor`` of 2.5.
We can also specify the default functions that will be evaluated with a call to ``FEASolver.evalFunctions``.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 126-127

We can also create loads within TACS to add to the structural problem.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 132-140

Solving and computing functions
-------------------------------
The system of governing equations is solved for a given structural problem by calling ``FEASolver(sp)``.
The desired functions are obtained by calling ``FEASolver.evalFunctions``.

.. literalinclude:: ../tutorial/struct/analysis/struct_run.py
    :linenos:
    :lines: 145-152

Run it yourself!
================================================================================
::

    $ mpirun -np 4 python struct_run.py

.. centered::
    :ref:`struct_load` | :ref:`intro`
