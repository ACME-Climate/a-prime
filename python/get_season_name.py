#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from get_season_months_index import get_season_months_index

def get_season_name(begin_month, end_month):


    initials = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    month_no = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    month_index, n_months = get_season_months_index(begin_month, end_month)


    if n_months == 1:
        season_name = month_no[month_index]

    else:
        season_name = ''

        for i in month_index:
            season_name = season_name + initials[i]

        if begin_month == 0 and end_month == 11:
            season_name = 'ANN'

    print('season_name: ', season_name)
    return season_name
