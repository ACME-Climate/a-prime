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
from optparse            import OptionParser

parser = OptionParser(usage = "python %prog [options]")

parser.add_option("--indir", dest = "indir",
                    help = "filepath to directory model data")

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

(options, args) = parser.parse_args()

indir                = options.indir
casename            = options.casename
field_name            = options.field_name
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

#Get filename
season = get_season_name(begin_month, end_month)

print()
print('Reading climo file for case: ', casename)
print()

field, lat, lon, area, units = read_climo_file(indir = indir, \
                     casename = casename, \
                     season = season, \
                     field_name = field_name, \
                     begin_yr = begin_yr, \
                     end_yr = end_yr, \
                     interp_grid = interp_grid, \
                     interp_method = interp_method, \
                     reg = 'global')

print()
print('Reading climo file for case: ', ref_case)
print()

field_ref_case, lat, lon, area, units = read_climo_file(indir = ref_case_dir, \
                         casename = ref_case, \
                         season = season, \
                         field_name = field_name, \
                         begin_yr = ref_begin_yr, \
                         end_yr = ref_end_yr, \
                         interp_grid = ref_interp_grid, \
                         interp_method = ref_interp_method,
                         reg = 'global')



field_max = numpy.max(field[:])
field_min = numpy.min(field[:])
field_avg = get_reg_area_avg(field, lat, lon, area)

field_ref_case_max = numpy.max(field_ref_case[:])
field_ref_case_min = numpy.min(field_ref_case[:])
field_ref_case_avg = get_reg_area_avg(field_ref_case, lat, lon, area)


#Computing levels using mean and standard deviation
num = 11

max_plot_temp = numpy.ma.mean(field_ref_case[:]) + \
                          4.0 * numpy.ma.std(field_ref_case[:])
if max_plot_temp > numpy.ma.max(field_ref_case[:]):
        max_plot_temp = numpy.ma.max(field_ref_case[:])

max_plot      = round_to_first(max_plot_temp)

min_plot_temp = numpy.ma.mean(field_ref_case[:]) - \
                          4.0 * numpy.ma.std(field_ref_case[:])

if min_plot_temp < numpy.ma.min(field_ref_case[:]):
        min_plot_temp = numpy.ma.min(field_ref_case[:])

min_plot      = round_to_first(min_plot_temp)

levels = numpy.linspace(min_plot, max_plot, num = num)

print()
print('For climatology plots: ')
print('mean, stddev, min_plot, max_plot ref_case: ',
      numpy.ma.mean(field_ref_case[:]), numpy.ma.std(field_ref_case[:]),
      min_plot, max_plot)
print('min, max field: ', field_min, field_max)
print('levels:', levels)
print()


#Plot climotology
f = plt.figure(figsize=(8.5, 11))

plt.suptitle(field_name + ' (' + units + ') ' + season, fontsize = 20)

#Plot test_case
ax = f.add_subplot(3,1,1)

ax.set_title(casename)

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')

m.drawcoastlines()

lons, lats = numpy.meshgrid(lon,lat)
x, y = m(lons,lats)

c = m.contourf(x, y, field[:, :], cmap = 'hot_r', levels = levels, extend = 'both')
cb = m.colorbar(c)

text_data = 'mean = ' + str(round(field_avg, 2)) + ', ' + \
                               'min = '  + str(round(field_min, 2)) + ', ' + \
                               'max = '  + str(round(field_max, 2))
ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)


#Plot ref_case
ax = f.add_subplot(3,1,2)

ax.set_title(ref_case)

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')

m.drawcoastlines()

c = m.contourf(x, y, field_ref_case[:, :], cmap = 'hot_r', levels = levels, extend = 'both')
cb = m.colorbar(c)

text_data = 'mean = ' + str(round(field_ref_case_avg, 2)) + ', ' + \
            'min = '  + str(round(field_ref_case_min, 2)) + ', ' + \
            'max = '  + str(round(field_ref_case_max, 2))

ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)


#Computing levels for diff plot using mean and standard deviation
field_diff      = field[:, :] - field_ref_case[:, :]
field_diff_mean = field_avg - field_ref_case_avg
field_diff_rmse = get_reg_area_avg_rmse(field_diff, lat, lon, area)
field_diff_min  = numpy.min(field_diff)
field_diff_max  = numpy.max(field_diff)

num         = 11
max_plot    = round_to_first(4.0 * numpy.ma.std(field_diff))
levels_diff = numpy.linspace(-max_plot, max_plot, num = num)

print()
print('For difference plot: ')
print('mean, stddev, max_plot: ', numpy.ma.mean(field_diff),
      numpy.ma.std(field_diff), max_plot)
print('min, max: ', numpy.ma.min(field_diff), numpy.ma.max(field_diff))
print('contour levels: ', levels_diff)

#Plot difference plot
ax = f.add_subplot(3,1,3)

#ax.set_title(casename + ' - ' + ref_case)
ax.set_title('Difference')

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')
m.drawcoastlines()

c = m.contourf(x, y, field_diff[:, :], cmap = 'seismic', levels = levels_diff, extend = 'both')
cb = m.colorbar()

text_data = 'RMSE = ' + str(round(field_diff_rmse, 2))+ ', ' + \
        'mean bias = ' + str(round(field_diff_mean, 2))+ ', ' + \
            'min = '  + str(round(field_diff_min, 2)) + ', ' + \
            'max = '  + str(round(field_diff_max, 2))

ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)

#Fill contour was buggy when plotting negative values, so we use image plots with line contours overlayed as another option
#Contour seems to be fixed now with a different backend
#c = m.imshow(field_diff, cmap = 'seismic', vmin = -max_abs, vmax = max_abs, filternorm = 0, interpolation = 'nearest')
#cb = m.colorbar(extend = 'both')
#c = m.contour(x, y, field_diff, levels = levels_diff, colors = 'k', extend = 'both', linewidths = 0.25)


mpl.rcParams['savefig.dpi']=300

outfile = plots_dir + '/' + casename + '-' + ref_case + '_' \
                   + field_name + '_climo_' + season + '.png'

plt.savefig(outfile)

#plt.show()



