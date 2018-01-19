
.. centered::
   :ref:`Previous: step 2 <Struct_step2>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 4 <Struct_step4>`


.. _Step3-chapt:

***************
Structure setup
***************

Content
=======
In this chapter, we focus on step 3 of the structure analysis process. First, we establish the wing general structure and characteristics. Second, we define the problem of interest by specifying the functions TACS need to evaluate (mass, stress, etc.).

.. blockdiag::
   :align: center

   blockdiag {

   pyBDF.py [shape = ellipse];
   Setup_Struct.py [shape = ellipse];
   pyFoce.py [shape = ellipse];
   ICEM [shape = ellipse];

   "Geometry (PYGEO)" -> pyBDF.py -> Structure -> ICEM -> "Nastran mesh" -> Setup_Struct.py
   "RANS (ADFLOW)" -> pyFoce.py -> Force.txt
   Force.txt ->  Setup_Struct.py

   group {
   color = none;
   label = "Step 1";
   "Geometry (PYGEO)" ,pyBDF.py ,Structure ,ICEM ,"Nastran mesh"
   }

   group {
   color = none;
   label = "Step 2";
   "RANS (ADFLOW)" ,pyFoce.py ,Force.txt
   }

   group {
   color = green;
   label = "Step 3";
   Setup_struct.py
   }

   }

.. centered::
   **Figure 1: step 3, geometry setup**

Open the file TUTORIAL/STRUC/TACS/Setup_Struct.py.

Define the material properties
==============================
For instance, the wing we want to build will be made of the composite metal ALUMINIUM 2024. In order to give this information to TACS, you need to define the following constant:
::
	rho_2024 = 2780
	E_2024 = 73.1e9
	ys_2024 = 324e6
	nu = 0.33
	t= .02
	tMin = 0.0016
	tMax = 0.020
	kcorr = 5.0/6.0

Structure composition
=====================
The structural wing is based of the bdf generated previously in step 1.
::
	bdfFile = 'nastran_input'

The structOptions enables to define some extraneous options such as the gravity vector:
::
	structOptions = {'transferSize':0.5, 'transferGaussOrder':3,'gravityVector':[0, -9.81, 0]}

In order to use TACS a class defining structure need to be build:
::
	FEASolver = pytacs.pyTACS(bdfFile, comm=MPI.COMM_WORLD, options=structOptions)


The wing structure is composed of ribs, strings, spars and skins as you can see in Figure 2.

.. figure:: Pic/Struc/Process/img_p8.png
   :width: 500px
   :align: center
   :height: 300px
   :alt: alternate text
   :figclass: align-center

   **Figure 2: decomposition of the wing structure by elements and groups**

Structural elements are grouped together by calling the function *addDVGroup*. By assigning each component to a design variable (DV) group, it is possible to associate each group some common material properties. It is also helpful for reducing the number of design variable. Thus the size of the structural problem to solve or optimization. On Figure 2 above, each color represents another group instead of using each element as an individual. The wing structure presented in Figure 2 is composed of:

**13 ribs (i=0 to i<13):**
::
	for i in xrange(13):
    		FEASolver.addDVGroup('RIBS', include='RIB.%2.2d'%i)

**2 Spars:** one for the leading edge and one for the trailling edge.
::
	FEASolver.addDVGroup('SPARS', include='LE_SPAR', nGroup=1)
	FEASolver.addDVGroup('SPARS', include='TE_SPAR', nGroup=1)


**12 pieces of skins (i=1 to i=12):** 6 pieces of Skins for the upper part and 6 for the lower part. Each piece of skin is bounded by two ribs, the leading edge spar and the trailing edge spar.
::
	boundLists = [
		['LE_SPAR','TE_SPAR','RIB.02','RIB.04'],
    	['LE_SPAR','TE_SPAR','RIB.04','RIB.06'],
    	['LE_SPAR','TE_SPAR','RIB.06','RIB.08'],
    	['LE_SPAR','TE_SPAR','RIB.08','RIB.10'],
    	['LE_SPAR','TE_SPAR','RIB.10','RIB.12']]

	for bounds in boundLists:
		FEASolver.addDVGroup('U_SKIN', include='U_SKIN', includeBounds=bounds)
		FEASolver.addDVGroup('L_SKIN', include='L_SKIN', includeBounds=bounds)

	# Skins at root are not included...do them here
	u_skins = []
	l_skins = []

	for i in xrange(1,13):
		u_skins.append('U_SKIN/U_SKIN.%3.3d'%(i))
		l_skins.append('L_SKIN/L_SKIN.%3.3d'%(i))

	FEASolver.addDVGroup('U_SKIN', include=u_skins)
	FEASolver.addDVGroup('L_SKIN', include=l_skins)

Conponents properties
=====================
The conCallBack definition function enable to keep track of the components description (names, groups, numbers, ...) added with addDVgroup. The constitutive.isoFSDTStiffness function defines the class associated to the stiffness matrix.
::
	def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):
		con = constitutive.isoFSDTStiffness(rho_2024, E_2024, nu, kcorr, ys_2024, t, dvNum, tMin, tMax)
		return con

TACS Assembler can be created by calling:
::
	FEASolver.createTACSAssembler(conCallBack)

pyTACS calls this function to set a constitutive object for each DV group. Once the assembler is created, DV groups can no longer be edited or added.

Assign TACS functions
=====================

The Mass functions:
::
	FEASolver.addFunction('mass', functions.StructuralMass)
	FEASolver.addFunction('uSkin', functions.StructuralMass, include='U_SKIN')
	FEASolver.addFunction('lSkin', functions.StructuralMass, include='L_SKIN')
	FEASolver.addFunction('leSpar', functions.StructuralMass, include=['LE_SPAR'])
	FEASolver.addFunction('teSpar', functions.StructuralMass, include=['TE_SPAR'])
	FEASolver.addFunction('ribs', functions.StructuralMass, include=['RIBS'])

The KS Failure functions is used to determine if the structure of the wing will fail or not for a 2.5G manoeuvre. Also for this case, the failure functions arer aggregated in order to ensure the safety by a weight.
::
	loadFactor = 2.5
	KSWeight = 80.0

	ks0 = FEASolver.addFunction('ks0', functions.AverageKSFailure, KSWeight=KSWeight,include=['RIBS','SPARS'], loadFactor=loadFactor)
	FEASolver.addFunction('max0',functions.MaxFailure, include=ks0, loadFactor=loadFactor)




.. centered::
   :ref:`Previous: step 2 <Struct_step2>` | :ref:`Summary <SUMMARY>` | :ref:`Next: step 4 <Struct_step4>`
