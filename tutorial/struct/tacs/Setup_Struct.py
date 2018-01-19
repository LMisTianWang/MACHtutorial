rho_2024 = 2780
E_2024 = 73.1e9
ys_2024 = 324e6
nu = 0.33
t= .02
tMin = 0.0016
tMax = 0.020
kcorr = 5.0/6.0

bdfFile = 'nastran_input'

structOptions = {'transferSize':0.5, 'transferGaussOrder':3,'gravityVector':[0, -9.81, 0]}
FEASolver = pytacs.pyTACS(bdfFile, comm=MPI.COMM_WORLD, options=structOptions)


N=13
for i in xrange(N):
	print "RIB.%2.2d" %(i)
	FEASolver.addDVGroup('RIBS', include='RIB.%2.2d'%i)


FEASolver.addDVGroup('SPARS', include='LE_SPAR', nGroup=1)
FEASolver.addDVGroup('SPARS', include='TE_SPAR', nGroup=1)

boundLists = [
['LE_SPAR', 'TE_SPAR','RIB.02','RIB.04'],
['LE_SPAR', 'TE_SPAR','RIB.04','RIB.06'],
['LE_SPAR', 'TE_SPAR','RIB.06','RIB.08'],
['LE_SPAR', 'TE_SPAR','RIB.08','RIB.10'],
['LE_SPAR', 'TE_SPAR','RIB.10','RIB.12']]

for bounds in boundLists:
	FEASolver.addDVGroup('U_SKIN', include='U_SKIN', includeBounds=bounds)
	FEASolver.addDVGroup('L_SKIN', include='L_SKIN', includeBounds=bounds)

u_skins = []
l_skins = []
for i in xrange(1,13):
	u_skins.append('U_SKIN/U_SKIN.%3.3d'%(i))
	l_skins.append('L_SKIN/L_SKIN.%3.3d'%(i))

FEASolver.addDVGroup('U_SKIN', include=u_skins)
FEASolver.addDVGroup('L_SKIN', include=l_skins)

def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):
	con = constitutive.isoFSDTStiffness(rho_2024, E_2024, nu, kcorr, ys_2024, t, dvNum, tMin, tMax)
	return con


FEASolver.createTACSAssembler(conCallBack)


FEASolver.addFunction('mass', functions.StructuralMass)
FEASolver.addFunction('uSkin', functions.StructuralMass, include='U_SKIN')
FEASolver.addFunction('lSkin', functions.StructuralMass, include='L_SKIN')
FEASolver.addFunction('leSpar', functions.StructuralMass, include=['LE_SPAR'])
FEASolver.addFunction('teSpar', functions.StructuralMass, include=['TE_SPAR'])
FEASolver.addFunction('ribs', functions.StructuralMass, include=['RIBS'])


loadFactor = 2.5
KSWeight = 80.0

ks0 = FEASolver.addFunction('ks0', functions.AverageKSFailure, KSWeight=KSWeight,include=['RIBS','SPARS'], loadFactor=loadFactor)
FEASolver.addFunction('max0',functions.MaxFailure, include=ks0, loadFactor=loadFactor)


















