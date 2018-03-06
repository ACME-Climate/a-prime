#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

#PBS -q batch
#PBS -l nodes=1
#PBS -l walltime=01:00:00
#PBS -A cli115
#PBS -N aprime_ocnice_diags
#PBS -o aprime_ocnice_diags.o$PBS_JOBID
#PBS -e aprime_ocnice_diags.e$PBS_JOBID
#PBS -V

cd $PBS_O_WORKDIR

# prefix to run a serial job on a single node on edison
export command_prefix="aprun -b -N 1 -n 1"

${coupled_diags_home}/bash_scripts/aprime_ocnice_diags.bash

echo
echo "**** The following batch job will be submitted to cp files to www_dir *if* the ocn/ice diags are completed"
echo "**** jobID:"
batch_script="${coupled_diags_home}/bash_scripts/batch_update_wwwdir.$machname.bash"
qsub -W depend=afterok:$PBS_JOBID $batch_script
