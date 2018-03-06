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
begin_yr=$3
end_yr=$4
index_field=$5
index_reg=$6
index_reg_name=$7
field_reg=$8
field_reg_name=$9
ref_scratch_dir=${10}
ref_case=${11}
ref_begin_yr=${12}
ref_end_yr=${13}
var_list_file=${14}


# Read in variable list for plotting climatologies  diagnostics
source $var_list_file

n_var=${#var_set[@]}

reg=($field_reg $index_reg)
reg_name=($field_reg_name $index_reg_name)

# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}


# Get grid information about the index field
for ((k=0; k<$n_var; k++)); do
	if [ "${var_set[$k]}" == "$index_field" ]; then
		interp_grid_index=${interp_grid_set[$k]}
		interp_method_index=${interp_method_set[$k]}
	fi	
done


# Generate regression plots for each field against the index 
for ((k=0; k<$n_var; k++)); do

        var=${var_set[$k]}
        interp_grid=${interp_grid_set[$k]}
        interp_method=${interp_method_set[$k]}

	echo	
	echo $casename $var
	echo

	if [ $ref_case == obs ]; then
		ref_casename=($interp_grid $interp_grid_index)
		ref_interp_grid=(0 0)
		ref_interp_method=(0 0)
	else
		ref_casename=($ref_case $ref_case)
		ref_interp_grid=($interp_grid $interp_grid_index)
		ref_interp_method=($interp_method $interp_method_index)
	fi

	for ((i=0; i<$n_seasons; i++)); do
                begin_month=${begin_month_set[$i]}
                end_month=${end_month_set[$i]}
                season_name=${season_name_set[$i]}

		python ${coupled_diags_home}/python/plot_regress_index_field.py -d True --indir $scratch_dir $scratch_dir\
								-c $casename $casename\
								-f $var $index_field\
								--begin_yr $begin_yr \
								--end_yr $end_yr \
								--interp_grid $interp_grid $interp_grid_index\
								--interp_method $interp_method $interp_method_index\
								--ref_begin_yr $ref_begin_yr \
								--ref_end_yr $ref_end_yr \
								--ref_case_dir $ref_scratch_dir $ref_scratch_dir\
								--ref_case ${ref_casename[@]} \
								--ref_interp_grid ${ref_interp_grid[@]} \
								--ref_interp_method ${ref_interp_method[@]} \
								--begin_month $begin_month $begin_month\
								--end_month $end_month $end_month\
								--aggregate 0 \
								--no_ann 1 \
								--stdize 0 \
								--reg ${reg[@]} \
								--reg_name ${reg_name[@]} \
								--plots_dir $plots_dir >& $log_dir/plot_regr_${casename}_${var}_vs_${index_reg_name}_$season_name.log &
                exstatus=$?
                if [ $exstatus -ne 0 ]; then
                  echo
                  echo "Failed plotting Nino regression plots for var=$var, season=$season_name"
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
