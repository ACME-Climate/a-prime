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
from scipy import stats
from netCDF4 import Dataset

from read_monthly_data_ts import read_monthly_data_ts
from get_season_months_index import get_season_months_index
from get_days_in_season_months import get_days_in_season_months
from get_reg_area_avg import get_reg_area_avg
from aggregate_ts_weighted import aggregate_ts_weighted
from get_reg_seasonal_avg import get_reg_seasonal_avg
from get_season_name import get_season_name
from get_reg_avg_climo import get_reg_avg_climo
from remove_seasonal_cycle_monthly_data import remove_seasonal_cycle_monthly_data
from standardize_time_series import standardize_time_series
from regress_index_field import regress_index_field
from aggregate_time_series_data import aggregate_time_series_data

def get_regress_index_index (indir,
               casename,
               field_name,
               interp_grid,
               interp_method,
               begin_yr,
               end_yr,
               begin_month,
               end_month,
               aggregate,
               lag,
               reg,
               reg_name,
               no_ann,
               stdize,
               debug = False):


    print(__name__, 'casename: ', casename)

    index, n_months_season, units_index = get_reg_seasonal_avg (
                              indir         = indir[1],
                              casename      = casename[1],
                              field_name    = field_name[1],
                              interp_grid   = interp_grid[1],
                              interp_method = interp_method[1],
                              begin_yr      = begin_yr,
                              end_yr        = end_yr,
                              begin_month   = begin_month[1],
                              end_month     = end_month[1],
                              reg           = reg[1],
                              aggregate     = aggregate,
                              debug         = debug)


    if aggregate == 0 and no_ann == 1:
        index_no_ann = remove_seasonal_cycle_monthly_data(index, n_months_season, debug = debug)
        index = index_no_ann

    if stdize == 1:
        index_stddize = standardize_time_series(index)
        index = index_stddize

    field, n_months_season, units_field = get_reg_seasonal_avg (
                              indir         = indir[0],
                              casename      = casename[0],
                              field_name    = field_name[0],
                              interp_grid   = interp_grid[0],
                              interp_method = interp_method[0],
                              begin_yr      = begin_yr,
                              end_yr        = end_yr,
                              begin_month   = begin_month[0],
                              end_month     = end_month[0],
                              reg           = reg[0],
                              aggregate     = aggregate,
                              debug         = debug)



    if aggregate == 0 and no_ann == 1:
        field_no_ann = remove_seasonal_cycle_monthly_data(field, n_months_season, debug = debug)
        field = field_no_ann

    if aggregate == 1:

        day_wgts = get_days_in_season_months(begin_month[0], end_month[0])
        if debug:
            print(__name__, 'day_wgts: ', day_wgts)

        field_seasonal_avg = aggregate_time_series_data(field, n_months_season, day_wgts)

        field = field_seasonal_avg


    regr_coef, intercept, r_value, p_value, std_err = stats.linregress(index, field)

    units = units_field + '/' + units_index

    if stdize == 1:
        units = units_out

    return regr_coef, intercept, r_value, p_value, std_err, field, index, units_field, units_index, units

