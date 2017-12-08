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

def get_reg_area_avg(field, lat, lon, area_wgts, debug = False):
    nlon = lon.shape[0]
    nlat = lat.shape[0]
    if field.ndim == 2:
        nt = 1
    else:
        nt   = field.shape[0]

    if debug:
        print(__name__, 'nlon, nlat: ', nlon, nlat)


    area_average = numpy.zeros(nt)

    if field.ndim == 2:
        area_average[0] = numpy.sum(field[:, :] * area_wgts[:, :])/numpy.sum(area_wgts)
    else:
        for i in range(0,nt):
            area_average[i] = numpy.sum(field[i, :, :] * area_wgts[:, :])/numpy.sum(area_wgts)

    print(__name__, 'area_average.shape: ', area_average.shape)
    if debug:
        print(__name__, 'area weights: ', area_wgts)
    if debug:
        print(__name__, 'area weighted total_field: ', area_average)



    return area_average
