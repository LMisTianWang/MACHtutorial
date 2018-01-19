# Import the librabry
from __future__ import division
import numpy

# You define a box around the wing. Use the the wing root and tip positions + epsilon. Be careful, the wing need to be totally inside.
x_root_range = [-0. , 5.5]
y_root_range = [-2.5, 2.5]
z_root = -1.0E-3

x_tip_range = [ 6.0 , 8.0]
y_tip_range = [-2.0 , 2.0]
z_tip = 12.5

# Now you define the number of controls points on the box. Here we define a 6x8 grid on the wing upper face and lower face.
nX = 6
nY = 2
nZ = 8

# Name of the file
filename = "FFD.fmt"
f = open(filename, 'w')
f.write('\t\t1\n')
f.write('\t\t%d\t\t%d\t\t%d\n' % (nX, nY, nZ))

# Sinusoidal weighting (tighter spacing at wingtip)
# Creat vector: from 0 to pi/2, of dimension nZ.
linear_dist = numpy.linspace(0, numpy.pi/2, nZ)
section_dist = numpy.sin(linear_dist)
z_sections = section_dist*(z_tip - z_root) + z_root
x_te = section_dist*(x_tip_range[0] - x_root_range[0]) + x_root_range[0]
x_le = section_dist*(x_tip_range[1] - x_root_range[1]) + x_root_range[1]
# vstack take a sequence of arrays and stack them vertically to make a single array
y_coords = numpy.vstack((section_dist*(y_tip_range[0] - y_root_range[0]) + y_root_range[0], section_dist*(y_tip_range[1] - y_root_range[1]) + y_root_range[1]))
# initialize the matrix for X,Y,Z
X = numpy.zeros((nY*nZ, nX))
Y = numpy.zeros((nY*nZ, nX))
Z = numpy.zeros((nY*nZ, nX))

    # Fill up the matrix: we define the coordinates of each controls point.
row = 0
for k in range(nZ):
	for j in range(nY):
		X[row,:] = numpy.linspace(x_te[k], x_le[k], nX)
		Y[row,:] = numpy.ones(nX)*y_coords[j,k]
		Z[row,:] = numpy.ones(nX)*z_sections[k]
		row += 1

for set in [X,Y,Z]:
	for row in set:
		vals = tuple(row)
		f.write('\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\n' % vals)

f.close()
