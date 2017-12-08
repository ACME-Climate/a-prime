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
from get_regress_index_index import get_regress_index_index
from optparse import OptionParser
from round_to_first import round_to_first
from get_season_name import get_season_name
import argparse


def plot_regress_index_index (indir,
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
               aggregate,
               lag,
               no_ann,
               stdize,
               reg,
               reg_name,
               split_yfit_x_0,
               plots_dir,
               debug = False):


    print(__name__, 'casename: ', casename)
    print(__name__, 'field_name: ', field_name)

    x = get_regress_index_index (indir     = indir,
                    casename     = casename,
                    field_name     = field_name,
                    interp_grid     = interp_grid,
                    interp_method = interp_method,
                    begin_yr     = begin_yr,
                    end_yr     = end_yr,
                    begin_month     = begin_month,
                    end_month     = end_month,
                    aggregate    = aggregate,
                    lag        = lag,
                    no_ann    = no_ann,
                    stdize    = stdize,
                    reg         = reg,
                    reg_name    = reg_name,
                    debug     = False)

    regr_coef = x[0]
    intercept = x[1]
    r_value = x[2]
    p_value = x[3]
    std_err = x[4]
    field = x[5]
    index = x[6]
    units_field = x[7]
    units_index = x[8]
    units = x[9]

    if field_name[0] == 'TAUX':
        field = field * 1000.0
        regr_coef = regr_coef * 1000.0
        units_field = '10^3 ' + units_field

    if split_yfit_x_0 == 1:
        posit_index = index[numpy.where(index >= 0)]
        field_posit_index = field[numpy.where(index >= 0)]

        m = stats.linregress(posit_index, field_posit_index)
        yfit_posit = m[0] * posit_index + m[1]


        neg_index = index[numpy.where(index < 0)]
        field_neg_index = field[numpy.where(index < 0)]

        n = stats.linregress(neg_index, field_neg_index)
        yfit_neg = n[0] * neg_index + n[1]

    else:
        m = stats.linregress(index, field)
        yfit = m[0] * index + m[1]



    field_name_ref = [] + field_name

    for k in [0, 1]:
        if ref_case[k] == 'HadISST' or ref_case[k] == 'HadISST_ts' or ref_case[k] == 'HadOIBl':
            if field_name[k] == 'TS': field_name_ref[k] = 'SST'

    if debug: print(__name__, 'field_name_ref: ', field_name_ref)


    x = get_regress_index_index (      indir         = ref_case_dir,
                      casename      = ref_case,
                      field_name    = field_name_ref,
                      interp_grid   = ref_interp_grid,
                      interp_method = ref_interp_method,
                      begin_yr      = ref_begin_yr,
                      end_yr        = ref_end_yr,
                      begin_month   = begin_month,
                      end_month     = end_month,
                      aggregate    = aggregate,
                      lag        = lag,
                      no_ann    = no_ann,
                      stdize    = stdize,
                      reg           = reg,
                      reg_name     = reg_name,
                      debug         = debug)

    ref_regr_coef = x[0]
    ref_intercept = x[1]
    ref_r_value = x[2]
    ref_p_value = x[3]
    ref_std_err = x[4]
    ref_field = x[5]
    ref_index = x[6]
    ref_units_field = x[7]
    ref_units_index = x[8]
    ref_units = x[9]

    if field_name[0] == 'TAUX':
        ref_field = ref_field * 1000.0
        ref_regr_coef = ref_regr_coef * 1000.0
        ref_units_field = '10^3 ' + ref_units_field

    if split_yfit_x_0 == 1:
        posit_ref_index       = ref_index[numpy.where(ref_index >= 0)]
        ref_field_posit_ref_index = ref_field[numpy.where(ref_index >= 0)]

        m_ref         = stats.linregress(posit_ref_index, ref_field_posit_ref_index)
        ref_yfit_posit  = m_ref[0] * posit_ref_index + m_ref[1]


        neg_ref_index         = ref_index[numpy.where(ref_index <= 0)]
        ref_field_neg_ref_index = ref_field[numpy.where(ref_index <= 0)]

        n_ref         = stats.linregress(neg_ref_index, ref_field_neg_ref_index)
        ref_yfit_neg = n_ref[0] * neg_ref_index + n_ref[1]

    else:
        m_ref = stats.linregress(ref_index, ref_field)
        ref_yfit = m_ref[0] * ref_index + m_ref[1]




    season_field = get_season_name(begin_month[0], end_month[0])
    season_index = get_season_name(begin_month[1], end_month[1])

    max_index_plot = 1.2 * numpy.max(abs(ref_index))
    max_field_plot = 1.2 * numpy.max(abs(ref_field))


    f = plt.figure(figsize=(8.5, 11))

    title_txt = 'Monthly Anomalies (' + season_index + ')'

    if stdize == 1:
        title_txt = 'Standardized (mean = 0, std. dev. = 1) Monthly Anomalies (' + season_index + ')'



    f.suptitle('Scatter Plot: ' + field_name[0] + ' (' + reg[0] + ') vs. ' + \
            field_name[1] + ' (' + reg[1] + ')', fontsize = 14, color = 'blue')

    f.text(0.5, 0.95, title_txt, ha = 'center', va='center', rotation='horizontal', fontsize = 12)

    f.text(0.5, 0.05, field_name[1] + ' (' + units_index + ')', \
        ha = 'center', va='center', rotation='horizontal', fontsize = 14)

    f.text(0.05, 0.5, field_name[0] + ' (' + units_field + ')', \
        ha = 'center', va='center', rotation='vertical', fontsize = 14)



    plt.axis([-max_index_plot, max_index_plot, -max_field_plot, max_field_plot])

    plt.axhline(y = 0, c = 'black', linewidth = 1)
    plt.axvline(x = 0, c = 'black', linewidth = 1)


    test_scatter = plt.scatter(index, field, s = 10, c = 'red', marker = 's', \
                    alpha = 0.7, edgecolors = 'face', label = casename[0])

    ref_scatter  = plt.scatter(ref_index, ref_field, s = 20, c = 'black', \
                    alpha = 0.3, edgecolors = 'face', \
                    label = ref_case[0] + ' (' + field_name[0] + ') vs. ' + ref_case[1] + ' (' + field_name[1] + ')')


    if split_yfit_x_0 == 1:

        posit_index_line, = plt.plot(posit_index, yfit_posit, c = 'red', linewidth = 3, \
                        label = 'Linear fit for positive ' + field_name[1] + \
                        ' anomalies (slope = ' + str(round(m[0], 2)) + ')')

        neg_index_line,   = plt.plot(neg_index, yfit_neg, c = 'red', linewidth = 4, alpha = 0.7, \
                        label = 'Linear fit for negative ' + field_name[1] + \
                        ' anomalies (slope = ' + str(round(n[0], 2)) + ')')

        ref_posit_line,   = plt.plot(posit_ref_index, ref_yfit_posit, c = 'black', linewidth = 3, \
                        label = 'Linear fit for positive ' + field_name[1] + \
                        ' anomalies (slope = ' + str(round(m_ref[0], 2)) + ')')


        ref_neg_line,     = plt.plot(neg_ref_index, ref_yfit_neg, c = 'black', linewidth = 4, alpha = 0.7, \
                        label = 'Linear fit for negative ' + field_name[1] + \
                        ' anomalies (slope = ' + str(round(n_ref[0], 2)) + ')')

        plt.legend(handles = [test_scatter, ref_scatter, posit_index_line, neg_index_line, ref_posit_line, ref_neg_line],
               loc = 'upper left',
               fontsize = 10)

    else:

        yfit_line, = plt.plot(index, yfit, c = 'red', linewidth = 3, \
                        label = 'Linear fit (slope = ' + str(round(m[0], 2)) + ')')

        ref_yfit_line, = plt.plot(ref_index, ref_yfit, c = 'black', linewidth = 3, \
                        label = 'Linear fit (slope = ' + str(round(m_ref[0], 2)) + ')')

        plt.legend(handles = [test_scatter, ref_scatter, yfit_line, ref_yfit_line],
               loc = 'upper left',
               fontsize = 10)

    mpl.rcParams['savefig.dpi']=300


    print(__name__, 'begin_month: ', begin_month)
    print(__name__, 'end_month: ', end_month)

    outfile = plots_dir + '/' + casename[0] + '-' + ref_case[0] + '_feedback_' \
               + field_name[0] + '_' + reg[0] + '_' + season_field + '_' \
               + field_name[1] + '_' + reg[1] + '_' + season_index + '.png'

    plt.savefig(outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python %prog [options]")

    parser.add_argument("-d", "--debug", dest = "debug", default = False,
            help = "debug option to print some data")

    parser.add_argument("--indir", dest = "indir", nargs = '+',
                        help = "filepath to directory model data")

    parser.add_argument("-c", "--casename", dest = "casename", nargs = '+',
                        help = "casename of the run")

    parser.add_argument("-f", "--field_name", dest = "field_name", nargs = '+',
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

    parser.add_argument("--begin_month", dest = "begin_month", type = int, nargs = '+',
                        help = "begin_month", default = 0)

    parser.add_argument("--end_month", dest = "end_month", type = int, nargs = '+',
                        help = "end_month", default = 11)

    parser.add_argument("--aggregate", dest = "aggregate", type = int,
                        help = "flag to aggregate data", default = 1)

    parser.add_argument("--lag", dest = "lag", type = int,
                        help = "lag for regression analysis", default = 0)

    parser.add_argument("--no_ann", dest = "no_ann", type = int,
                        help = "flag to remove annual cycle", default = 0)

    parser.add_argument("--stdize", dest = "stdize", type = int,
                        help = "flag to standardize index", default = 0)

    parser.add_argument("--reg", dest = "reg", nargs = '+',
                        help = "regions to be analyzed/plotted")

    parser.add_argument("--reg_name", dest = "reg_name", nargs = '+',
                        help = "names of regions to be placed in plots")

    parser.add_argument("--split_yfit_x_0", dest = "split_yfit_x_0", type = int,
                        help = "flag to split yfit at x=0", default = 0)

    parser.add_argument("--plots_dir", dest = "plots_dir",
                        help = "filepath to GPCP directory")

    args = parser.parse_args()

    debug                = args.debug
    indir                = args.indir
    casename            = args.casename
    field_name            = args.field_name
    interp_grid            = args.interp_grid
    interp_method           = args.interp_method
    ref_case_dir            = args.ref_case_dir
    ref_case                = args.ref_case
    ref_interp_grid         = args.ref_interp_grid
    ref_interp_method       = args.ref_interp_method
    begin_yr            = args.begin_yr
    end_yr              = args.end_yr
    ref_begin_yr        = args.ref_begin_yr
    ref_end_yr          = args.ref_end_yr
    begin_month         = args.begin_month
    end_month           = args.end_month
    aggregate           = args.aggregate
    lag               = args.lag
    no_ann            = args.no_ann
    stdize            = args.stdize
    reg            = args.reg
    reg_name        = args.reg_name
    split_yfit_x_0        = args.split_yfit_x_0
    plots_dir           = args.plots_dir


    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_regress_index_index (indir = indir,
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
                               reg = reg,
                   reg_name = reg_name,
                   aggregate = aggregate,
                   lag = lag,
                   no_ann = no_ann,
                   stdize = stdize,
                   split_yfit_x_0 = split_yfit_x_0,
                   plots_dir = plots_dir,
                               debug = debug)
