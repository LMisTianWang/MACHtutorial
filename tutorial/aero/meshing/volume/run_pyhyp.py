from pyhyp import pyHyp

# pyHyp options (begin)
options= {

    # ---------------------------
    #        Input File
    # ---------------------------
    'inputFile':'wing.cgns',
    'fileType':'cgns',
    'unattachedEdgesAreSymmetry':True,
	'outerFaceBC':'farfield',
 	'autoConnect':'True',
    'BC':{},
    'families':'wall',
    # ---------------------------
    #        Grid Parameters
    # ---------------------------
    'N': 100,
    's0':1e-5,
	'marchDist':20.0*20,
    # ---------------------------
    #   Pseudo Grid Parameters
    # ---------------------------
    'ps0':-1,
    'pGridRatio':-1,
    'cMax': 10.0,

    # ---------------------------
    #   Smoothing parameters
    # ---------------------------
    'epsE': 2.0,
    'epsI': 4.0,
    'theta': 2.0,
    'volCoef': .2,
    'volBlend': 0.0005,
    'volSmoothIter': 20,

    # ---------------------------
    #   Solution Parameters
    # ---------------------------
    'kspRelTol': 1e-10,
    'kspMaxIts': 1500,
    'kspSubspaceSize':50
    }
# pyHyp options (end)

hyp = pyHyp(options=options)
hyp.run()
hyp.writeCGNS('cgns_utils/wing_mvol.cgns')
