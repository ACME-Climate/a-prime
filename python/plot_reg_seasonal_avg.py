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

import numpy
from netCDF4 import Dataset

from read_monthly_data_ts import read_monthly_data_ts
from get_season_months_index import get_season_months_index
from get_days_in_season_months import get_days_in_season_months
from get_reg_area_avg import get_reg_area_avg
from aggregate_ts_weighted import aggregate_ts_weighted
from get_reg_seasonal_avg import get_reg_seasonal_avg

from optparse import OptionParser


def plot_reg_seasonal_avg (casename,
               field_name,
               interp_grid,
               begin_yr,
               end_yr,
               begin_month,
               end_month,
               reg,
               aggregate,
               debug = False):

    area_seasonal_avg = get_reg_seasonal_avg (casename = casename,
                  field_name = field_name,
                  interp_grid = interp_grid,
                  begin_yr = begin_yr,
                  end_yr = end_yr,
                  begin_month = begin_month,
                  end_month = end_month,
                  reg = reg,
                  aggregate = aggregate,
                  debug = debug)

    print(__name__, 'area_seasonal_avg.shape', area_seasonal_avg.shape)

    #plt.subplot(3,1,1)

    plt.plot(area_seasonal_avg)

    #mpl.rcParams['savefig.dpi']=300
    plt.show()


if __name__ == "__main__":
    parser = OptionParser(usage = "python %prog [options]")

    parser.add_option("-d", "--debug", dest = "debug", default = False,
            help = "debug option to print some data")

    parser.add_option("-c", "--casename", dest = "casename",
                        help = "casename of the run")

    parser.add_option("-f", "--field_name", dest = "field_name",
                        help = "variable name")

    parser.add_option("--begin_yr", dest = "begin_yr", type = "int",
                        help = "begin year")

    parser.add_option("--end_yr", dest = "end_yr", type = "int",
                        help = "end year")

    parser.add_option("--begin_month", dest = "begin_month", type = "int",
                        help = "begin_month", default = 0)

    parser.add_option("--end_month", dest = "end_month", type = "int",
                        help = "end_month", default = 11)

    parser.add_option("--reg", dest = "reg", type = "string",
                        help = "world region for analysis", default = "global")


    (options, args) = parser.parse_args()

    debug        = options.debug
    casename    = options.casename
    field_name  = options.field_name
    begin_yr    = options.begin_yr
    end_yr      = options.end_yr
    begin_month = options.begin_month
    end_month   = options.end_month
    reg         = options.reg

    plot_reg_seasonal_avg (casename = casename,
                               field_name = field_name,
                   interp_grid = interp_grid,
                               begin_yr = begin_yr,
                               end_yr = end_yr,
                               begin_month = begin_month,
                               end_month = end_month,
                               reg = reg,
                               debug = debug)
