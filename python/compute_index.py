#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import matplotlib as mpl
#changing the default backend to agg to resolve contouring issue on rhea
mpl.use('Agg')

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import numpy
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
from get_index_filename import get_index_filename
from optparse import OptionParser
import argparse

def compute_index   (archive_dir,
               indir,
               casename,
               field_name,
               interp_grid,
               interp_method,
               begin_yr,
               end_yr,
               begin_month,
               end_month,
               reg,
               index_name,
               aggregate,
               no_ann,
               stdize,
               write_netcdf,
               debug = False):

    print(__name__, 'casename: ', casename)
    print(__name__, 'reg: ', reg)
    area_seasonal_avg, n_months_season, units = get_reg_seasonal_avg (
                              indir     = archive_dir,
                              casename     = casename,
                              field_name     = field_name,
                              interp_grid     = interp_grid,
                              interp_method = interp_method,
                              begin_yr     = begin_yr,
                              end_yr     = end_yr,
                              begin_month     = begin_month,
                              end_month     = end_month,
                              reg         = reg,
                              aggregate     = aggregate,
                              debug     = debug)


    index = area_seasonal_avg

    if aggregate == 0 and no_ann == 1:
        area_seasonal_avg_no_ann = remove_seasonal_cycle_monthly_data(index, n_months_season, debug = debug)
        index = area_seasonal_avg_no_ann

    if stdize == 1:
        area_seasonal_avg_stddize = standardize_time_series(index)
        index = area_seasonal_avg_stddize
        units = 'unitless'

    nt = index.shape[0]

    time = numpy.arange(0,nt)

    season = get_season_name(begin_month, end_month)

    index_name = index_name

    #Writing netcdf file

    if write_netcdf == 1:
        outfile = get_index_filename (      indir         = indir,
                          casename      = casename,
                          index_name    = index_name,
                          field_name    = field_name,
                          interp_grid   = interp_grid,
                          interp_method = interp_method,
                          begin_yr      = begin_yr,
                          end_yr        = end_yr,
                          begin_month   = begin_month,
                          end_month     = end_month,
                          aggregate     = aggregate,
                          no_ann    = no_ann,
                          stdize    = stdize,
                          debug         = debug)


        print("Writing ", outfile)
        print("")

        f_write = Dataset(outfile, 'w', format = 'NETCDF4')

        time_dim_outfile = f_write.createDimension('time', None)

        field_outfile = f_write.createVariable('index', 'f4', ('time'))
        field_outfile.setncattr('long_name', index_name + ' index')
        field_outfile.setncattr('units', units)

        field_outfile[:] = index

        time_outfile = f_write.createVariable('time', 'f4', ('time'))
        time_outfile.setncattr('long_name', 'time')

        time_outfile[:] = time

    return index, units


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python %prog [options]")

    parser.add_argument("-d", "--debug", dest = "debug", default = False,
            help = "debug option to print some data")

    parser.add_argument("--archive_dir", dest = "archive_dir",
                        help = "filepath to directory model data")

    parser.add_argument("--indir", dest = "indir",
                        help = "filepath to scratch directory")

    parser.add_argument("-c", "--casename", dest = "casename",
                        help = "casename of the run")

    parser.add_argument("-f", "--field_name", dest = "field_name",
                        help = "variable name")

    parser.add_argument("--interp_grid", dest = "interp_grid",
                        help = "variable name")

    parser.add_argument("--interp_method", dest = "interp_method",
                        help = "method used for interpolating the test case e.g. conservative_mapping")

    parser.add_argument("--begin_yr", dest = "begin_yr", type = int,
                        help = "begin year")

    parser.add_argument("--end_yr", dest = "end_yr", type = int,
                        help = "end year")

    parser.add_argument("--begin_month", dest = "begin_month", type = int,
                        help = "begin_month", default = 0)

    parser.add_argument("--end_month", dest = "end_month", type = int,
                        help = "end_month", default = 11)

    parser.add_argument("--reg", dest = "reg",
                        help = "region to be analyzed/plotted")

    parser.add_argument("--index_name", dest = "index_name",
                        help = "name of the index set for naming plot files")

    parser.add_argument("--aggregate", dest = "aggregate", type = int,
                        help = "end_month", default = 1)

    parser.add_argument("--no_ann", dest = "no_ann", type = int,
            help = "flag (0/1) to remove annual cycle, default is off (0)", default = 0)

    parser.add_argument("--stdize", dest = "stdize", type = int,
            help = "flag (0/1) to standardize index, default is off (0)", default = 0)

    parser.add_argument("--write_netcdf", dest = "write_netcdf", type = int,
            help = "flag (0/1) to write netcdf file of the index, default is on (1)", default = 1)

    args = parser.parse_args()

    debug              = args.debug
    archive_dir        = args.archive_dir
    indir              = args.indir
    casename           = args.casename
    field_name         = args.field_name
    interp_grid        = args.interp_grid
    interp_method      = args.interp_method
    begin_yr           = args.begin_yr
    end_yr             = args.end_yr
    begin_month        = args.begin_month
    end_month          = args.end_month
    reg                = args.reg
    index_name         = args.index_name
    aggregate          = args.aggregate
    no_ann             = args.no_ann
    stdize             = args.stdize
    write_netcdf       = args.write_netcdf

    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    compute_index(archive_dir = archive_dir,
                  indir = indir,
                  casename = casename,
                  field_name = field_name,
                  interp_grid = interp_grid,
                  interp_method = interp_method,
                  begin_yr = begin_yr,
                  end_yr = end_yr,
                  begin_month = begin_month,
                  end_month = end_month,
                  reg = reg,
                  index_name = index_name,
                  aggregate = aggregate,
                  no_ann = no_ann,
                  stdize = stdize,
                  write_netcdf = write_netcdf,
                  debug = debug)
