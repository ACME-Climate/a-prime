#!/bin/bash -l
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

#SBATCH --partition=regular
# change number of nodes to change the number of parallel tasks
# (anything between 1 and the total number of tasks to run)
#SBATCH --nodes=10
#SBATCH --time=01:00:00
#SBATCH --account=acme
#SBATCH --job-name=aprime_ocnice_diags
#SBATCH --output=aprime_ocnice_diags.o%j
#SBATCH --error=aprime_ocnice_diags.e%j
#SBATCH -L cscratch1,SCRATCH,project
#SBATCH --export=ALL

cd $SLURM_SUBMIT_DIR

export OMP_NUM_THREADS=1

# prefix to run a serial job on a single node on edison
export command_prefix="srun -N 1 -n 1"

./bash_scripts/aprime_ocnice_diags.bash

exitCode=`sacct --jobs=$SLURM_JOB_ID --format=ExitCode | awk '{if (NR==3) printf "%d",$1}'`
if [ $exitCode -eq 0 ]; then
  # Update www/plots directory with newly generated plots
  cp -u $plots_dir/* $www_dir/$plots_dir_name
  #chmod a+r $www_dir/$plots_dir_name/*

  echo
  echo "Updated ocn/ice plots in website directory: $www_dir/$plots_dir_name"
  echo
else
  echo
  echo "Something went wrong with the ocn/ice diagnostics: website plots NOT updated!"
  echo
fi
