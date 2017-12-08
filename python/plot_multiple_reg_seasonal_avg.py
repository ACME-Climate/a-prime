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

import math
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
from round_to_first_given_range import round_to_first_given_range
from optparse import OptionParser
import argparse


def plot_multiple_reg_seasonal_avg (indir,
               casename,
               field_name,
               interp_grid,
               interp_method,
               ref_case,
               ref_interp_grid,
               ref_interp_method,
               begin_yr,
               end_yr,
               begin_month,
               end_month,
               regs,
               aggregate,
               debug = False):

    n_reg = len(regs)


    for i,reg in enumerate(regs):
        print(__name__, 'casename: ', casename)
        area_seasonal_avg, n_months_season, units = get_reg_seasonal_avg (
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
                                  aggregate     = aggregate,
                                  debug     = debug)

        if i == 0: plot_ts = numpy.zeros((n_reg, area_seasonal_avg.shape[0]))

        plot_ts[i, :] = area_seasonal_avg

        if ref_case == 'CERES-EBAF':
            if field_name == 'FLNT': field_name_ref = 'FLUT'
            if field_name == 'RESTOM': field_name_ref = 'RESTOA'
            if field_name == 'FSNT': field_name_ref = 'FSNTOA'

        elif ref_case == 'HadISST':
            if field_name == 'TS': field_name_ref = 'SST'

        else:
            field_name_ref = field_name

        ref_area_seasonal_avg, ref_units = get_reg_avg_climo (
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

        if i == 0: ref_plot_ts = numpy.zeros((n_reg, area_seasonal_avg.shape[0]))

        ref_plot_ts[i, :] = numpy.tile(ref_area_seasonal_avg, area_seasonal_avg.shape[0])

        if debug:
            print(__name__, 'ref_plot_ts.shape ', ref_plot_ts.shape)


        if debug:
            print(__name__, 'plot_ts: ', plot_ts)

    plot_ts_mean = numpy.mean(plot_ts, axis = 1)

    print(__name__, 'int(math.ceil(n_reg/2)):', int(math.ceil(n_reg // 2)))

    f, ax = plt.subplots(int(math.ceil(n_reg // 2)), 2, sharex = True, figsize=(8.5,11))

    nt = area_seasonal_avg.shape[0]


    f.text(0.5, 0.04, 'Model Year', ha='center', fontsize = 24)

    f.text(0.04, 0.5, field_name + ' (' + units + ')', va='center', rotation='vertical', fontsize = 16)

    season = get_season_name(begin_month, end_month)
    plt.suptitle(field_name + ' ' + season, fontsize = 24)

    if aggregate == 1:
            plot_time = numpy.arange(0,nt) + begin_yr
    else:
            plot_time = numpy.arange(0,nt)

    ref_case_text = ref_case + ' ' + field_name_ref + ' climo'

    for i,name in enumerate(names):
        j = numpy.unravel_index(i, ax.shape)
        print(__name__, 'i and unraveled index, j: ', i, j)

        min_plot = min(numpy.amin(plot_ts[i, :]), ref_plot_ts[i, 0])
        max_plot = max(numpy.amax(plot_ts[i, :]), ref_plot_ts[i, 0])

        y_axis_ll = min_plot - 0.5*numpy.std(plot_ts[i, :])
        y_axis_ul = max_plot + 0.5 * numpy.std(plot_ts[i,:])

        #plot_range = y_axis_ul_temp - y_axis_ll_temp

        #y_axis_ll = round_to_first_given_range(y_axis_ll_temp, plot_range)
        #y_axis_ul = round_to_first_given_range(y_axis_ul_temp, plot_range)

        ax[j].axis([plot_time[0],plot_time[-1], y_axis_ll, y_axis_ul])

        print('plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot: ',
              plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot)

        if begin_month == 0 and end_month == 11 and aggregate == 0:
            bw   = 13
            wgts = numpy.ones(bw) // bw
            nyrs = nt // n_months_season

            plot_ts_moving_avg = numpy.convolve(plot_ts[i, :], wgts, 'valid')

            ax[j].plot(plot_time[bw // 2:-bw // 2+1], plot_ts_moving_avg, color = colors[i], linewidth = 4.0)
            ax[j].plot(plot_time, plot_ts[i, :], color = colors[i], linewidth = 1.0)
            ax[j].plot(plot_time, ref_plot_ts[i, :], color = 'black', linewidth = 1.0)
            ax[j].set_xticks(numpy.arange(0, nt, 12))
            ax[j].set_xticklabels(numpy.arange(0, nyrs, 1) + begin_yr)
        else:
                ax[j].plot(plot_time, plot_ts[i, :], color = colors[i], linewidth = 4.0)


        ref_line, = ax[j].plot(plot_time, ref_plot_ts[i, :], color = 'green', linewidth = 1.0, label = ref_case_text)
        if i == 0:
            ax[j].legend(loc = 'lower left', bbox_to_anchor = (0.0,1.15), handles=[ref_line], fontsize = 10)

        ax[j].set_title(name + ' , mean = ' +  "%.2f" % plot_ts_mean[i], fontsize = 12)

        ax[j].get_yaxis().get_major_formatter().set_useOffset(False)
        ax[j].yaxis.set_major_locator(MaxNLocator(6))

        for tick in ax[j].yaxis.get_major_ticks():
                tick.label.set_fontsize(10)
        for tick in ax[j].xaxis.get_major_ticks():
                tick.label.set_fontsize(10)


    plt.subplots_adjust(hspace=0.3)

    mpl.rcParams['savefig.dpi']=300

    outfile = plots_dir + '/' + casename + '_' \
           + field_name + '_' + season + '_reg_ts.png'

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

    parser.add_argument("--regs", dest = "regs", nargs = '+',
                        help = "regions to be analyzed/plotted")

    parser.add_argument("--names", dest = "names", nargs = '+',
                        help = "names of regions to be placed in plots")

    parser.add_argument("--aggregate", dest = "aggregate", type = int,
                        help = "end_month", default = 1)

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
    regs                = args.regs
    names               = args.names
    aggregate           = args.aggregate
    plots_dir           = args.plots_dir

    #regs = ['global', 'NH_high_lats', 'NH_mid_lats', 'tropics', 'SH_mid_lats', 'SH_high_lats']
    #names = ['Global', '90N-50N', '50N-20N', '20N-20S', '20S-50S', '50S-90S']

    print('salil', regs)
    print('salil', names)

    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_multiple_reg_seasonal_avg(indir = indir,
                                   casename = casename,
                                   field_name = field_name,
                                   interp_grid = interp_grid,
                                   interp_method = interp_method,
                                   ref_case = ref_case,
                                   ref_interp_grid = ref_interp_grid,
                                   ref_interp_method = ref_interp_method,
                                   begin_yr = begin_yr,
                                   end_yr = end_yr,
                                   begin_month = begin_month,
                                   end_month = end_month,
                                   regs = regs,
                                   aggregate = aggregate,
                                   debug = debug)
