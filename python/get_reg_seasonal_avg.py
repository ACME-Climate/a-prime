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
from netCDF4 import Dataset

from read_monthly_data_ts import read_monthly_data_ts
from get_season_months_index import get_season_months_index
from get_days_in_season_months import get_days_in_season_months
from get_reg_area_avg import get_reg_area_avg
from aggregate_ts_weighted import aggregate_ts_weighted

def get_reg_seasonal_avg (indir,
              casename,
              field_name,
                  interp_grid,
              interp_method,
              begin_yr,
              end_yr,
              begin_month,
                end_month,
              reg,
              aggregate,
              debug = False):


    field, lat_reg, lon_reg, area_reg, units_out = read_monthly_data_ts(indir = indir,
                 casename = casename,
                 field_name = field_name,
                 interp_grid = interp_grid,
                 interp_method = interp_method,
                 begin_yr = begin_yr,
                 end_yr = end_yr,
                 begin_month = begin_month,
                 end_month = end_month,
                 reg = reg,
                 debug = debug)


    area_average = get_reg_area_avg(field = field,
                    lat = lat_reg,
                    lon = lon_reg,
                    area_wgts = area_reg,
                    debug = debug)

    a, n_months_season = get_season_months_index(begin_month, end_month)

    day_wgts = get_days_in_season_months(begin_month, end_month)
    if debug:
        print(__name__, 'day_wgts: ', day_wgts)

    if aggregate == 1:
        area_seasonal_avg = aggregate_ts_weighted(ts = area_average,
                              bw = n_months_season,
                              wgts = day_wgts,
                              debug = debug)

        return area_seasonal_avg, n_months_season, units_out
    else:
        return area_average, n_months_season, units_out
