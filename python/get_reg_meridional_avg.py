#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import numpy

def get_reg_meridional_avg(field, area_wgts, debug = False):

    #The following should work for both 2 dimensions as well as 3 dimensions
    #since model variables are stored as (time, lat, lon) or (lat, lon) in netcdf files,
    #lat is the second axis from the end (-2)

    meridional_avg = numpy.sum(field * area_wgts, axis = -2)/numpy.sum(area_wgts, axis = -2)

    print(__name__, 'meridional_avg.shape: ', meridional_avg.shape)
    if debug:
        print(__name__, 'area weighted meridional avg.: ', meridional_avg)

    return meridional_avg
