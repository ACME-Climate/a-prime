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

def aggregate_ts_weighted(ts, bw, wgts = 1, debug = False):

    nt = ts.shape[0]
    n_agg_ts = nt // bw

    if debug:
        print(__name__, 'nyrs_ts: ', n_agg_ts)

    ts_reshape = numpy.reshape(ts, (n_agg_ts, bw))

    if debug:
        print(__name__, 'ts_reshape: ', ts_reshape)

    ts_reshape_wgted = wgts * ts_reshape

    if debug:
        print(__name__, 'ts_reshape_wgted: ', ts_reshape_wgted)

    agg_ts = numpy.sum(ts_reshape_wgted, axis = 1)/numpy.sum(wgts)

    if debug:
        print(__name__, 'area_seasonal_avg: ', agg_ts)

    return agg_ts
