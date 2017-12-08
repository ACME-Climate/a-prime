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
from round_to_first import round_to_first
from round_to_first_given_range import round_to_first_given_range

def compute_contour_levels(field, n_stddev, num_levels):

    if numpy.ma.min(field[:]) < 0 and numpy.ma.max(field[:]) > 0:
        max_plot_temp = numpy.ma.mean(field) + n_stddev * numpy.ma.std(field)
        range_plot = 2 * max_plot_temp
        max_plot    = round_to_first_given_range(x = max_plot_temp, range_x = range_plot)

        print(__name__, 'max_plot_temp: ', max_plot_temp)
        print(__name__, 'max_plot: ', max_plot)

        levels = numpy.linspace(-max_plot, max_plot, num = num_levels)

    else:
        max_plot_temp = numpy.ma.mean(field[:]) + \
                  n_stddev * numpy.ma.std(field[:])

        if max_plot_temp > numpy.ma.max(field[:]):
            max_plot_temp = numpy.ma.max(field[:])

        min_plot_temp = numpy.ma.mean(field[:]) - \
                      n_stddev * numpy.ma.std(field[:])

        if min_plot_temp < numpy.ma.min(field[:]):
            min_plot_temp = numpy.ma.min(field[:])

        range_plot = max_plot_temp - min_plot_temp

        max_plot = round_to_first_given_range(max_plot_temp, range_x = range_plot)
        min_plot = round_to_first_given_range(min_plot_temp, range_x = range_plot)

        print(__name__, 'min_plot_temp, max_plot_temp: ', min_plot_temp,
              max_plot_temp)
        print(__name__, 'min_plot, max_plot: ', min_plot, max_plot)

        levels = numpy.linspace(min_plot, max_plot, num = num_levels)

    print('contour levels: ', levels)

    return levels
