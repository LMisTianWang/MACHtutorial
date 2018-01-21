from __future__ import division
import numpy

x_root_range = [-1.E-001, 5.5]
y_root_range = [-1., 1.]
z_root = -1.0000000000000000E-003

x_tip_range = [6.0, 8]
y_tip_range = [0., 2.]
z_tip = 12.6

nX = 6
nY = 2
nZ = 8

linear_dist = numpy.linspace(0, numpy.pi/2, nZ)
section_dist = numpy.sin(linear_dist)
z_sections = section_dist*(z_tip - z_root) + z_root

x_te = section_dist*(x_tip_range[0] - x_root_range[0]) + x_root_range[0]
x_le = section_dist*(x_tip_range[1] - x_root_range[1]) + x_root_range[1]
#Stack arrays in sequence vertically (row wise).
y_coords = numpy.vstack((section_dist*(y_tip_range[0] - y_root_range[0]) + y_root_range[0], section_dist*(y_tip_range[1] - y_root_range[1]) + y_root_range[1]))

X = numpy.zeros((nY*nZ, nX))
Y = numpy.zeros((nY*nZ, nX))
Z = numpy.zeros((nY*nZ, nX))
row = 0
for k in range(nZ):
	for j in range(nY):
		X[row,:] = numpy.linspace(x_te[k], x_le[k], nX)
		Y[row,:] = numpy.ones(nX)*y_coords[j,k]
		Z[row,:] = numpy.ones(nX)*z_sections[k]
		row += 1

filename = "ffd.fmt"
f = open(filename, 'w')
f.write('\t\t1\n')
f.write('\t\t%d\t\t%d\t\t%d\n' % (nX, nY, nZ))
for set in [X,Y,Z]:
	for row in set:
		vals = tuple(row)
		f.write('\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\t%3.8f\n' % vals)

f.close()

