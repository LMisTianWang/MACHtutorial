import argparse
import numpy
from pygeo import *
from pyspline import *
from pylayout import *

surfFile = 'wing.igs'
geo = pyGeo('iges', fileName=surfFile)
layoutGeo = pyLayoutGeo.LayoutGeo(geo, h=.15, rightWing=True, prefix='WING')
eSize = 0.2
surf = 'y'
layoutGeo.addDomain(surf, offset=5)



leRoot   =  numpy.array([0.00, 0.00,  0.00])
leBreak  =  numpy.array([2.28, 0.43,  4.60])
leTip    =  numpy.array([6.24, 1.16, 12.43])

rootChord  =5.41
breakChord =3.13
tipChord   =1.29


lep0 = leRoot    + [0.10*rootChord  , 0.00, 0.00]
lep1 = leBreak   + [0.10*breakChord , 0.00, 0.00]
lep2 = leTip     + [0.35*tipChord   , 0.00, 0.00]


tep0 = leRoot    + [0.60*rootChord  , 0.00, 0.00]
tep1 = leBreak   + [0.60*breakChord , 0.00, 0.00]
tep2 = leTip     + [0.60*tipChord   , 0.00, 0.00]

layoutGeo.addComponent('spar', [ lep0, lep1, lep2], tag='le_spar', elemSize=eSize, nSeg=10)
layoutGeo.addComponent('spar', [ tep0, tep1, tep2], tag='te_spar', elemSize=eSize, nSeg=10)

xaxis = numpy.array([1.0, 0., 0.])

basePt = lep0
i=0
print "base point i=%d coord:" %(i)
print basePt
layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis,bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)

N = 4
for i in range(1,N-1):	
	basePt = lep0 + (float(i)/(N-1))*(lep1 - lep0)
	print "base point i=%d coord:" %(i)
	print basePt
	layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis, bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)    


basePt = lep1
print "base point i=%d coord:" %(N-1)
print basePt

layoutGeo.addComponent('rib', basePt=basePt, bidirectional=True, direction=xaxis, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize,leRib=False)
 
N = 10
for i in range(1,N-1):	
	basePt = lep1 + (float(i)/(N-1))*(lep2 - lep1)
	print "base point i=%d coord:" %(i)
	print basePt
	layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis, bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'], elemSize=eSize, leRib=False)
 
 
basePt = lep2
print "base point tip coord:"
print basePt
layoutGeo.addComponent('rib', basePt=basePt, direction=xaxis,bidirectional=True, clipLower=['le_spar'], clipUpper=['te_spar'],elemSize=eSize, leRib=False)

layoutGeo.addSkins(elemSize=eSize)

layoutGeo.writeTinFile('wing_box.tin')
