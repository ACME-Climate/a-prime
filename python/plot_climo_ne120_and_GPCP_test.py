#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib as mpl

import math
import numpy
from netCDF4 import Dataset

from get_season_name import get_season_name

from optparse import OptionParser


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

parser.add_option("--GPCP_dir", dest = "GPCP_dir",
                    help = "filepath to GPCP directory")

parser.add_option("--plots_dir", dest = "plots_dir",
                    help = "filepath to GPCP directory")

(options, args) = parser.parse_args()

indir       = options.indir
casename    = options.casename
field_name  = options.field_name
begin_yr    = options.begin_yr
end_yr      = options.end_yr
begin_month = options.begin_month
end_month   = options.end_month
GPCP_dir    = options.GPCP_dir
plots_dir   = options.plots_dir

#Get filename

if field_name == 'PRECT':
    file_name_PRECC = indir + '/' + casename + \
                '.climo.' + str(begin_month) + '_' + str(end_month) + \
                '.GPCP_conservative_mapping.' + 'PRECC.nc'

    print("file_name: ", file_name_PRECC)


    f_PRECC = Dataset(file_name_PRECC, "r")


    field_PRECC = f_PRECC.variables['PRECC']
    lat = f_PRECC.variables['lat']
    lon = f_PRECC.variables['lon']
    units = field_PRECC.units

    file_name_PRECL = indir + '/' + casename + \
                '.climo.' + str(begin_month) + '_' + str(end_month) + \
                '.GPCP_conservative_mapping.' + 'PRECL.nc'

    print("file_name: ", file_name_PRECL)


    f_PRECL = Dataset(file_name_PRECL, "r")


    field_PRECL = f_PRECL.variables['PRECL']

    field = field_PRECC[:, :] + field_PRECL[:, :]

else:
    file_name = indir + '/' + casename + \
                '.climo.' + str(begin_month) + '_' + str(end_month) + \
            '.GPCP_conservative_mapping.' + field_name + '.nc'

    print("file_name: ", file_name)


    f = Dataset(file_name, "r")


    field = f.variables[field_name]
    lat = f.variables['lat']
    lon = f.variables['lon']
    units = field.units

print('field.shape: ', field.shape)


season = get_season_name(begin_month, end_month)

file_GPCP = GPCP_dir + '/' + 'GPCP_' + season + '_climo.nc'

print("Using GPCP file: ", file_GPCP)

f_GPCP = Dataset(file_GPCP, "r")

field_GPCP = f_GPCP.variables[field_name]




plt.subplot(1,1,1)

plt.suptitle(field_name + ' (' + units + ') ' + season)

plt.title(casename)

m = Basemap(projection='cyl',llcrnrlat=-90.0,urcrnrlat=90.0,\
            llcrnrlon=0.0,urcrnrlon=360.0,resolution='c')

m.drawcoastlines()

lons, lats = numpy.meshgrid(lon,lat)
x, y = m(lons,lats)

field_diff = field[:, :] - field_GPCP[0, :, :]


m.drawcoastlines()

clevs = [-3,-2.5, -2,-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
#c = m.contourf(x, y, field_diff[:, :], clevs, cmap = 'bwr', extend = 'both', corner_mask='legacy')
#cb = m.colorbar()
#c = m.contour(x, y, field_diff[:, :], clevs, cmpa = 'bwr', extend = 'both')

c = m.imshow(field_diff, cmap = 'seismic', vmin = -5.0, vmax = 5.0, filternorm = 0, interpolation = 'nearest')
cb = m.colorbar(extend = 'both')

c = m.contour(x, y, field_diff[:, :], clevs, cmpa = 'bwr', extend = 'both')

mpl.rcParams['savefig.dpi']=300

outfile = plots_dir + '/' + casename + '_' \
                   + field_name + '_climo_GPCP_' + season + '.png'

plt.savefig(outfile)

#plt.show()



