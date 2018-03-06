#!/bin/bash -l
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

#SBATCH --partition=regular
#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --account=acme
#SBATCH --job-name=aprime_atm_diags
#SBATCH --output=aprime_atm_diags.o%j
#SBATCH --error=aprime_atm_diags.e%j
#SBATCH -L cscratch1,SCRATCH,project
#SBATCH --export=ALL

cd $SLURM_SUBMIT_DIR

export OMP_NUM_THREADS=1

srun -N 1 -n 1 ${coupled_diags_home}/bash_scripts/aprime_atm_diags.bash

exitCode=`sacct --jobs=$SLURM_JOB_ID --format=ExitCode | awk '{if (NR==3) printf "%d",$1}'`
if [ $exitCode -eq 0 ]; then
  # Update www/plots directory with newly generated plots
  cp -u $plots_dir/* $www_dir/$plots_dir_name
  chmod -R ga+rX $www_dir/$plots_dir_name

  echo
  echo "Updated atm plots in website directory: $www_dir/$plots_dir_name"
  echo
else
  echo
  echo "Something went wrong with the atm diagnostics: website plots NOT updated!"
  echo
fi
