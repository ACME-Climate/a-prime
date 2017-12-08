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
from read_index_file import read_index_file
from optparse import OptionParser
import argparse


def plot_multiple_index_same_plot   (indir,
               casename,
               field_names,
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
               index_names,
               aggregate,
               no_ann,
               stdize,
               debug = False):

    n_index = len(index_names)

    for i,index_name in enumerate(index_names):
        print(__name__, 'casename: ', casename)
        index_temp, units = read_index_file (
                                  indir     = indir[i],
                                  casename     = casename[i],
                                  field_name     = field_names[i],
                                  index_name    = index_names[i],
                                  interp_grid     = interp_grid[i],
                                  interp_method = interp_method[i],
                                  begin_yr     = begin_yr,
                                  end_yr     = end_yr,
                                  begin_month     = begin_month,
                                  end_month     = end_month,
                                  aggregate     = aggregate[i],
                                  no_ann    = no_ann[i],
                                  stdize    = stdize[i],
                                  debug     = debug)

        if i == 0: test_plot_ts = numpy.zeros((n_index, index_temp.shape[0]))

        test_plot_ts[i, :] = index_temp


        if debug: print(__name__, 'test_plot_ts: ', test_plot_ts)

    test_corr_matrix = numpy.corrcoef(test_plot_ts)

    for i,index_name in enumerate(index_names):
        print(__name__, 'casename: ', casename)
        index_temp, units = read_index_file (
                              indir     = ref_case_dir[i],
                              casename     = ref_case[i],
                              field_name     = field_names[i],
                              index_name    = index_names[i],
                              interp_grid     = ref_interp_grid[i],
                              interp_method = ref_interp_method[i],
                              begin_yr     = ref_begin_yr,
                              end_yr     = ref_end_yr,
                              begin_month     = begin_month,
                              end_month     = end_month,
                              aggregate     = aggregate[i],
                              no_ann    = no_ann[i],
                              stdize    = stdize[i],
                              debug     = debug)


        if i == 0: ref_plot_ts = numpy.zeros((n_index, index_temp.shape[0]))
        ref_plot_ts[i, :] = index_temp


        if debug: print(__name__, 'ref_plot_ts: ', ref_plot_ts)

    ref_corr_matrix = numpy.corrcoef(ref_plot_ts)

    f, ax = plt.subplots(n_index, 2, figsize=(11,8.5))


    season = get_season_name(begin_month, end_month)
    z, n_months_season = get_season_months_index(begin_month, end_month)

    plt.suptitle('Monthly Indices', fontsize = 20)



    for k in [0, 1]:
        if k == 0:
            plot_case = casename
            plot_ts = test_plot_ts
            plot_begin_yr = begin_yr
            corr_matrix = test_corr_matrix

        if k == 1:
            plot_case = ref_case
            plot_ts = ref_plot_ts
            plot_begin_yr = ref_begin_yr
            corr_matrix = ref_corr_matrix


        nt = plot_ts.shape[1]

        if aggregate == 1:
            plot_time = numpy.arange(0,nt) + plot_begin_yr
        else:
            plot_time = numpy.arange(0,nt)

        if debug: print(__name__, 'plot_time: ', plot_time)
        if debug: print(__name__, 'plot_begin_yr: ', plot_begin_yr)

        plot_ts_mean   = numpy.mean(plot_ts, axis = 1)
        plot_ts_stddev = numpy.std(plot_ts, axis = 1)

        for i,name in enumerate(index_names):
            min_plot = numpy.amin(ref_plot_ts[i, :])
            max_plot = numpy.amax(ref_plot_ts[i, :])

            y_axis_ll = min_plot - 0.5*numpy.std(ref_plot_ts[i, :])
            y_axis_ul = max_plot + 0.5 * numpy.std(ref_plot_ts[i,:])

            ax[i, k].axis([plot_time[0],plot_time[-1], y_axis_ll, y_axis_ul])

            print('plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot: ',
                  plot_time[0],plot_time[-1], 1.1*min_plot, 1.1*max_plot)

            mean_line_plot = numpy.zeros(nt) + plot_ts_mean[i]
            mean_line, = ax[i, k].plot(plot_time, mean_line_plot, color = 'black', linewidth = 1.0, label = 'Mean')

            if begin_month == 0 and end_month == 11 and aggregate[i] == 0:
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


            ax[i, k].set_ylabel(field_names[i] + ' (' + units + ')', va='center', rotation='vertical', fontsize = 12)

            if i == 0 and k == 1:
                plt.legend(bbox_to_anchor = (1.0,1.0),
                        bbox_transform=plt.gcf().transFigure,
                             handles=[mean_line, index_line, smooth_line],
                             fontsize = 7)

        #    if i == 0:
            ax[i, k].text(0.5, 1.1, plot_case[i], ha='center', \
                    fontsize = 10, color = 'green', transform=ax[i, k].transAxes)

            corr_str = [str(round(x, 2)) for x in corr_matrix[i, :]]

            for j,name_corr in enumerate(index_names):
                if name != name_corr:
                    corr_text = 'Corr (' + name + ', ' + index_names[j] + '): ' + corr_str[j] + ' \n'

            print(__name__, 'corr_text: ', corr_text)

            ax[i, k].text(0.05, 0.90, corr_text, ha='left', \
                                                fontsize = 8, transform=ax[i, k].transAxes)



            if i == n_index-1:
                ax[i, k].text(0.5, -0.3, 'Year', ha='center', \
                        fontsize = 14, transform=ax[i, k].transAxes)

            ax[i, k].set_title(name + ' , mean = ' +  "%.2f" % plot_ts_mean[i]
                    + ' , std. dev. = ' +  "%.2f" % plot_ts_stddev[i], fontsize = 10)

            ax[i, k].get_yaxis().get_major_formatter().set_useOffset(False)
            ax[i, k].yaxis.set_major_locator(MaxNLocator(6))

            if i < n_index-1:
                ax[i, k].tick_params(labelbottom='off')

            for tick in ax[i, k].yaxis.get_major_ticks():
                    tick.label.set_fontsize(10)
            for tick in ax[i, k].xaxis.get_major_ticks():
                    tick.label.set_fontsize(10)


    plt.subplots_adjust(hspace=0.3)
    plt.subplots_adjust(wspace=0.3)

    mpl.rcParams['savefig.dpi']=300

    index_names_text = '_'.join(index_names)

    outfile = plots_dir + '/' + casename[0] + '_' + season + '_' + index_names_text + '.png'

    print(__name__, 'Plot file: ', outfile)

    plt.savefig(outfile)
    #plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python %prog [options]")

    parser.add_argument("-d", "--debug", dest = "debug", default = False,
            help = "debug option to print some data")

    parser.add_argument("--indir", dest = "indir", nargs = '+',
                        help = "filepath to directory model data")

    parser.add_argument("-c", "--casename", dest = "casename", nargs = '+',
                        help = "casename of the run")

    parser.add_argument("-f", "--field_names", dest = "field_names", nargs = '+',
                        help = "variable name")

    parser.add_argument("--interp_grid", dest = "interp_grid", nargs = '+',
                        help = "variable name")

    parser.add_argument("--interp_method", dest = "interp_method", nargs = '+',
                        help = "method used for interpolating the test case e.g. conservative_mapping")

    parser.add_argument("--ref_case_dir", dest = "ref_case_dir", nargs = '+',
                        help = "filepath to ref_case directory")

    parser.add_argument("--ref_case", dest = "ref_case", nargs = '+',
                        help = "reference casename")

    parser.add_argument("--ref_interp_grid", dest = "ref_interp_grid", nargs = '+',
                        help = "name of the interpolated grid of reference case")

    parser.add_argument("--ref_interp_method", dest = "ref_interp_method", nargs = '+',
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

    parser.add_argument("--index_names", dest = "index_names", nargs = '+',
                        help = "name of the indices to plot")

    parser.add_argument("--aggregate", dest = "aggregate", nargs = '+', type = int,
                        help = "end_month", default = 1)

    parser.add_argument("--no_ann", dest = "no_ann", nargs = '+', type = int,
            help = "flag (0/1) to remove annual cycle, default is off (0)", default = 0)

    parser.add_argument("--stdize", dest = "stdize", nargs = '+', type = int,
            help = "flag (0/1) to standardize index, default is off (0)", default = 0)

    parser.add_argument("--plots_dir", dest = "plots_dir",
                        help = "filepath to GPCP directory")

    args = parser.parse_args()

    debug               = args.debug
    indir               = args.indir
    casename            = args.casename
    field_names         = args.field_names
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
    index_names         = args.index_names
    aggregate           = args.aggregate
    no_ann              = args.no_ann
    stdize              = args.stdize
    plots_dir           = args.plots_dir



    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_multiple_index_same_plot(indir = indir,
                                  casename = casename,
                                  field_names = field_names,
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
                                  index_names = index_names,
                                  aggregate = aggregate,
                                  no_ann = no_ann,
                                  stdize = stdize,
                                  debug = debug)
