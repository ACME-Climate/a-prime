#!/bin/bash -f 
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

scratch_dir=$1
casename=$2
reg=$3
begin_yr=$4
end_yr=$5
ref_scratch_dir=$6
ref_case=$7
ref_begin_yr=$8
ref_end_yr=$9
var_list_file=${10}

# Read in variable list for plotting climatologies  diagnostics

source $var_list_file

n_var=${#var_set[@]}

# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}


# Generate plots for each field and season

for ((k=0; k<$n_var; k++)); do

        var=${var_set[$k]}
        interp_grid=${interp_grid_set[$k]}
        interp_method=${interp_method_set[$k]}

        echo    
        echo $casename $var
        echo

        if [ $ref_case == obs ]; then
                ref_casename=$interp_grid
                ref_interp_grid=0
                ref_interp_method=0
        else
                ref_casename=$ref_case
                ref_interp_grid=$interp_grid
                ref_interp_method=$interp_method
        fi

        for ((i=0; i<$n_seasons; i++)); do
                begin_month=${begin_month_set[$i]}
                end_month=${end_month_set[$i]}
                season_name=${season_name_set[$i]}


		python ${coupled_diags_home}/python/plot_stddev.py \
			--indir $scratch_dir \
			-c $casename \
			-f $var \
			--reg $reg \
			--begin_month $begin_month \
			--end_month $end_month \
			--begin_yr $begin_yr \
			--end_yr $end_yr \
			--interp_grid $interp_grid \
			--interp_method $interp_method \
			--ref_case_dir $ref_scratch_dir \
			--ref_case $ref_casename \
			--ref_begin_yr $ref_begin_yr \
			--ref_end_yr $ref_end_yr \
			--ref_interp_grid $ref_interp_grid \
			--ref_interp_method $ref_interp_method \
			--plots_dir $plots_dir >& $log_dir/plot_stddev_${reg}_$casename-$ref_casename.$var.$season_name.log &
                exstatus=$?
                if [ $exstatus -ne 0 ]; then
                  echo
                  echo "Failed plotting Nino stddev plots for var=$var, season=$season_name"
                  exit 1
                fi
	done
done

echo
echo Waiting for jobs to complete ...
echo

wait
echo ... Done.
echo
