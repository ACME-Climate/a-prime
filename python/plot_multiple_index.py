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
from optparse import OptionParser
import argparse

def plot_multiple_index   (indir,
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
                           ref_begin_yr,
                           ref_end_yr,
               begin_month,
               end_month,
               regs,
               names,
               index_set_name,
               aggregate,
               no_ann,
               stdize,
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

        if i == 0: test_plot_ts = numpy.zeros((2*n_reg, area_seasonal_avg.shape[0]))

        test_plot_ts[i, :] = area_seasonal_avg

        if aggregate == 0 and no_ann == 1:
            area_seasonal_avg_no_ann = remove_seasonal_cycle_monthly_data(test_plot_ts[i, :], n_months_season, debug = debug)
            test_plot_ts[i, :] = area_seasonal_avg_no_ann

        if stdize == 1:
            area_seasonal_avg_stddize = standardize_time_series(test_plot_ts[i, :])
            test_plot_ts[i, :] = area_seasonal_avg_stddize


        if debug:
            print(__name__, 'test_plot_ts: ', test_plot_ts)


    for i,reg in enumerate(regs):
        print(__name__, 'casename: ', casename)
        area_seasonal_avg, n_months_season, units = get_reg_seasonal_avg (
                                  indir     = ref_case_dir,
                                  casename     = ref_case,
                                  field_name     = field_name,
                                  interp_grid     = ref_interp_grid,
                                  interp_method = ref_interp_method,
                                  begin_yr     = ref_begin_yr,
                                  end_yr     = ref_end_yr,
                                  begin_month     = begin_month,
                                  end_month     = end_month,
                                  reg         = reg,
                                  aggregate     = aggregate,
                                  debug     = debug)


        if i == 0: ref_plot_ts = numpy.zeros((n_reg, area_seasonal_avg.shape[0]))
        ref_plot_ts[i, :] = area_seasonal_avg

        if aggregate == 0 and no_ann == 1:
            area_seasonal_avg_no_ann = remove_seasonal_cycle_monthly_data(ref_plot_ts[i, :], n_months_season, debug = debug)
            ref_plot_ts[i, :] = area_seasonal_avg_no_ann

        if stdize == 1:
            area_seasonal_avg_stddize = standardize_time_series(ref_plot_ts[i, :])
            ref_plot_ts[i, :] = area_seasonal_avg_stddize


        if debug:
            print(__name__, 'test_plot_ts: ', test_plot_ts)


    f, ax = plt.subplots(n_reg, 2, figsize=(11,8.5))

    f.text(0.04, 0.5, field_name + ' (' + units + ')', va='center', rotation='vertical', fontsize = 14)

    season = get_season_name(begin_month, end_month)
    plt.suptitle('Monthly ' + index_set_name + ' index', fontsize = 20)



    for k in [0, 1]:
        if k == 0:
            plot_case = casename
            plot_ts = test_plot_ts
            plot_begin_yr = begin_yr

        if k == 1:
            plot_case = ref_case
            plot_ts = ref_plot_ts
            plot_begin_yr = ref_begin_yr


        nt = plot_ts.shape[1]

        if aggregate == 1:
            plot_time = numpy.arange(0,nt) + plot_begin_yr
        else:
            plot_time = numpy.arange(0,nt)

        if debug:
            print(__name__, 'plot_time: ', plot_time)
        if debug:
            print(__name__, 'plot_begin_yr: ', plot_begin_yr)

        plot_ts_mean   = numpy.mean(plot_ts, axis = 1)
        plot_ts_stddev = numpy.std(plot_ts, axis = 1)

        for i,name in enumerate(names):
            min_plot = numpy.amin(ref_plot_ts[i, :])
            max_plot = numpy.amax(ref_plot_ts[i, :])

            y_axis_ll = min_plot - 0.5*numpy.std(ref_plot_ts[i, :])
            y_axis_ul = max_plot + 0.5 * numpy.std(ref_plot_ts[i,:])

            ax[i, k].axis([plot_time[0],plot_time[-1], y_axis_ll, y_axis_ul])

            print('plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot: ',
                  plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot)

            mean_line_plot = numpy.zeros(nt) + plot_ts_mean[i]
            mean_line, = ax[i, k].plot(plot_time, mean_line_plot, color = 'black', linewidth = 1.0, label = 'Mean')

            if begin_month == 0 and end_month == 11 and aggregate == 0:
                bw   = 13
                wgts = numpy.ones(bw) // bw
                nyrs = nt // n_months_season


                plot_ts_moving_avg = numpy.convolve(plot_ts[i, :], wgts, 'valid')

                smooth_line, = ax[i, k].plot(plot_time[bw // 2:-bw // 2+1], plot_ts_moving_avg,
                                color = colors[i],
                                linewidth = 2.0,
                                label = 'Moving avg. (Bandwidth = ' + "%3d" % bw + ' months)')

                index_line, = ax[i, k].plot(plot_time, plot_ts[i, :],
                                color = colors[i],
                                linewidth = 1.0,
                                label = 'Index')

                ax[i, k].set_xticks(numpy.arange(0, nt, 12*5))
                ax[i, k].set_xticklabels(numpy.arange(0, nyrs, 5) + plot_begin_yr)

            else:
                ax[i, k].plot(plot_time, plot_ts[i, :], color = colors[i], linewidth = 4.0)


            if i == 0 and k == 1:
                ax[i, k].legend(bbox_to_anchor = (1.2,1.55),
                         handles=[mean_line, index_line, smooth_line],
                         fontsize = 7)

            if i == 0:
                ax[i, k].text(0.5, 1.15, plot_case, ha='center', \
                        fontsize = 14, transform=ax[i, k].transAxes)

            if i == n_reg-1:
                ax[i, k].text(0.5, -0.3, 'Year', ha='center', \
                        fontsize = 14, transform=ax[i, k].transAxes)

            ax[i, k].set_title(name + ' , mean = ' +  "%.2f" % plot_ts_mean[i]
                    + ' , std. dev. = ' +  "%.2f" % plot_ts_stddev[i], fontsize = 10)

            ax[i, k].get_yaxis().get_major_formatter().set_useOffset(False)
            ax[i, k].yaxis.set_major_locator(MaxNLocator(6))

            if i < n_reg-1:
                ax[i, k].tick_params(labelbottom='off')

            for tick in ax[i, k].yaxis.get_major_ticks():
                    tick.label.set_fontsize(10)
            for tick in ax[i, k].xaxis.get_major_ticks():
                    tick.label.set_fontsize(10)


    plt.subplots_adjust(hspace=0.3)
    plt.subplots_adjust(wspace=0.3)

    mpl.rcParams['savefig.dpi']=300

    outfile = plots_dir + '/' + casename + '_' \
           + field_name + '_' + season + '_' + index_set_name + '.png'

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

    parser.add_argument("--ref_begin_yr", dest = "ref_begin_yr", type = int,
                        help = "reference case begin year")

    parser.add_argument("--ref_end_yr", dest = "ref_end_yr", type = int,
                        help = "reference case end year")

    parser.add_argument("--begin_month", dest = "begin_month", type = int,
                        help = "begin_month", default = 0)

    parser.add_argument("--end_month", dest = "end_month", type = int,
                        help = "end_month", default = 11)

    parser.add_argument("--regs", dest = "regs", nargs = '+',
                        help = "regions to be analyzed/plotted")

    parser.add_argument("--names", dest = "names", nargs = '+',
                        help = "names of regions to be placed in plots")

    parser.add_argument("--index_set_name", dest = "index_set_name",
                        help = "name of the index set for naming plot files")

    parser.add_argument("--aggregate", dest = "aggregate", type = int,
                        help = "end_month", default = 1)

    parser.add_argument("--no_ann", dest = "no_ann", type = int,
            help = "flag (0/1) to remove annual cycle, default is off (0)", default = 0)

    parser.add_argument("--stdize", dest = "stdize", type = int,
            help = "flag (0/1) to standardize index, default is off (0)", default = 0)

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
    ref_begin_yr        = args.ref_begin_yr
    ref_end_yr          = args.ref_end_yr
    regs                = args.regs
    names               = args.names
    index_set_name      = args.index_set_name
    aggregate           = args.aggregate
    no_ann              = args.no_ann
    stdize              = args.stdize
    plots_dir           = args.plots_dir

    #regs = ['global', 'NH_high_lats', 'NH_mid_lats', 'tropics', 'SH_mid_lats', 'SH_high_lats']
    #names = ['Global', '90N-50N', '50N-20N', '20N-20S', '20S-50S', '50S-90S']

    print('salil', regs)
    print('salil', names)

    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_multiple_index(indir = indir,
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
                        ref_begin_yr = ref_begin_yr,
                        ref_end_yr = ref_end_yr,
                        begin_month = begin_month,
                        end_month = end_month,
                        regs = regs,
                        names = names,
                        index_set_name = index_set_name,
                        aggregate = aggregate,
                        no_ann = no_ann,
                        stdize = stdize,
                        debug = debug)
