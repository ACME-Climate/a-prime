#!/bin/bash 
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

scratch_dir=$1
casename=$2
begin_yr=$3
end_yr=$4
ref_scratch_dir=$5
ref_case=$6
var_list_file=$7

# Read in variable list for plotting climatologies  diagnostics
source $var_list_file

n_var=${#var_set[@]}

reg='Tropical_Pacific'
reg_name='Tropical-Pacific'


# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}


# Generate plots for each field
k=0
while [ $k -lt $n_var ]; do

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

	i=0
	while [ $i -lt $n_seasons ]; do
                begin_month=${begin_month_set[$i]}
                end_month=${end_month_set[$i]}
                season_name=${season_name_set[$i]}

		python ${coupled_diags_home}/python/plot_meridional_avg_climo.py -d True --indir $scratch_dir \
								-c $casename \
								-f $var \
								--begin_yr $begin_yr \
								--end_yr $end_yr \
								--interp_grid $interp_grid \
								--interp_method $interp_method \
								--ref_case_dir $ref_scratch_dir \
								--ref_case $ref_casename \
								--ref_interp_grid $ref_interp_grid \
								--ref_interp_method $ref_interp_method \
								--begin_month $begin_month \
								--end_month $end_month \
								--aggregate 1 \
								--reg $reg \
								--reg_name $reg_name \
								--plots_dir $plots_dir >& $log_dir/plot_meridional_avg_${reg}_${casename}_${var}_$season_name.log &
                exstatus=$?
                if [ $exstatus -ne 0 ]; then
                  echo
                  echo "Failed plotting Nino Tropical Pacific averages for var=$var, season=$season_name"
                  exit 1
                fi

		i=$((i+1))
	done

	k=$((k+1))
done

echo
echo Waiting for jobs to complete ...

wait
echo
echo ... Done
echo
