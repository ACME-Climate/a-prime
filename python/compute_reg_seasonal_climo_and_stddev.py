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
from aggregate_time_series_data import aggregate_time_series_data

def compute_reg_seasonal_climo_and_stddev(indir,
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


    a, n_months_season = get_season_months_index(begin_month, end_month)

    day_wgts = get_days_in_season_months(begin_month, end_month)
    if debug:
        print(__name__, 'day_wgts: ', day_wgts)

    seasonal_avg_ts = aggregate_time_series_data(    data = field,
                              aggregate_size = n_months_season,
                              wgts = day_wgts,
                              debug = debug)

    seasonal_avg_ts_mean   = seasonal_avg_ts.mean(axis = 0)
    seasonal_avg_ts_stddev = seasonal_avg_ts.std(axis = 0)

    return seasonal_avg_ts_mean, seasonal_avg_ts_stddev, lat_reg, lon_reg, units_out
