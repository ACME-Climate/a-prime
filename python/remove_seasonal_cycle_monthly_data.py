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

def remove_seasonal_cycle_monthly_data(field, n_months_season = 12, debug = False):

    ntime = field.shape[0]
    field_noann = field + numpy.nan

    nyrs = ntime // n_months_season
    yrs = numpy.arange(0, nyrs)

    if debug: print(__name__, 'ntime, nyrs, yrs, field.ndim: ', ntime, nyrs,
                    yrs, field.ndim)

    if field.ndim == 1:
        for i in range(0, n_months_season):
            field_mean_temp = numpy.ma.mean(field[n_months_season*yrs + i])
            field_noann[n_months_season*yrs + i] = field[n_months_season*yrs + i] - field_mean_temp
    else:
        for i in range(0, n_months_season):
            field_mean_temp = numpy.ma.mean(field[n_months_season*yrs + i, ::], axis = 0)
            field_noann[n_months_season*yrs + i, ::] = field[n_months_season*yrs + i, ::] - field_mean_temp

    if debug: print(__name__, 'field_noann: ', field_noann)

    return field_noann

