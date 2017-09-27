#!/bin/bash

# GENERATE OCEAN DIAGNOSTICS

# Initialize MPAS-Analysis code
export GIT_DISCOVERY_ACROSS_FILESYSTEM=true
export tmp_currentdir="`pwd`"
export tmp_gittopdir="`git rev-parse --show-toplevel`"
cd $tmp_gittopdir
#
git submodule update --init
#
echo
echo "MPAS-Analysis submodule: "`git submodule status`
cd $tmp_currentdir
unset tmp_currentdir tmp_gittopdir

export config_file="$log_dir/config.ocnice.$uniqueID"
python python/setup_ocnice_config.py
if [ $? -ne 0 ]; then
  echo "Failed to build config.ocnice"
  exit 1
fi

python python/MPAS-Analysis/run_analysis.py $config_file
