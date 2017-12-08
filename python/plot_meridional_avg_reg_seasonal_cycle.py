#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
#Not ready yet (07/18/2017: Salil)

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
from get_reg_meridional_avg_climo import get_reg_meridional_avg_climo
from optparse import OptionParser
import argparse


def plot_meridional_avg_reg_seasonal_cycle(indir,
               casename,
               field_name,
               interp_grid,
               interp_method,
               ref_case_dir,
               ref_case,
               ref_interp_grid,
               ref_interp_method,
               begin_yr,
               end_yr,
               begin_month,
               end_month,
               aggregate,
               reg,
               reg_name,
               debug = False):


    print(__name__, 'casename: ', casename)

    for month in range(0, 11):
        meridional_avg, lon_reg, units = get_reg_meridional_avg_climo (
                                  indir     = indir,
                                  casename     = casename,
                                  field_name     = field_name,
                                  interp_grid     = interp_grid,
                                  interp_method = interp_method,
                                  begin_yr     = begin_yr,
                                  end_yr     = end_yr,
                                  begin_month     = month,
                                  end_month     = month,
                                  reg         = reg,
                                  debug     = debug)

        meridional_avg_all_months[:, month] = meridional_avg

    if ref_case == 'CERES-EBAF':
        if field_name == 'FLNT': field_name_ref = 'FLUT'
        if field_name == 'RESTOM': field_name_ref = 'RESTOA'
        if field_name == 'FSNT': field_name_ref = 'FSNTOA'

    elif ref_case == 'HadISST':
        if field_name == 'TS': field_name_ref = 'SST'

    else:
        field_name_ref = field_name

    for month in range(0, 11):
        ref_meridional_avg, lon_reg, ref_units = get_reg_meridional_avg_climo (
                                indir = ref_case_dir,
                                casename = ref_case,
                                field_name = field_name_ref,
                                interp_grid = ref_interp_grid,
                                interp_method = ref_interp_method,
                                begin_yr = begin_yr,
                                end_yr = end_yr,
                                begin_month = begin_month,
                                end_month = end_month,
                                reg = reg,
                                debug = debug)

        ref_meridional_avg_all_months[:, month] = ref_meridional_avg


    if debug:
        print(__name__, 'ref_plot_field.shape ', ref_plot_field.shape)

    if debug:
        print(__name__, 'plot_field: ', plot_field)

    season = get_season_name(begin_month, end_month)

    plot_field_mean = numpy.mean(plot_field, axis = 0)
    ref_plot_field_mean = numpy.mean(ref_plot_field, axis = 0)

    nlon = lon_reg.shape[0]

    f = plt.subplots(2, 1, figsize=(8.5, 11))

    plt.suptitle(reg_name + ' Meridional Avg. ' + season, fontsize = 20)

    f.text(0.5, 0.04, 'Longitude (E)', ha='center', fontsize = 16)
    f.text(0.04, 0.5, 'Month', va='center', rotation='vertical', fontsize = 16)

    n_stddev = 4
    n_levels = 11

    levels = compute_contour_levels(ref_meridional_avg_all_months, n_stddev, n_levels)

    for k in [0, 1]:
        if k == 0:
            plot_case = casename
            plot_field = meridional_avg_all_months
        if k == 1:
            plot_case = ref_case
            plot_field = ref_meridional_avg_all_months

        ax[k].axis([lon_reg[0],lon_reg[-1], 0, 11])
        ax[k].set_title(plot_case, fontsize = 12)

        x, y = np.meshgrid(lon_reg, np.arange(1, 12))
        c = contourf(x, y, plot_field, cmap = 'seismic', levels = levels, extend = 'both')

        cb = plt.colorbar(c)

        text_data = 'min = '  + str(round(numpy.ma.min(plot_field), 2)) + ', ' + \
                    'max = '  + str(round(numpy.ma.max(plot_field), 2))

        ax[k].text(0.0, -0.15, text_data, transform = ax[k].transAxes, fontsize = 10)


        ax[k].get_yaxis().get_major_formatter().set_useOffset(False)
        ax[k].yaxis.set_major_locator(MaxNLocator(12))

        for tick in ax[k].yaxis.get_major_ticks():
                tick.label.set_fontsize(10)
        for tick in ax[k].xaxis.get_major_ticks():
                tick.label.set_fontsize(10)


    mpl.rcParams['savefig.dpi']=300

    outfile = plots_dir + '/' + casename + '-' + ref_case + '_' + field_name \
           + '_meridional_avg_seasonal_cycle_' + reg + '.png'

    plt.savefig(outfile)
    #plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python %prog [options]")

    parser.add_argument("-d", "--debug", dest = "debug", default = False,
            help = "debug option to print some data")

    parser.add_argument("--indir", dest = "indir",
                        help = "filepath to directory model data")

    parser.add_argument("-c", "--casename", dest = "casename",
                        help = "casename of the run")

    parser.add_argument("-f", "--field_name", dest = "field_name",
                        help = "variable name")

    parser.add_argument("--interp_grid", dest = "interp_grid",
                        help = "variable name")

    parser.add_argument("--interp_method", dest = "interp_method",
                        help = "method used for interpolating the test case e.g. conservative_mapping")

    parser.add_argument("--ref_case_dir", dest = "ref_case_dir",
                        help = "filepath to ref_case directory")

    parser.add_argument("--ref_case", dest = "ref_case",
                        help = "reference casename")

    parser.add_argument("--ref_interp_grid", dest = "ref_interp_grid",
                        help = "name of the interpolated grid of reference case")

    parser.add_argument("--ref_interp_method", dest = "ref_interp_method",
                        help = "method used for interpolating the reference case e.g. conservative_mapping")

    parser.add_argument("--begin_yr", dest = "begin_yr", type = int,
                        help = "begin year")

    parser.add_argument("--end_yr", dest = "end_yr", type = int,
                        help = "end year")

    parser.add_argument("--begin_month", dest = "begin_month", type = int,
                        help = "begin_month", default = 0)

    parser.add_argument("--end_month", dest = "end_month", type = int,
                        help = "end_month", default = 11)

    parser.add_argument("--aggregate", dest = "aggregate", type = int,
                        help = "end_month", default = 1)

    parser.add_argument("--reg", dest = "reg",
                        help = "regions to be analyzed/plotted")

    parser.add_argument("--reg_name", dest = "reg_name",
                        help = "names of regions to be placed in plots")

    parser.add_argument("--plots_dir", dest = "plots_dir",
                        help = "filepath to GPCP directory")

    args = parser.parse_args()

    debug               = args.debug
    indir               = args.indir
    casename            = args.casename
    field_name          = args.field_name
    interp_grid         = args.interp_grid
    interp_method       = args.interp_method
    ref_case_dir        = args.ref_case_dir
    ref_case            = args.ref_case
    ref_interp_grid     = args.ref_interp_grid
    ref_interp_method   = args.ref_interp_method
    begin_yr            = args.begin_yr
    end_yr              = args.end_yr
    begin_month         = args.begin_month
    end_month           = args.end_month
    aggregate           = args.aggregate
    reg                 = args.reg
    reg_name            = args.reg_name
    plots_dir           = args.plots_dir


    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_meridional_avg_climo(indir = indir,
                              casename = casename,
                              field_name = field_name,
                              interp_grid = interp_grid,
                              interp_method = interp_method,
                              ref_case_dir = ref_case_dir,
                              ref_case = ref_case,
                              ref_interp_grid = ref_interp_grid,
                              ref_interp_method = ref_interp_method,
                              begin_yr = begin_yr,
                              end_yr = end_yr,
                              begin_month = begin_month,
                              end_month = end_month,
                              reg = reg,
                              reg_name = reg_name,
                              aggregate = aggregate,
                              debug = debug)
