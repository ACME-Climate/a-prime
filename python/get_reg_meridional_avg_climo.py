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
from netCDF4             import Dataset

from get_season_name           import get_season_name
from read_monthly_data_ts     import read_monthly_data_ts
from get_season_months_index     import get_season_months_index
from get_days_in_season_months     import get_days_in_season_months
from get_reg_area_avg         import get_reg_area_avg
from aggregate_ts_weighted     import aggregate_ts_weighted
from read_climo_file        import read_climo_file
from get_reg_meridional_avg    import get_reg_meridional_avg

def get_reg_meridional_avg_climo (      indir,
              casename,
              field_name,
                  interp_grid,
              interp_method,
              begin_yr,
              end_yr,
              begin_month,
              end_month,
              reg,
              debug = False):

    season = get_season_name(begin_month, end_month)

    field, lat_reg, lon_reg, area_reg, units_out = read_climo_file(     indir = indir,
                                     casename = casename,
                                     field_name = field_name,
                                     season = season,
                                     begin_yr = begin_yr,
                                     end_yr = end_yr,
                                     interp_grid = interp_grid,
                                     interp_method = interp_method,
                                     reg = reg,
                                     debug = debug)


    meridional_avg = get_reg_meridional_avg(field = field,
                        area_wgts = area_reg,
                        debug = True)

    a, n_months_season = get_season_months_index(begin_month, end_month)

    return meridional_avg, lon_reg, units_out
