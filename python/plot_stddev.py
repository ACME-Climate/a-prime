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

from   mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import math
import numpy

from netCDF4 import Dataset

from get_season_name       import get_season_name
from round_to_first        import round_to_first
from get_reg_area_avg      import get_reg_area_avg
from get_reg_area_avg_rmse import get_reg_area_avg_rmse
from read_climo_file       import read_climo_file
from compute_reg_seasonal_climo_and_stddev import compute_reg_seasonal_climo_and_stddev
from compute_contour_levels import compute_contour_levels
from optparse            import OptionParser

parser = OptionParser(usage = "python %prog [options]")

parser.add_option("--indir", dest = "indir",
                    help = "filepath to directory model data")

parser.add_option("-c", "--casename", dest = "casename",
                    help = "casename of the run")

parser.add_option("-f", "--field_name", dest = "field_name",
                    help = "variable name")

parser.add_option("--reg", dest = "reg",
                    help = "name of region to be plotted")

parser.add_option("--begin_yr", dest = "begin_yr", type = "int",
                    help = "begin year")

parser.add_option("--end_yr", dest = "end_yr", type = "int",
                    help = "end year")

parser.add_option("--begin_month", dest = "begin_month", type = "int",
                    help = "begin_month", default = 0)

parser.add_option("--end_month", dest = "end_month", type = "int",
                    help = "end_month", default = 11)

parser.add_option("--interp_grid", dest = "interp_grid",
                    help = "name of the interpolated grid of test case")

parser.add_option("--interp_method", dest = "interp_method",
                    help = "method used for interpolating the test case e.g. conservative_mapping")

parser.add_option("--ref_case_dir", dest = "ref_case_dir",
                    help = "filepath to ref_case directory")

parser.add_option("--ref_case", dest = "ref_case",
                    help = "reference casename")

parser.add_option("--ref_begin_yr", dest = "ref_begin_yr", type = "int",
                    help = "ref_case begin year")

parser.add_option("--ref_end_yr", dest = "ref_end_yr", type = "int",
                    help = "ref_case end year")

parser.add_option("--ref_interp_grid", dest = "ref_interp_grid",
                    help = "name of the interpolated grid of reference case")

parser.add_option("--ref_interp_method", dest = "ref_interp_method",
                    help = "method used for interpolating the reference case e.g. conservative_mapping")

parser.add_option("--plots_dir", dest = "plots_dir",
                    help = "filepath to plots directory")

parser.add_option("--debug", dest = "debug",
                    help = "debug flag", default = False)

(options, args) = parser.parse_args()

indir                = options.indir
casename            = options.casename
field_name            = options.field_name
reg                = options.reg
begin_yr            = options.begin_yr
end_yr                = options.end_yr
begin_month            = options.begin_month
end_month            = options.end_month
interp_grid            = options.interp_grid
interp_method             = options.interp_method
ref_case_dir           = options.ref_case_dir
ref_case           = options.ref_case
ref_begin_yr            = options.ref_begin_yr
ref_end_yr        = options.ref_end_yr
ref_interp_grid         = options.ref_interp_grid
ref_interp_method       = options.ref_interp_method
plots_dir              = options.plots_dir
debug            = options.debug

#Get filename
season = get_season_name(begin_month, end_month)

print()
print('Computing climo and inter-annual std. dev. for case: ', casename)
print()

field_mean, field_stddev, lat, lon, units = compute_reg_seasonal_climo_and_stddev(
                                indir = indir,
                                casename= casename,
                                field_name = field_name,
                                interp_grid = interp_grid,
                                interp_method = interp_method,
                                begin_yr= begin_yr,
                                end_yr= end_yr,
                                begin_month = begin_month,
                                end_month = end_month,
                                reg = reg,
                                aggregate = 1,
                                debug = debug)


ref_field_mean, ref_field_stddev, lat, lon, units = compute_reg_seasonal_climo_and_stddev(
                                indir = ref_case_dir,
                                casename = ref_case,
                                field_name = field_name,
                                interp_grid = ref_interp_grid,
                                interp_method = ref_interp_method,
                                begin_yr= ref_begin_yr,
                                end_yr= ref_end_yr,
                                begin_month = begin_month,
                                end_month = end_month,
                                reg = reg,
                                aggregate = 1,
                                debug = debug)


