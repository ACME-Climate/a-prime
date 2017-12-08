#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from scipy import stats
import numpy

def regress_index_field(index, field, lag = 0):
    nlon = field.shape[2]
    nlat = field.shape[1]
    nt = field.shape[0]

    regr_matrix   = numpy.ma.zeros((nlat, nlon))
    const_matrix  = numpy.ma.zeros((nlat, nlon))
    corr_matrix   = numpy.ma.zeros((nlat, nlon))
    p_val_matrix  = numpy.ma.zeros((nlat, nlon))
    t_test_matrix = numpy.ma.zeros((nlat, nlon))
    stderr_matrix = numpy.ma.zeros((nlat, nlon))

    print(__name__, 'type(field): ', type(field))

    if numpy.ma.is_masked(field):
        regr_matrix.mask = field.mask[0, ::]
        const_matrix.mask = field.mask[0, ::]
        corr_matrix.mask = field.mask[0, ::]
        p_val_matrix.mask = field.mask[0, ::]
        t_test_matrix.mask = field.mask[0, ::]
        stderr_matrix.mask = field.mask[0, ::]

        print(__name__, 'field.mask: ', field.mask)
        print(__name__, 'field.mask.shape: ', field.mask.shape)
        print(__name__, 'regr_matrix.mask: ', regr_matrix.mask)


    for i in range(0, nlon):
        for j in range (0, nlat):
            if lag < 0:
                regr_matrix[j, i], const_matrix[j, i], corr_matrix[j, i], \
                p_val_matrix[j, i], stderr_matrix[j, i] = stats.mstats.linregress(index[abs(lag):nt], field[0:nt-abs(lag), j, i])
            else:
                regr_matrix[j, i], const_matrix[j, i], corr_matrix[j, i], \
                p_val_matrix[j, i], stderr_matrix[j, i] = stats.mstats.linregress(index[0:nt-lag], field[abs(lag):nt, j, i])



    t_test_matrix[numpy.where(p_val_matrix < 0.05)] = 1


    print(__name__, 'type(regr_matrix): ', type(regr_matrix))
    print(__name__, 'regr_matrix: ', regr_matrix)

    return regr_matrix, const_matrix, corr_matrix, t_test_matrix, stderr_matrix


