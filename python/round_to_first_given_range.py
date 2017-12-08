#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import math

def round_to_first_given_range(x, range_x):
    if x != 0:
        return round(x, -int(math.floor(math.log10(abs(range_x)))))
    else:
        return 0

