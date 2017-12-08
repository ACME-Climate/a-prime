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

def get_season_months_index(begin_month, end_month):

    if end_month < begin_month:
            n_months_season_yr1 = 12 - begin_month
            n_months_season_yr2 = end_month + 1
            n_months_season = n_months_season_yr1 + n_months_season_yr2

            index_months = numpy.zeros(n_months_season, dtype = numpy.int)
            index_months[0:n_months_season_yr1] = numpy.arange(begin_month,12)
            index_months[n_months_season_yr1:n_months_season] = numpy.arange(0, end_month+1)

    else:
            n_months_season = end_month - begin_month + 1
            index_months = numpy.arange(begin_month, end_month+1)


    return (index_months, n_months_season)
