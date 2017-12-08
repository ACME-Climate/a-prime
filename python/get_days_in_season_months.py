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
from get_season_months_index import get_season_months_index

def get_days_in_season_months(begin_month, end_month):
    days_in_month = numpy.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

    index_months, n_months_season = get_season_months_index(begin_month, end_month)

    days_season_months = days_in_month[index_months]

    return days_season_months
