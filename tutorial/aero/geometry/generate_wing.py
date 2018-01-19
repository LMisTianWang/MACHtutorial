#rst0: Imports
import numpy
from pygeo import pyGeo
#rst1: Imports

#rst0: Airfoil file
airfoil_list = ['rae2822.dat'] * 2
naf = len(airfoil_list) # number of airfoils
#rst1: Airfoil file

#rst0: Wing definition
# Airfoil leading edge positions
x = [0.0, 7.5 ]
y = [0.0, 0.0 ]
z = [0.0, 14.0]
offset = numpy.zeros((naf,2)) # x-y offset applied to airfoil position before scaling

# Airfoil rotations
rot_x = [0.,0.,0.]
rot_y = [0.,0.,0.]
rot_z = [0.,0.,0.]

# Airfoil scaling
chord = [5.0, 1.5] # chord lengths
#rst1: Wing definition

#rst0: Run pyGeo
wing = pyGeo('liftingSurface', xsections=airfoil_list, scale=chord, offset=offset,
    x=x, y=y, z=z, rotX=rot_x, rotY=rot_y, rotZ=rot_z, tip='rounded', bluntTe=True,
    squareTeTip=True, teHeight=0.25*.0254)
#rst1: Run pyGeo

#rst0: Write output files
wing.writeTecplot('wing.dat')
wing.writeIGES('wing.igs')
wing.writeTin('wing.tin')
#rst1: Write output files
