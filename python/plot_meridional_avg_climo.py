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
from matplotlib.ticker import MaxNLocator, LinearLocator, FixedLocator

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
from round_to_first import round_to_first
from optparse import OptionParser
import argparse


def plot_meridional_avg_climo (indir,
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
    meridional_avg, lon_reg, units = get_reg_meridional_avg_climo (
                              indir     = indir,
                              casename     = casename,
                              field_name     = field_name,
                              interp_grid     = interp_grid,
                              interp_method = interp_method,
                              begin_yr     = begin_yr,
                              end_yr     = end_yr,
                              begin_month     = begin_month,
                              end_month     = end_month,
                              reg         = reg,
                              debug     = debug)

    plot_field =  meridional_avg

    if ref_case == 'CERES-EBAF':
        if field_name == 'FLNT': field_name_ref = 'FLUT'
        if field_name == 'RESTOM': field_name_ref = 'RESTOA'
        if field_name == 'FSNT': field_name_ref = 'FSNTOA'

    elif ref_case == 'HadISST':
        if field_name == 'TS': field_name_ref = 'SST'

    else:
        field_name_ref = field_name

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


    ref_plot_field = ref_meridional_avg

    if debug:
        print(__name__, 'ref_plot_field.shape ', ref_plot_field.shape)

    if debug:
        print(__name__, 'plot_field: ', plot_field)

    plot_field_mean = numpy.mean(plot_field, axis = 0)
    ref_plot_field_mean = numpy.mean(ref_plot_field, axis = 0)

    nlon = lon_reg.shape[0]

    f = plt.figure(figsize=(11, 8.5))
    f.text(0.5, 0.04, 'Longitude (E)', ha='center', fontsize = 16)
    f.text(0.04, 0.5, field_name + ' (' + units + ')', va='center', rotation='vertical', fontsize = 16)

    ax = f.add_subplot(111)

    season = get_season_name(begin_month, end_month)
    plt.suptitle(reg_name + ' Meridional Avg. ' + season, fontsize = 20)


    ref_case_text = ref_case + ' ' + field_name_ref + ' climo'

    #min_plot = min(numpy.amin(plot_field), numpy.amin(ref_plot_field))
    #max_plot = max(numpy.amax(plot_field), numpy.amax(ref_plot_field))
    min_plot = numpy.amin(ref_plot_field)
    max_plot = numpy.amax(ref_plot_field)

    y_axis_ll = round_to_first(min_plot - 0.5*numpy.std(ref_plot_field))
    y_axis_ul = round_to_first(max_plot + 0.5*numpy.std(ref_plot_field))

    levels   = numpy.linspace(y_axis_ll, y_axis_ul, num = 5)

    ax.axis([lon_reg[0],lon_reg[-1], y_axis_ll, y_axis_ul])

    print('lon_reg[0],lon_reg[-1], 1.1*min_plot, 1.1*max_plot: ',
          lon_reg[0],lon_reg[-1], 1.1*min_plot, 1.1*max_plot)

    print('lon_reg.shape, plot_field.shape, ref_plot_field.shape: ',
          lon_reg.shape, plot_field.shape, ref_plot_field.shape)

    test_line, = ax.plot(lon_reg, plot_field, color = 'green', linewidth = 2.0, label = casename)
    ref_line, = ax.plot(lon_reg, ref_plot_field, color = 'black', linewidth = 2.0, label = ref_case)

    ax.legend(bbox_to_anchor = (1.0,1.0), handles=[ref_line, test_line], fontsize = 10)

    ax.set_title(field_name, fontsize = 12)

    #ax.get_yaxis().get_major_formatter().set_useOffset(False)
    print(__name__, 'levels:', levels)
    ax.yaxis.set_major_locator(FixedLocator(levels))

    for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(10)
    for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(10)


    mpl.rcParams['savefig.dpi']=300

    outfile = plots_dir + '/' + casename + '-' + ref_case + '_' + field_name \
           + '_meridional_avg_' + reg + '_' + season + '.png'

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
