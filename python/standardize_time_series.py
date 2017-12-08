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

def standardize_time_series(field):

    field_stddize = (field - field.mean(axis = 0))/field.std(axis = 0)

    return field_stddize

