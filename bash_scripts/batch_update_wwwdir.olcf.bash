#!/bin/bash

#PBS -q batch
#PBS -l nodes=0
#PBS -l walltime=00:20:00
#PBS -A cli115
#PBS -N aprime_update_wwwdir
#PBS -o aprime_update_wwwdir.o$PBS_JOBID
#PBS -e aprime_update_wwwdir.e$PBS_JOBID
#PBS -V

cd $PBS_O_WORKDIR

# Update www/plots directory with newly generated plots
cp -u $plots_dir/* $www_dir/$plots_dir_name
echo
echo "Updated atm plots in website directory: $www_dir/$plots_dir_name"
echo
