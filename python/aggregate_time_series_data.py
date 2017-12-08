#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
# to compute mean (aggregates) of time series data at different intervals,
# for e.g. to compute annual mean from daily timeseries data.

from __future__ import absolute_import, division, print_function, \
    unicode_literals
import numpy

def aggregate_time_series_data(data, aggregate_size, wgts, debug = False):
    nt = data.shape[0]

    n_aggregates = int(nt // aggregate_size)

    # concatenating tuples to create shape for aggregate_data
    agg_shape = (n_aggregates,) + data.shape[1:]

    print(__name__, 'agg_shape: ', agg_shape)

    aggregate_data = numpy.ma.zeros((agg_shape))
    print("aggregate_data.shape: ", aggregate_data.shape)

    if data.ndim == 1:
        for i in range(0, n_aggregates):
            aggregate_data[i] = numpy.ma.average(data[i*aggregate_size:(i+1) * aggregate_size], axis = 0, weights = wgts)

    else:
        for i in range(0, n_aggregates):
            aggregate_data[i, ::] = numpy.ma.average(data[i*aggregate_size:(i+1) * aggregate_size, ::], axis = 0, weights = wgts)

    print("aggregate_data.shape: ", aggregate_data.shape)

    return aggregate_data
