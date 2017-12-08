#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
#python script to plot wind stress vectors and magnitude over the oceans using
#CF variables TAUX and TAUY

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
from optparse              import OptionParser

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

indir                   = options.indir
casename                = options.casename
field_name              = options.field_name
begin_yr                = options.begin_yr
end_yr                  = options.end_yr
begin_month             = options.begin_month
end_month               = options.end_month
interp_grid             = options.interp_grid
interp_method           = options.interp_method
ref_case_dir            = options.ref_case_dir
ref_case                = options.ref_case
ref_begin_yr            = options.ref_begin_yr
ref_end_yr              = options.ref_end_yr
ref_interp_grid         = options.ref_interp_grid
ref_interp_method       = options.ref_interp_method
plots_dir               = options.plots_dir


#Getting season name from begin_month and end_month
season = get_season_name(begin_month, end_month)

if field_name == 'TAU':
    field_X_name    = 'TAUX'
    field_Y_name    = 'TAUY'
    field_mask_name = 'OCNFRAC'

#Read x and y components of vector field and mask field
#Reading mask field
field_mask, lat, lon, area, units = read_climo_file(indir = indir, \
                     casename = casename, \
                     season = season, \
                     field_name = field_mask_name, \
                     begin_yr = begin_yr, \
                     end_yr = end_yr, \
                     interp_grid = interp_grid, \
                     interp_method = interp_method, \
                     reg = 'global')

#Reading X component and masking grid boxes
field_X, lat, lon, area, units = read_climo_file(indir = indir, \
                     casename = casename, \
                     season = season, \
                     field_name = field_X_name, \
                     begin_yr = begin_yr, \
                     end_yr = end_yr, \
                     interp_grid = interp_grid, \
                     interp_method = interp_method, \
                     reg = 'global')


field_X_plot      = numpy.ma.zeros((lat.shape[0], lon.shape[0]))
field_X_plot[:,:] = field_X[:,:]
field_X_plot.mask = numpy.where(field_mask[:,:] < 0.5, 1, 0)

#Reading Y component and masking grid boxes
field_Y, lat, lon, area, units = read_climo_file(indir = indir, \
                     casename = casename, \
                     season = season, \
                     field_name = field_Y_name, \
                     begin_yr = begin_yr, \
                     end_yr = end_yr, \
                     interp_grid = interp_grid, \
                     interp_method = interp_method, \
                     reg = 'global')


field_Y_plot      = numpy.ma.zeros((lat.shape[0], lon.shape[0]))
field_Y_plot[:,:] = field_Y[:,:]
field_Y_plot.mask = numpy.where(field_mask[:,:] < 0.5, 1, 0)

#Computing an approximation of field magnitude from monthly averages
field_XY = numpy.ma.sqrt(numpy.ma.power(field_X_plot, 2.0) + numpy.ma.power(field_Y_plot, 2.0))


print()
print('Reading climo file for case: ', ref_case)
print()

field_ref_case_X, lat, lon, area, units = read_climo_file(indir = ref_case_dir, \
                     casename = ref_case, \
                     season = season, \
                     field_name = field_X_name, \
                     begin_yr = ref_begin_yr, \
                     end_yr = ref_end_yr, \
                     interp_grid = ref_interp_grid, \
                     interp_method = ref_interp_method, \
                     reg = 'global')

field_ref_case_Y, lat, lon, area, units = read_climo_file(indir = ref_case_dir, \
                     casename = ref_case, \
                     season = season, \
                     field_name = field_Y_name, \
                     begin_yr = ref_begin_yr, \
                     end_yr = ref_end_yr, \
                     interp_grid = ref_interp_grid, \
                     interp_method = ref_interp_method, \
                     reg = 'global')



field_ref_case_X_plot      = numpy.ma.zeros((lat.shape[0], lon.shape[0]))
field_ref_case_Y_plot      = numpy.ma.zeros((lat.shape[0], lon.shape[0]))

field_ref_case_X_plot[:,:] = field_ref_case_X[:,:]
field_ref_case_Y_plot[:,:] = field_ref_case_Y[:,:]

#Masking if the ref_case is also a model output
if ref_case != 'ERS':
    field_ref_case_X_plot.mask = numpy.where(field_mask[:,:] < 0.5, 1, 0)
    field_ref_case_Y_plot.mask = numpy.where(field_mask[:,:] < 0.5, 1, 0)

