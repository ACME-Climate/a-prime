#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
# Compute the climatology for a case
# Uses MPI

from __future__ import absolute_import, division, print_function, \
    unicode_literals
import numpy
from   scipy.io import netcdf
from   netCDF4  import Dataset
#from   mpi4py   import MPI
import math
import time
from   optparse import OptionParser

from get_season_name import get_season_name

#Parse options
parser = OptionParser(usage = "mpirun [options] python %prog [options]")

parser.add_option("--indir", dest = "indir",
                    help = "archive directory path")

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

(options, args) = parser.parse_args()

indir       = options.indir
casename    = options.casename
field_name  = options.field_name
begin_yr    = options.begin_yr
end_yr      = options.end_yr
begin_month = options.begin_month
end_month   = options.end_month


#Get filename

file_name = indir + '/' + casename + '.cam.h0.' + field_name + \
        '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'

print("file_name: ", file_name)

f = Dataset(file_name, 'r')

field = f.variables[field_name]
lat = f.variables['lat']
lon = f.variables['lon']

ntime = field.shape[0]
ncol  = field.shape[1]

print("field.shape: ", field.shape)
print("field.units: ", field.units)

t0 = time.clock()

begin_index = 0
end_index = ncol

local_field = field[:,begin_index:end_index]

print("file read!, time taken: ", str(time.clock()-t0))

nyrs = ntime // 12
clim_field = numpy.zeros((12, ncol))


#Computing the climatology of each month
for month in range(0, 12):
    i = numpy.arange(0,nyrs) * 12 + month
    # print(i
    clim_field[month, :] = numpy.mean(field[i, :], axis = 0)

units_out = field.units

if field_name[0:4] == 'PREC':
    print('A precipitation field! Changing units to mm/day!...')
    clim_field = clim_field * 86400.0 * 1000.0
    units_out = 'mm/day'

seasonal_clim = numpy.zeros((ncol))
days_in_month = numpy.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

print('begin_month, end_month:', begin_month, end_month)

#Setting up months in the prescribed season
if (begin_month <= end_month):
    n_months = end_month - begin_month + 1
    seasonal_index = numpy.arange(begin_month, end_month+1)

else:
    n_months = (11 - begin_month + 1) + (end_month + 1)
    seasonal_index = numpy.zeros((n_months), dtype = numpy.int)

    seasonal_index[0:11-begin_month+1]       = numpy.arange(begin_month, 12)
    seasonal_index[11-begin_month+1:n_months]  = numpy.arange(0, end_month+1)

print("seasonal_index: ", seasonal_index)
print("seasonal_index.shape: ", seasonal_index.shape)
print("clim_field.shape: ", clim_field.shape)

weights = numpy.zeros((n_months))
weights[:] = days_in_month[seasonal_index]
print("weights: ", weights)

#Computing seasonal mean
seasonal_clim[:] = numpy.average(clim_field[seasonal_index, :], axis = 0, weights = weights)

season = get_season_name(begin_month, end_month)

#Writing netcdf file
outfile = indir + '/'+ casename + '_' + season \
            + '_climo.' + field_name + \
        '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'

print("Writing ", outfile)
print("")

f_write = Dataset(outfile, 'w', format = 'NETCDF3_64BIT')

ncol_outfile = f_write.createDimension('ncol', ncol)

field_outfile = f_write.createVariable(field_name, 'f4', ('ncol'))
lat_outfile = f_write.createVariable('lat', 'float64', ('ncol'))
lon_outfile = f_write.createVariable('lon', 'float64', ('ncol'))

field_outfile[:] = seasonal_clim

for ncattr in field.ncattrs():
    field_outfile.setncattr(ncattr, field.getncattr(ncattr))

field_outfile.units = units_out

lat_outfile[:] = lat[:]

for ncattr in lat.ncattrs():
    lat_outfile.setncattr(ncattr, lat.getncattr(ncattr))

lon_outfile[:] = lon[:]
for ncattr in lon.ncattrs():
    lon_outfile.setncattr(ncattr, lon.getncattr(ncattr))

f_write.close()
