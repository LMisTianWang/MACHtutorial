cgns_utils symmzero wing_mvol.cgns z wing_mvol0.cgns
cgns_utils coarsen wing_mvol0.cgns wing_mvol1.cgns
cgns_utils coarsen wing_mvol1.cgns ../ADflow/wing_mvol2.cgns