#Computing an approximation of field magnitude
field_ref_case_XY = numpy.ma.sqrt(numpy.ma.power(field_ref_case_X_plot, 2.0) + numpy.ma.power(field_ref_case_Y_plot, 2.0))

#Computing levels using mean and standard deviation
num = 11

max_plot = round_to_first(numpy.ma.mean(field_XY) + \
              3.0 * numpy.ma.std(field_XY))
min_plot = 0.0

levels = numpy.linspace(min_plot, max_plot, num = num)

field_max_TAU       = numpy.ma.max(field_XY)
field_min_TAU       = numpy.ma.min(field_XY)

field_max_ERS_TAU = numpy.ma.max(field_ref_case_XY)
field_min_ERS_TAU = numpy.ma.min(field_ref_case_XY)

print('mean, stddev, min_plot, max_plot: ',
      numpy.ma.mean(field_XY), numpy.ma.std(field_XY), min_plot, max_plot)
print('min, max: ', field_min_TAU, field_max_TAU)
print('levels:', levels)



#PLOT CASE DATA
f = plt.figure(figsize=(8.5, 11))

plt.suptitle(field_name + ' (' + units + ') ' + season, fontsize = 20)

ax = f.add_subplot(3,1,1)

ax.set_title(casename)

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')

m.drawcoastlines()

lons, lats = numpy.meshgrid(lon,lat)
x, y       = m(lons,lats)

c = m.contourf(    x, y, field_XY, \
           cmap = 'gnuplot2_r', \
        levels = levels, \
        extend = 'both')

cb = m.colorbar(c)

q = m.quiver(    x[::3,::3], y[::3,::3], \
        field_X_plot[::3, ::3], field_Y_plot[::3, ::3], \
        scale = 3.0)

text_data = 'min = '  + str(round(field_min_TAU, 2)) + ', ' + \
            'max = '  + str(round(field_max_TAU, 2))

ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)



#PLOT REF CASE DATA
ax = f.add_subplot(3,1,2)

ax.set_title('ERS')

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')

m.drawcoastlines()

c  = m.contourf(    x, y, field_ref_case_XY, \
        cmap = 'gnuplot2_r', \
        levels = levels, \
        extend = 'both')

cb = m.colorbar(c)

q  = m.quiver(    x[::3,::3], y[::3,::3], \
        field_ref_case_X_plot[::3, ::3], field_ref_case_Y_plot[::3, ::3], \
        scale = 3.0)

text_data = 'min = '  + str(round(field_min_ERS_TAU, 2)) + ', ' + \
            'max = '  + str(round(field_max_ERS_TAU, 2))

ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)



#PLOT DIFFERENCE
ax = f.add_subplot(3,1,3)

#ax.set_title(casename + ' - ' + ref_case)
ax.set_title('Difference')

field_diff_XY = field_XY - field_ref_case_XY

field_diff_max_TAU = numpy.ma.max(field_diff_XY)
field_diff_min_TAU = numpy.ma.min(field_diff_XY)


#Computing levels using mean and standard deviation
num         = 11
max_plot    = round_to_first(3.0 * numpy.ma.std(field_diff_XY))
levels_diff = numpy.linspace(-max_plot, max_plot, num = num)

print('For difference plot: ')
print('mean, stddev, max_plot: ', numpy.ma.mean(field_diff_XY),
      numpy.ma.std(field_diff_XY), max_plot)
print('min, max: ', numpy.ma.min(field_diff_XY), numpy.ma.max(field_diff_XY))
print('contour levels: ', levels)

#Computing difference vectors
field_diff_X = field_X_plot - field_ref_case_X_plot
field_diff_Y = field_Y_plot - field_ref_case_Y_plot

m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c')

m.drawcoastlines()

c  = m.contourf(x, y, field_diff_XY, \
        cmap = 'seismic', \
        levels = levels_diff, \
        extend = 'both')

cb = m.colorbar(c)

q  = m.quiver(    x[::3,::3], y[::3,::3], \
        field_diff_X[::3, ::3], field_diff_Y[::3, ::3], \
        scale = 1.0)

text_data = 'min = '  + str(round(field_diff_min_TAU, 2)) + ', ' + \
            'max = '  + str(round(field_diff_max_TAU, 2))

ax.text(0, -100, text_data, transform = ax.transData, fontsize = 10)

#SAVING PLOT
mpl.rcParams['savefig.dpi']=300

outfile = plots_dir + '/' + casename + '-' + ref_case + '_' \
                   + field_name + '_climo_' + season + '.png'

plt.savefig(outfile)

#plt.show()



