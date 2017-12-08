#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
from __future__ import absolute_import, division, print_function, \
    unicode_literals
from get_season_name import get_season_name


def get_index_filename (indir,
              casename,
              index_name,
              field_name,
              interp_grid,
              interp_method,
              begin_yr,
              end_yr,
              begin_month,
              end_month,
              aggregate,
              no_ann,
              stdize,
              debug):

    season = get_season_name(begin_month, end_month)


    season_text = season

    if aggregate == 1:
        season_text = season + '_aggregated'

    if no_ann == 1:
        season_text = season + '_no_anncyc'

    if stdize == 1:
        season_text = season + '_stdized'

    if interp_grid == '0':
        outfile = indir + '/'+ casename + '_' + season_text + '.' + \
                    index_name + '_' + field_name + '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'
    else:
        outfile = indir + '/'+ casename + '_' + season_text + '.' + \
                    interp_grid + '_' + interp_method + '.' + \
                    index_name + '_' + field_name + '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'


    return outfile

