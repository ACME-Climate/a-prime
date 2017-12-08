#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
from __future__ import absolute_import, division, print_function, \
    unicode_literals

def get_reg_box(reg):

    if reg == "global":
        lat_ll, lat_ul, lon_ll, lon_ul = -90, 90, 0, 360

    if reg == "NH":
        lat_ll, lat_ul, lon_ll, lon_ul = 0, 90, 0, 360

    if reg == "SH":
        lat_ll, lat_ul, lon_ll, lon_ul = -90, 0, 0, 360

    if reg == "SH_high_lats":
        lat_ll, lat_ul, lon_ll, lon_ul = -90, -50, 0, 360

    if reg == "SH_mid_lats":
        lat_ll, lat_ul, lon_ll, lon_ul = -50, -20, 0, 360

    if reg == "tropics":
        lat_ll, lat_ul, lon_ll, lon_ul = -20, 20, 0, 360

    if reg == "NH_mid_lats":
        lat_ll, lat_ul, lon_ll, lon_ul = 20, 50, 0, 360

    if reg == "NH_high_lats":
        lat_ll, lat_ul, lon_ll, lon_ul = 50, 90, 0, 360

    if reg == "Nino3":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 210, 270

    if reg == "Nino3.4":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 190, 240

    if reg == "Nino4":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 160, 210

    if reg == "Tropical_Pacific":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 160, 270

    if reg == "Greater_Tropical_Pacific":
        lat_ll, lat_ul, lon_ll, lon_ul = -30, 30, 120, 290

    if reg == "EPAC":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 230, 280

    if reg == "INDO":
        lat_ll, lat_ul, lon_ll, lon_ul = -5, 5, 90, 140

    return (lat_ll, lat_ul, lon_ll, lon_ul)