#field, lat, lon, area, units = read_climo_file(indir = indir, \
#                     casename = casename, \
#                     season = season, \
#                     field_name = field_name, \
#                     begin_yr = begin_yr, \
#                     end_yr = end_yr, \
#                     interp_grid = interp_grid, \
#                     interp_method = interp_method, \
#                     reg = 'global')
#
#print
#print('Reading climo file for case: ', ref_case
#print
#
#field_ref_case, lat, lon, area, units = read_climo_file(indir = ref_case_dir, \
#                         casename = ref_case, \
#                         season = season, \
#                         field_name = field_name, \
#                         begin_yr = ref_begin_yr, \
#                         end_yr = ref_end_yr, \
#                         interp_grid = ref_interp_grid, \
#                         interp_method = ref_interp_method,
#                         reg = 'global')
#


#field_max = numpy.max(field[:])
#field_min = numpy.min(field[:])
#field_avg = get_reg_area_avg(field, lat, lon, area)
#
#field_ref_case_max = numpy.max(field_ref_case[:])
#field_ref_case_min = numpy.min(field_ref_case[:])
#field_ref_case_avg = get_reg_area_avg(field_ref_case, lat, lon, area)



#Computing levels using mean and standard deviation
num = 11
n_stddev = 5


#Plot std. dev.
f, ax = plt.subplots(3, 2, figsize=(17, 11))

plt.suptitle('Climatology and Inter-annual Standard Deviation\n' + field_name + ' (' + units + ') ' + season, fontsize = 14, color = 'blue')

levels = compute_contour_levels(ref_field_mean, n_stddev, num)

for k in [0, 1, 2]:
    if k == 0:
        plot_case = casename
        plot_field = field_mean
        cmap_color = 'hot_r'
        if numpy.ma.min(ref_field_mean) < 0 and numpy.ma.max(ref_field_mean) > 0:
            cmap_color = 'seismic'
    if k == 1:
        plot_case = ref_case
        plot_field = ref_field_mean
        cmap_color = 'hot_r'
        if numpy.ma.min(ref_field_mean) < 0 and numpy.ma.max(ref_field_mean) > 0:
            cmap_color = 'seismic'
    if k == 2:
        plot_case = 'Difference'
        plot_field = field_mean - ref_field_mean
        cmap_color = 'seismic'
        max_plot = round_to_first(2.0 * numpy.ma.std(ref_field_mean))
        levels   = numpy.linspace(-max_plot, max_plot, num = num)
        #levels = compute_contour_levels(plot_field, n_stddev, num)

    plot_field_min = numpy.min(plot_field[:])
    plot_field_max = numpy.max(plot_field[:])

    ax[k, 0].set_title(plot_case)

    m = Basemap(projection='cyl',llcrnrlat=lat[0],urcrnrlat=lat[-1],\
            llcrnrlon=lon[0],urcrnrlon=lon[-1],resolution='c', ax = ax[k, 0])

    m.drawcoastlines()

    lons, lats = numpy.meshgrid(lon,lat)
    x, y = m(lons,lats)


    c = m.contourf(x, y, plot_field[:, :], cmap = cmap_color, levels = levels, extend = 'both')

    meridians = numpy.arange(numpy.floor(lon[0]),numpy.ceil(lon[-1]),30)
    parallels = numpy.arange(numpy.floor(lat[0]),numpy.ceil(lat[-1]),30)

    m.drawmeridians(meridians, labels=[0,0,0,1],fontsize=10)
    m.drawparallels(parallels, labels=[1,0,0,0],fontsize=10)

    cb = m.colorbar(c)

    text_data = 'min = '  + str(round(plot_field_min, 2)) + ', ' + \
            'max = '  + str(round(plot_field_max, 2))

    ax[k, 0].text(0.0, -0.15, text_data, transform = ax[k, 0].transAxes, fontsize = 10)

    if k == 0:
        ax[k, 0].text(0.5, 1.2, 'Mean', ha='center', \
                fontsize = 14, transform=ax[k, 0].transAxes, color = 'green')


levels = compute_contour_levels(ref_field_stddev, n_stddev, num)

