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
from get_index_filename import get_index_filename
from netCDF4 import Dataset

def read_index_file (      indir,
              casename,
              index_name,
              field_name,
              interp_grid,
              interp_method,
              begin_yr,
              end_yr,
              begin_month,
              end_month,
              no_ann,
              aggregate,
              stdize,
              debug):

    file_name = get_index_filename (      indir         = indir,
                                          casename      = casename,
                                          index_name    = index_name,
                                          field_name    = field_name,
                                          interp_grid   = interp_grid,
                                          interp_method = interp_method,
                                          begin_yr      = begin_yr,
                                          end_yr        = end_yr,
                                          begin_month   = begin_month,
                                          end_month     = end_month,
                                          no_ann        = no_ann,
                                          aggregate     = aggregate,
                                          stdize        = stdize,
                                          debug         = debug)

    print(__name__, 'file_name: ', file_name)

    #try:
    f = Dataset(file_name, "r")
    field = f.variables['index']

    units = field.units

    field_in = field[:]
    print(field.shape)
    print(field_in.shape)

    #except:

    #    print
    #        print(file_name, 'not found! Exiting'
    #    quit()


    return field_in, units


