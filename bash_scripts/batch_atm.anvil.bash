#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

#PBS -q acme 
#PBS -l nodes=1
#PBS -l walltime=01:00:00
#PBS -A ACME
#PBS -N aprime_atm_diags
#PBS -o aprime_atm_diags.o$PBS_JOBID
#PBS -e aprime_atm_diags.e$PBS_JOBID
#PBS -V

cd $PBS_O_WORKDIR

${coupled_diags_home}/bash_scripts/aprime_atm_diags.bash

echo
echo "**** The following batch job will be submitted to cp files to www_dir *if* the atm diags are completed"
echo "**** jobID:"
batch_script="${coupled_diags_home}/bash_scripts/batch_update_wwwdir.$machname.bash"
qsub -W depend=afterok:$PBS_JOBID $batch_script