for k in [0, 1, 2]:
    if k == 0:
        plot_case = casename
        plot_field = field_stddev
        cmap_color = 'hot_r'
    if k == 1:
        plot_case = ref_case
        plot_field = ref_field_stddev
        cmap_color = 'hot_r'
    if k == 2:
        plot_case = 'Difference'
        plot_field = field_stddev - ref_field_stddev
        cmap_color = 'seismic'
        max_plot = round_to_first(2.0 * numpy.ma.std(ref_field_stddev))
        levels   = numpy.linspace(-max_plot, max_plot, num = num)
        #levels = compute_contour_levels(plot_field, n_stddev, num)

    plot_field_min = numpy.min(plot_field[:])
    plot_field_max = numpy.max(plot_field[:])

    ax[k, 1].set_title(plot_case)

    m = Basemap(projection='cyl',llcrnrlat=lat[0],urcrnrlat=lat[-1],\
            llcrnrlon=lon[0],urcrnrlon=lon[-1],resolution='c', ax = ax[k, 1])

    m.drawcoastlines()

    lons, lats = numpy.meshgrid(lon,lat)
    x, y = m(lons,lats)


    c = m.contourf(x, y, plot_field[:, :], cmap = cmap_color, levels = levels, extend = 'both')

    meridians = numpy.arange(numpy.floor(lon[0]),numpy.ceil(lon[-1]),30)
    parallels = numpy.arange(numpy.floor(lat[0]),numpy.ceil(lat[-1]),30)

    m.drawmeridians(meridians, labels=[0,0,0,1],fontsize=10)
    m.drawparallels(parallels, labels=[1,0,0,0],fontsize=10)

    cb = m.colorbar(c)

    text_data = 'min = '  + str(round(plot_field_min, 2)) + ', ' + \
            'max = '  + str(round(plot_field_max, 2))

    ax[k, 1].text(0.0, -0.15, text_data, transform = ax[k, 1].transAxes, fontsize = 10)

    if k == 0:
        ax[k, 1].text(0.5, 1.2, 'Std. Dev.', ha='center', \
                fontsize = 14, transform=ax[k, 1].transAxes, color = 'green')

plt.subplots_adjust(hspace=0.25)


#Plot ref_case
#ax = f.add_subplot(2,1,2)
#
#ax.set_title(ref_case)
#
#m = Basemap(projection='cyl',llcrnrlat=lat[0],urcrnrlat=lat[-1],\
#            llcrnrlon=lon[0],urcrnrlon=lon[-1],resolution='c')
#
#m.drawcoastlines()
#
#c = m.contourf(x, y, ref_plot_field[:, :], cmap = 'hot_r', levels = levels, extend = 'both')
#
#m.drawmeridians(meridians, labels=[0,0,0,1],fontsize=10)
#m.drawparallels(parallels, labels=[1,0,0,0],fontsize=10)
#
#cb = m.colorbar(c)
#
#text_data = 'min = '  + str(round(ref_field_min, 2)) + ', ' + \
#            'max = '  + str(round(ref_field_max, 2))
#
#ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)


##Computing levels for diff plot using mean and standard deviation
#field_diff      = field[:, :] - field_ref_case[:, :]
#field_diff_mean = field_avg - field_ref_case_avg
#field_diff_rmse = get_reg_area_avg_rmse(field_diff, lat, lon, area)
#field_diff_min  = numpy.min(field_diff)
#field_diff_max  = numpy.max(field_diff)
#
#num         = 11
#max_plot    = round_to_first(4.0 * numpy.ma.std(field_diff))
#levels_diff = numpy.linspace(-max_plot, max_plot, num = num)
#
#print()
#print('For difference plot: ')
#print('mean, stddev, max_plot: ',
#      numpy.ma.mean(field_diff), numpy.ma.std(field_diff), max_plot)
#print('min, max: ', numpy.ma.min(field_diff), numpy.ma.max(field_diff))
#print('contour levels: ', levels_diff)
#
##Plot difference plot
#ax = f.add_subplot(3,1,3)
#
##ax.set_title(casename + ' - ' + ref_case)
#ax.set_title('Difference')
#
#m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
#            llcrnrlon=0,urcrnrlon=360,resolution='c')
#m.drawcoastlines()
#
#c = m.contourf(x, y, field_diff[:, :], cmap = 'seismic', levels = levels_diff, extend = 'both')
#cb = m.colorbar()
#
#text_data = 'RMSE = ' + str(round(field_diff_rmse, 2))+ ', ' + \
#        'mean bias = ' + str(round(field_diff_mean, 2))+ ', ' + \
#            'min = '  + str(round(field_diff_min, 2)) + ', ' + \
#            'max = '  + str(round(field_diff_max, 2))
#
#ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)

#Fill contour was buggy when plotting negative values, so we use image plots with line contours overlayed as another option
#Contour seems to be fixed now with a different backend
#c = m.imshow(field_diff, cmap = 'seismic', vmin = -max_abs, vmax = max_abs, filternorm = 0, interpolation = 'nearest')
#cb = m.colorbar(extend = 'both')
#c = m.contour(x, y, field_diff, levels = levels_diff, colors = 'k', extend = 'both', linewidths = 0.25)


mpl.rcParams['savefig.dpi']=300

outfile = plots_dir + '/' + casename + '-' + ref_case + '_' \
                   + field_name + '_stddev_' + reg + '_' + season + '.png'

plt.savefig(outfile)

#plt.show()



