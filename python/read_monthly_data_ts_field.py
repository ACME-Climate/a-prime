#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals
import numpy
from netCDF4 import Dataset
from get_season_months_index import get_season_months_index
from get_reg_box import get_reg_box

def read_monthly_data_ts_field(indir,
             casename,
             field_name,
             begin_yr,
             end_yr,
             begin_month,
             end_month,
             reg,
             interp_method,
             interp_grid,
             debug = False):

    #Get filename
    #indir = '/lustre/atlas1/cli049/proj-shared/salil/archive/'

    print(indir, casename, interp_grid,interp_method, field_name)

    if casename == 'COREv2' or casename == 'COREv2_flux' or casename == 'NCEP2' or casename == 'NCEP2_surface' or casename == 'HadISST_ts' or casename == 'HadOIBl':
        cam_text = '.'
        begin_yr = 1979
        end_yr   = 2006
    else:
        cam_text = '.cam.h0.'

    if casename == 'HadOIBl':
        begin_yr = 1979
        end_yr = 1998

    if interp_grid == '0':
        file_name = indir + '/' + casename + cam_text \
             + field_name + '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'
    else:
        file_name = indir + '/' + casename + cam_text \
            + interp_grid + '_' + \
            interp_method + '.' + field_name + '.' + str(begin_yr) + '-' + str(end_yr) +'.nc'

    print("file_name: ", file_name)


    f = Dataset(file_name, "r")


    field = f.variables[field_name]
    units = field.units

    lat = f.variables['lat']
    lon = f.variables['lon']
    area = f.variables['area']

    nt = field.shape[0]
    nyrs = nt // 12


    if end_month < begin_month:
        n_months_season_yr1 = 12 - begin_month
        n_months_season_yr2 = end_month + 1
        n_months_season = n_months_season_yr1 + n_months_season_yr2

        index_months_temp, n_months_season = get_season_months_index(begin_month, end_month)

        index_months_tile = numpy.tile(index_months_temp, nyrs-1)

        if debug:
            print(__name__, 'index_months_tile.shape: ',
                  index_months_tile.shape)

        if debug:
            print(__name__, 'index_months_tile: ', index_months_tile)

        index_yr_temp = numpy.arange(nyrs) * 12
        index_yr_repeat = numpy.repeat(index_yr_temp, n_months_season)

        index_yr_repeat = index_yr_repeat[n_months_season_yr2:nyrs*n_months_season-n_months_season_yr1]

        if debug:
            print(__name__, 'index_yr_repeat.shape: ', index_yr_repeat.shape)
        if debug:
            print(__name__, 'index_yr_repeat: ', index_yr_repeat)

        index_time = index_months_tile + index_yr_repeat

    else:
        n_months_season = end_month - begin_month + 1

        index_months_temp = numpy.arange(begin_month, end_month+1)

        index_months_tile = numpy.tile(index_months_temp, nyrs)

        if debug:
            print(__name__, 'index_months_tile.shape: ',
                  index_months_tile.shape)
        if debug:
            print(__name__, 'index_months_tile: ', index_months_tile)


        index_yr_temp = numpy.arange(nyrs) * 12
        index_yr_repeat = numpy.repeat(index_yr_temp, n_months_season)

        if debug:
            print(__name__, 'index_yr_repeat: ', index_yr_repeat)

        index_time = index_months_tile + index_yr_repeat

    if debug:
        print(__name__, 'index_time: ', index_time)

    nlon = lon.shape[0]
    nlat = lat.shape[0]

    lat_ll, lat_ul, lon_ll, lon_ul = get_reg_box(reg)

    print(__name__, 'lat_ll, lat_ul, lon_ll, lon_ul: ', lat_ll, lat_ul, lon_ll,
          lon_ul)

    lat_reg_boolean = numpy.logical_and(lat[:]>=lat_ll, lat[:]<=lat_ul)
    lat_index_reg   = numpy.asarray(numpy.where(lat_reg_boolean))[0, :]
    lat_reg         = lat[lat_reg_boolean]

    #The following also works:
    #lat_index = numpy.arange(0,nlat)
    #lat_index_reg = lat_index[lat_reg_boolean]

    if lon_ll > lon_ul:
        lon_reg_boolean = numpy.logical_or(lon[:]>=lon_ll, lon[:] <= lon_ul)
    else:
        lon_reg_boolean = numpy.logical_and(lon[:]>=lon_ll, lon[:] <= lon_ul)

    lon_index_reg   = numpy.asarray(numpy.where(lon_reg_boolean))[0, :]
    lon_reg         = lon[lon_reg_boolean]

    #lon_index = numpy.arange(0,nlon)
    #lon_index_reg = lon_index[lon_reg_boolean]

    if debug: print(__name__, 'lat_reg: ', lat_reg_boolean)
    if debug: print(__name__, 'lon_reg: ', lon_reg_boolean)
    if debug: print(__name__, 'lat_index_reg.shape: ', lat_index_reg.shape)
    if debug: print(__name__, 'lat_index_reg: ', lat_index_reg)
    if debug: print(__name__, 'lon_index_reg: ', lon_index_reg)

    if debug: print(__name__, 'field[0, :, :]: ', field[0, :, :])

    field_in = field[index_time,lat_index_reg,lon_index_reg]
    area_reg = area[lat_index_reg, lon_index_reg]

    print(__name__, 'field.shape: ', field.shape)
    print(__name__, 'field_in.shape: ', field_in.shape)
    print('')

    if field_name[0:4] == 'PREC' and field.units == 'm/s':
        print('A precipitation field in m/s units! Changing units from m/s '
              'to mm/day!...')
        field_in = field_in * 86400.0 * 1000.0
        units = 'mm/day'

    if field_name[0:2] == 'TS' and field.units == 'K':
        print('A temperature field in K units! Changing units from K to C!...')
        field_in = field_in - 273.15
        units = 'C'

    if field_name[0:2] == 'TS' and field.units == 'degK':
        print('A temperature field in degK units! Changing units from K to '
              'C!...')
        field_in = field_in - 273.15
        units = 'C'

    if field_name[0:3] == 'SST' and field.units == 'K':
        print('A temperature field in K units! Changing units from K to C!...')
        field_in = field_in - 273.15
        units = 'C'

    if field_name[0:3] == 'TAU' and casename != 'ERS' and casename != 'COREv2_flux':
        print('Flipping sign of atm model wind stress values ...')
        field_in = -field_in

    if field_name == 'LHFLX' and casename == 'COREv2_flux':
        print('Flipping sign of COREv2_flux LHFLX to define positive values '
              'for upward fluxes (ocean to atm) ...')
        field_in = -field_in

    if field_name == 'SHFLX' and casename == 'COREv2_flux':
        print('Flipping sign of COREv2_flux SHFLX to define positive values '
              'for upward fluxes (ocean to atm) ...')
        field_in = -field_in

    if debug:
        print(__name__, 'field_in[0,:,:]: ', field_in[0, :, :])

    return (field_in, lat_reg, lon_reg, area_reg, units)
