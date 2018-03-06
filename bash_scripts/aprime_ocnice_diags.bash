#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
#
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

# GENERATE OCEAN DIAGNOSTICS

export config_file="$log_dir/config.ocnice.$uniqueID"
python ${coupled_diags_home}/python/setup_ocnice_config.py
exstatus=$?
if [ $exstatus -ne 0 ]; then
  echo
  echo "Failed to build config.ocnice"
  exit 1
fi

# run_mpas_analysis should be in the user's path if the mpas_analysis conda
# package has been installed correctly
run_mpas_analysis $config_file
exstatus=$?
if [ $exstatus -ne 0 ]; then
  echo
  echo "Failed some ocean/ice diagnostic tasks"
  exit 1
fi
