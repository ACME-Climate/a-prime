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
from sympy import *

def get_derived_var_expr (field_name):


    if field_name == 'PRECT':
        PRECC, PRECL = symbols('PRECC, PRECL')
        var_expr = PRECC + PRECL
    elif field_name == 'RESTOM':
        FSNT, FLNT = symbols('FSNT, FLNT')
        var_expr = FSNT - FLNT
    elif field_name == 'FLNS':
        FLUS, FLDS = symbols('FLUS, FLDS')
        var_expr = FLUS - FLDS
    elif field_name == 'RESSURF':
        FLNS, FSNS, LHFLX, SHFLX = symbols('FLNS, FSNS, LHFLX, SHFLX')
        var_expr = FLNS - FSNS + LHFLX + SHFLX
    else:
        print()
        print('No derived variable list found for ', field_name)

    print
    print(field_name, 'derived from: ', var_expr.atoms(Symbol))

    var_expr_numpy = lambdify(var_expr.atoms(Symbol), var_expr, str("numpy"))

    return var_expr, var_expr_numpy


