#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals
from netCDF4 import Dataset
from get_reg_box import get_reg_box
from get_climo_filename import get_climo_filename
from get_derived_var_expr import get_derived_var_expr
import numpy
from sympy import *

def read_climo_file (indir, \
             casename, \
             season, \
             field_name, \
             begin_yr, \
             end_yr, \
             interp_grid, \
             interp_method, \
             reg, \
             debug = False):

    file_name = get_climo_filename(    indir,
                    casename,
                    field_name,
                    season,
                    begin_yr,
                    end_yr,
                    interp_grid,
                    interp_method)

    try:
        f = Dataset(file_name, "r")
        field_temp = f.variables[field_name]
        lat = f.variables['lat'][:]
        lon = f.variables['lon'][:]

        try:
            area = f.variables['area'][:]
        except:
            gw = f.variables['gw'][:]

        try:
            units = field_temp.units
        except AttributeError:
            units = field_temp.lunits

        field = field_temp[:]
        f.close()

    except:

        print()
        print(file_name, 'not found! Checking derived variables list for ',
              field_name)

        var_expr, var_expr_numpy = get_derived_var_expr(field_name)

        for i, field_name_temp in enumerate(var_expr.atoms(Symbol)):

            print(field_name_temp)
            field_name_temp_str = str(field_name_temp)
            print(field_name_temp_str)

            file_name_temp = get_climo_filename(     indir,
                                casename,
                                field_name_temp_str,
                                season,
                                begin_yr,
                                end_yr,
                                interp_grid,
                                interp_method)

            f = Dataset(file_name_temp, "r")

            field_temp = f.variables[field_name_temp_str]

            print('field_temp.shape: ', field_temp.shape)

            if i == 0:
                field_list = [field_temp[:]]
                units = field_temp.units
                lat = f.variables['lat'][:]
                lon = f.variables['lon'][:]

                try:
                    area = f.variables['area'][:]
                except:
                    gw = f.variables['gw'][:]

            else:
                field_list.append(field_temp[:])

            f.close()

        print()
        print('field_list length: ', len(field_list))

        field = var_expr_numpy(*field_list)
        print(__name__, 'field.shape: ', field.shape)

    print(__name__, 'field.shape: ', field.shape)
    print(field)


    nlon = lon.shape[0]
    nlat = lat.shape[0]


    #Getting area tile from gw if "area" is not available in the climo file

    if 'gw' in locals():
        print(__name__, 'Computing area weights from gw')

        area_tile = numpy.tile(gw[:], (nlon))
        area_transpose = numpy.reshape(area_tile, (nlon, nlat))

        area = numpy.transpose(area_transpose)


    #Getting the requested region

    lat_ll, lat_ul, lon_ll, lon_ul = get_reg_box(reg)

    print()
    print(__name__, 'lat_ll, lat_ul, lon_ll, lon_ul: ', lat_ll, lat_ul, lon_ll,
          lon_ul)
    print(__name__, 'lat: ', lat)
    print(__name__, 'type(lat[:]): ', type(lat[:]))

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

    if debug: print()
    if debug: print(__name__, 'lat_reg: ', lat_reg_boolean)
    if debug: print(__name__, 'lon_reg: ', lon_reg_boolean)
    if debug: print(__name__, 'lat_index_reg.shape: ', lat_index_reg.shape)
    if debug: print(__name__, 'lat_index_reg: ', lat_index_reg)
    if debug: print(__name__, 'lon_index_reg: ', lon_index_reg)
    if debug: print(__name__, 'type(field): ', type(field))

    #Mulitdimensional indexing with numpy require indexes to be multidimensional arrays
    #Used here only for derived variables like RESTOM

    if isinstance(field, numpy.ndarray):
        if field.ndim == 2:
            field_in = field[lat_index_reg[:, None],lon_index_reg[None, :]]
        if field.ndim == 3:
            field_in = field[0,lat_index_reg[:, None],lon_index_reg[None, :]]


        #Multidimensional indexing with netcdf variables require 1d index variables
    #Used here for variables that are available in netcdf files

    else:
        if field.ndim == 2:
            field_in = field[lat_index_reg,lon_index_reg]
        if field.ndim == 3:
            field_in = field[0,lat_index_reg,lon_index_reg]


    if isinstance(area, numpy.ndarray):
        area_reg = area[lat_index_reg[:, None],lon_index_reg[None, :]]
    else:
        area_reg = area[lat_index_reg,lon_index_reg]


    print(__name__, "field_in.shape: ", field_in.shape)

    if field_name[0:4] == 'PREC' and units == 'm/s':
        print('A precipitation field in m/s units! Changing units from m/s to '
              'mm/day!...')
        field_in = field_in * 86400.0 * 1000.0
        units = 'mm/day'

    if field_name[0:2] == 'TS' and units == 'K':
        print('A temperature field in K units! Changing units from K to C!...')
        field_in = field_in - 273.15
        units = 'C'

    if field_name[0:3] == 'SST' and units == 'K':
        print('A temperature field in K units! Changing units from K to C!...')
        field_in = field_in - 273.15
        units = 'C'

    if field_name[0:3] == 'TAU' and casename != 'ERS':
        print('Flipping sign of atm model wind stress values ...')
        field_in = -field_in

    return field_in, lat_reg, lon_reg, area_reg, units
