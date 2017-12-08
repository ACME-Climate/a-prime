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


def get_climo_filename(    indir,
            casename,
            field_name,
            season,
            begin_yr,
            end_yr,
            interp_grid,
            interp_method):

    if interp_grid == '0':
        file_name = indir + '/' + casename + '_' + season + '_' +\
                'climo.' + field_name + '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'
    else:
        file_name = indir + '/' + casename + '_' + season + '_' + \
                'climo.' + interp_grid + '_' + interp_method + \
                '.' + field_name + '.' + str(begin_yr) + '-' + str(end_yr) + '.nc'


    print("file_name: ", file_name)


    try:
        f     = Dataset(file_name, "r")

    except (RuntimeError,IOError):
        print()
        print(file_name, " not found!")

        if interp_grid == '0':
            file_name = indir + '/' + casename + '_' + season + '_' +\
                'climo' + '.nc'
        else:
            file_name = indir + '/' + casename + '_' + season + '_' + \
                'climo.' + interp_grid + '_' + interp_method + \
                '.nc'

        print()
        print("Using file: ", file_name)
        print()

    return file_name
