#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from read_monthly_data_ts_field import read_monthly_data_ts_field
from get_derived_var_expr import get_derived_var_expr

import numpy
from sympy import *


def read_monthly_data_ts(indir,
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


    if field_name == 'RESSURF':

        try:
            field_in, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
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


        except:

            print()
            print(field_name, 'not found! Checking derived variables list '
                  'for ', field_name)

            var_expr, var_expr_numpy = get_derived_var_expr(field_name)

            for i, field_name_temp in enumerate(var_expr.atoms(Symbol)):

                print(field_name_temp)
                field_name_temp_str = str(field_name_temp)
                print(field_name_temp_str)


                field_temp, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
                     casename = casename,
                     field_name = field_name_temp_str,
                     interp_grid = interp_grid,
                     interp_method = interp_method,
                     begin_yr = begin_yr,
                     end_yr = end_yr,
                     begin_month = begin_month,
                     end_month = end_month,
                     reg = reg,
                     debug = debug)

                if i == 0:
                    field_list = [field_temp]
                else:
                    field_list.append(field_temp)

            print()
            print('field_list length: ', len(field_list))

            field_in = var_expr_numpy(*field_list)
            print(__name__, 'field_in.shape: ', field_in.shape)


    elif field_name == 'PRECT':

        try:
            field_in, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
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


        except:
            print()
            print("Could not find file for: ", field_name,
                  " Trying to look for PRECC and PRECL files!")
            print()

            field_PRECC, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
                     casename = casename,
                     field_name = 'PRECC',
                     interp_grid = interp_grid,
                     interp_method = interp_method,
                     begin_yr = begin_yr,
                     end_yr = end_yr,
                     begin_month = begin_month,
                     end_month = end_month,
                     reg = reg,
                     debug = debug)

            field_PRECL, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
                     casename = casename,
                     field_name = 'PRECL',
                     interp_grid = interp_grid,
                     interp_method = interp_method,
                     begin_yr = begin_yr,
                     end_yr = end_yr,
                     begin_month = begin_month,
                     end_month = end_month,
                     reg = reg,
                     debug = debug)

            field_in = field_PRECC + field_PRECL


    elif field_name == 'RESTOM':

        try:
            field_in, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
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


        except:
            print()
            print("Could not find file for: ", field_name,
                  " Trying to look for FSNT and FLNT files!")
            print()

            field_FSNT, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
                 casename = casename,
                             field_name = 'FSNT',
                             interp_grid = interp_grid,
                             interp_method = interp_method,
                             begin_yr = begin_yr,
                             end_yr = end_yr,
                             begin_month = begin_month,
                             end_month = end_month,
                             reg = reg,
                             debug = debug)

            field_FLNT, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
                 casename = casename,
                             field_name = 'FLNT',
                             interp_grid = interp_grid,
                             interp_method = interp_method,
                             begin_yr = begin_yr,
                             end_yr = end_yr,
                             begin_month = begin_month,
                             end_month = end_month,
                             reg = reg,
                             debug = debug)

        field_in = field_FSNT - field_FLNT     #positive downwards

    else:

        field_in, lat, lon, area, units = read_monthly_data_ts_field(indir = indir,
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

    return (field_in, lat, lon, area, units)
