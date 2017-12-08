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
from get_regress_index_field import get_regress_index_field
from optparse import OptionParser
from round_to_first import round_to_first
from get_season_name import get_season_name
import argparse


def plot_regress_lead_lag_index_field (indir,
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
               reg,
               reg_name,
               debug = False):


    print(__name__, 'casename: ', casename)
    print(__name__, 'field_name: ', field_name)

    lags = list(range(-8, 12, 4))
#    lags = list(range(-4, 4, 4))
    n_lags = len(lags)

    for i, lag in enumerate(lags):
        regr_matrix, corr_matrix, t_test_matrix, lat_reg, lon_reg, units = get_regress_index_field (
                                  indir     = indir,
                                  casename     = casename,
                                  field_name     = field_name,
                                  interp_grid     = interp_grid,
                                  interp_method = interp_method,
                                  begin_yr     = begin_yr,
                                  end_yr     = end_yr,
                                  begin_month     = begin_month,
                                  end_month     = end_month,
                                  aggregate    = 0,
                                  no_ann    = 1,
                                  stdize    = stdize,
                                  lag         = lag,
                                  reg         = reg,
                                  reg_name    = reg_name,
                                  debug     = debug)

        if i == 0:
            regr_matrix_lag   = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))
            corr_matrix_lag   = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))
            t_test_matrix_lag = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))

        regr_matrix_lag[i, ::]   = regr_matrix
        corr_matrix_lag[i, ::]   = corr_matrix
        t_test_matrix_lag[i, ::] = t_test_matrix


    plot_field =  regr_matrix_lag
    plot_t_test = t_test_matrix_lag


    field_name_ref = [] + field_name

    for k in [0, 1]:
        if ref_case[k] == 'HadISST' or ref_case[k] == 'HadISST_ts' or ref_case[k] == 'HadOIBl':
            if field_name[k] == 'TS': field_name_ref[k] = 'SST'

    if debug:
        print(__name__, 'field_name_ref: ', field_name_ref)


    for i, lag in enumerate(lags):
        ref_regr_matrix, ref_corr_matrix, ref_t_test_matrix, lat_reg, lon_reg, units = get_regress_index_field (
                                  indir         = ref_case_dir,
                                  casename      = ref_case,
                                  field_name    = field_name_ref,
                                  interp_grid   = ref_interp_grid,
                                  interp_method = ref_interp_method,
                                  begin_yr      = ref_begin_yr,
                                  end_yr        = ref_end_yr,
                                  begin_month   = begin_month,
                                  end_month     = end_month,
                                  aggregate     = 0,
                                  lag           = lag,
                                  no_ann        = 1,
                                  stdize        = stdize,
                                  reg           = reg,
                                  reg_name       = reg_name,
                                  debug         = debug)

        if i == 0:
            ref_regr_matrix_lag   = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))
            ref_corr_matrix_lag   = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))
            ref_t_test_matrix_lag = numpy.ma.zeros((n_lags, lat_reg.shape[0], lon_reg.shape[0]))

        ref_regr_matrix_lag[i, ::]   = ref_regr_matrix
        ref_corr_matrix_lag[i, ::]   = ref_corr_matrix
        ref_t_test_matrix_lag[i, ::] = ref_t_test_matrix

        ref_plot_field = ref_regr_matrix_lag
        ref_plot_t_test = ref_t_test_matrix_lag

        if debug:
            print(__name__, 'plot_field: ', plot_field)
        if debug:
            print(__name__, 'ref_plot_field: ', ref_plot_field)

    season_field = get_season_name(begin_month[0], end_month[0])
    season_index = get_season_name(begin_month[1], end_month[1])

    #Computing levels using mean and standard deviation
    plot_field_min  = numpy.min(plot_field)
    plot_field_max  = numpy.max(plot_field)


    n_stddev = 5
    num      = 11
    max_plot = round_to_first(5.0 * numpy.nanstd(ref_plot_field))
    levels      = numpy.linspace(-max_plot, max_plot, num = num)

    print()
    print('plot_field - mean, stddev: ', numpy.nanmean(plot_field),
          numpy.nanstd(plot_field))
    print('plot_field - min, max: ', numpy.ma.min(plot_field),
          numpy.ma.max(plot_field))

    print('ref_plot_field - mean, stddev: ', numpy.nanmean(ref_plot_field),
          numpy.nanstd(ref_plot_field))
    print('ref_plot_field - min, max: ', numpy.nanmin(plot_field),
          numpy.nanmax(plot_field))

    print('max_plot: ', max_plot)
    print('contour levels: ', levels)


    #PLOT REGRESSIONS
    f, ax = plt.subplots(n_lags, 3, figsize=(12, 11))

    title_txt = 'Lead-lag Regression Coefficients: ' + field_name[0] + ' on ' \
                   + reg_name[1] + ' (' + field_name[1] + ') index'

    if stdize == 1:
        title_txt = 'Lead-lag Regression Coefficients: ' + field_name[0] + ' on ' \
                'standardized ' + reg_name[1] + ' (' + field_name[1] + ') index'  + \
                ' (mean = 0, std. dev. = 1)'

    f.suptitle('ENSO Evolution: ' +  field_name[0], fontsize = 12, color = 'blue')

    f.text(0.5, 0.95, title_txt, ha = 'center', va='center', rotation='horizontal', fontsize = 10)

    lons, lats = numpy.meshgrid(lon_reg,lat_reg)

    for k in [0, 1, 2]:
        if k == 0:
            plot_case = casename[0]
            plot_field = regr_matrix_lag
            plot_t_test = t_test_matrix_lag

        if k == 1:
            plot_case = ref_case[0]
            plot_field = ref_regr_matrix_lag
            plot_t_test = ref_t_test_matrix_lag

        if k == 2:
            plot_case = 'Difference'
            plot_field = regr_matrix_lag - ref_regr_matrix_lag




        for i, lag in enumerate(lags):
            ax[i, k].set_title('lag = ' + str(lag) + ' months', fontsize = 10)

            m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=0,urcrnrlon=360,resolution='c', ax = ax[i, k])

            m.drawcoastlines()

            x, y = m(lons,lats)

            c = m.contourf(x, y, plot_field[i, :, :], cmap = 'seismic', levels = levels, extend = 'both')

            #plotting hatches representing statistical significance
            if k != 2:
                m.contourf(x, y, plot_t_test[i, :, :], 2, colors = 'none', extend = 'both', hatches = [None, '////'])

            if i == 0:
                ax[i, k].text(0.5, 1.2, plot_case, ha='center', \
                    fontsize = 10, transform=ax[i, k].transAxes, color = 'green')

            text_data = 'min = '  + str(round(numpy.nanmin(plot_field[i, :, :]), 2)) + ', ' + \
                    'max = '  + str(round(numpy.nanmax(plot_field[i, :, :]), 2))

            ax[i, k].text(0, -100, text_data, transform = ax[i, k].transData, fontsize = 6)

    text_data = 'Units = ' + units + '. ' + \
            'Hatched areas: Significant at 95% confidence level. ' + \
            'Positive lags indicate Nino 3.4 index leading.'

    f.text(0.05, 0.05, text_data, va='center', rotation='horizontal', fontsize = 8)


    plt.subplots_adjust(hspace=0.25)

    f.subplots_adjust(right = 0.85)

    cbar_ax = f.add_axes([0.9, 0.25, 0.01, 0.5])

    cb = f.colorbar(c, cax=cbar_ax)
    cb.set_label('Regression Coefficient (' + units + ')')

    mpl.rcParams['savefig.dpi']=300


    print(__name__, 'begin_month: ', begin_month)
    print(__name__, 'end_month: ', end_month)

    outfile = plots_dir + '/' + casename[0] + '_ENSO_evolution_regr_' \
               + field_name[0] + '_' + reg[0] + '_' + season_field + '_' \
               + field_name[1] + '_' + reg[1] + '_' + season_index + '.png'

    plt.savefig(outfile)



    #PLOT CORRELATIONS
    max_plot = round_to_first(5.0 * numpy.nanstd(ref_corr_matrix_lag))
    levels      = numpy.linspace(-max_plot, max_plot, num = num)

    f, ax = plt.subplots(n_lags, 3, figsize=(12, 11))

    title_txt = 'Lead-lag Correlations: ' + field_name[0] + ' on ' \
                   + reg_name[1] + ' (' + field_name[1] + ') index'

    if stdize == 1:
        title_txt = 'Lead-lag Correlations: ' + field_name[0] + ' on ' \
                'standardized ' + reg_name[1] + ' (' + field_name[1] + ') index'  + \
                ' (mean = 0, std. dev. = 1)'

    f.suptitle('ENSO Evolution: ' +  field_name[0], fontsize = 12, color = 'blue')

    f.text(0.5, 0.95, title_txt, ha = 'center', va='center', rotation='horizontal', fontsize = 10)

    lons, lats = numpy.meshgrid(lon_reg,lat_reg)

    for k in [0, 1, 2]:
        if k == 0:
            plot_case = casename[0]
            plot_field = corr_matrix_lag
            plot_t_test = t_test_matrix_lag

        if k == 1:
            plot_case = ref_case[0]
            plot_field = ref_corr_matrix_lag
            plot_t_test = ref_t_test_matrix_lag

        if k == 2:
            plot_case = 'Difference'
            plot_field = corr_matrix_lag - ref_corr_matrix_lag


        for i, lag in enumerate(lags):
            ax[i, k].set_title('lag = ' + str(lag) + ' months', fontsize = 10)

            m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=0,urcrnrlon=360,resolution='c', ax = ax[i, k])

            m.drawcoastlines()

            x, y = m(lons,lats)

            c = m.contourf(x, y, plot_field[i, :, :], cmap = 'seismic', levels = levels, extend = 'both')

            #plotting hatches representing statistical significance
        #    m.contourf(x, y, plot_t_test[i, :, :], 2, colors = 'none', extend = 'both', hatches = [None, '////'])

            text_data = 'min = '  + str(round(numpy.nanmin(plot_field[i, :, :]), 2)) + ', ' + \
                    'max = '  + str(round(numpy.nanmax(plot_field[i, :, :]), 2))

            ax[i, k].text(0, -100, text_data, transform = ax[i, k].transData, fontsize = 6)

            if i == 0:
                ax[i, k].text(0.5, 1.2, plot_case, ha='center', \
                    fontsize = 10, transform=ax[i, k].transAxes, color = 'green')


    text_data =  'Positive lags indicate Nino 3.4 index leading.'

    f.text(0.05, 0.05, text_data, rotation='horizontal', fontsize = 10)


    plt.subplots_adjust(hspace=0.25)

    f.subplots_adjust(right = 0.85)

    cbar_ax = f.add_axes([0.9, 0.25, 0.01, 0.5])

    cb = f.colorbar(c, cax=cbar_ax)
    cb.set_label('Correlation')

    mpl.rcParams['savefig.dpi']=300


    print(__name__, 'begin_month: ', begin_month)
    print(__name__, 'end_month: ', end_month)

    outfile = plots_dir + '/' + casename[0] + '_ENSO_evolution_corr_' \
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
                        help = "end_month", default = 1)

    parser.add_argument("--no_ann", dest = "no_ann", type = int,
                        help = "end_month", default = 0)

    parser.add_argument("--stdize", dest = "stdize", type = int,
                        help = "end_month", default = 0)

    parser.add_argument("--reg", dest = "reg", nargs = '+',
                        help = "regions to be analyzed/plotted")

    parser.add_argument("--reg_name", dest = "reg_name", nargs = '+',
                        help = "names of regions to be placed in plots")

    parser.add_argument("--plots_dir", dest = "plots_dir",
                        help = "filepath to directory where plots will be saved")

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
    ref_begin_yr            = args.ref_begin_yr
    ref_end_yr              = args.ref_end_yr
    begin_month         = args.begin_month
    end_month           = args.end_month
    aggregate           = args.aggregate
    no_ann            = args.no_ann
    stdize            = args.stdize
    reg            = args.reg
    reg_name        = args.reg_name
    plots_dir           = args.plots_dir


    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    x = mpl.get_backend()
    print('backend: ', x)

    plot_regress_lead_lag_index_field (indir = indir,
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
                               debug = debug)
