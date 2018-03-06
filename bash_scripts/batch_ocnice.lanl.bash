#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --account=climateacme
#SBATCH --job-name=aprime_ocnice_diags
#SBATCH --output=aprime_ocnice_diags.o%j
#SBATCH --error=aprime_ocnice_diags.e%j
#SBATCH --qos=interactive
#SBATCH --export=ALL

cd $SLURM_SUBMIT_DIR

# prefix to run a serial job on a single node on edison
export command_prefix=""

${coupled_diags_home}/bash_scripts/aprime_ocnice_diags.bash

exitCode=`sacct --jobs=$SLURM_JOB_ID --format=ExitCode | awk '{if (NR==3) printf "%d",$1}'`
if [ $exitCode -eq 0 ]; then
  # Update www/plots directory with newly generated plots
  rsync -augltq $plots_dir/* $www_dir/$plots_dir_name
  chmod -R ga+rX $www_dir/$plots_dir_name

  echo
  echo "Updated ocn/ice plots in website directory: $www_dir/$plots_dir_name"
  echo
else
  echo
  echo "Something went wrong with the ocn/ice diagnostics: website plots NOT updated!"
  echo
fi
