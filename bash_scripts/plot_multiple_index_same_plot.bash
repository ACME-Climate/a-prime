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
ref_scratch_dir=$5
ref_case=$6
ref_begin_yr=$7
ref_end_yr=$8
var_list_file=$9

# Read in variable list for plotting climatologies  diagnostics
source $var_list_file

n_var=${#var_set[@]}

index_set_name=SOI_Nino

index_names=('EQSOI' 'Nino3.4')
field_names=('PSL' 'TS')

scratch_dir_index=($scratch_dir $scratch_dir)
casename_index=($casename $casename)

ref_scratch_dir_index=($ref_scratch_dir $ref_scratch_dir)
ref_case_index=($ref_case $ref_case)

interp_grid=(0 0)
interp_method=(0 0)

ref_casename=(0 0)
ref_interp_grid=(0 0)
ref_interp_method=(0 0)

n_index=${#index_names[@]}


# Get grid information about the indices
for ((i=0; i<$n_index; i++)); do 
        for ((k=0; k<$n_var; k++)); do 
                if [ "${field_names[$i]}" == "${var_set[$k]}" ]; then
			interp_grid[$i]=${interp_grid_set[$k]}
			interp_method[$i]=${interp_method_set[$k]}

			if [ $ref_case != obs ]; then
				ref_interp_grid[$i]=${interp_grid_set[$k]}
				ref_interp_method[$i]=${interp_method_set[$k]}
			else
				ref_case_index[$i]=${interp_grid_set[$k]}
			fi

		fi
	done
done


# Generate plots for each field

python ${coupled_diags_home}/python/plot_multiple_index_same_plot.py -d True --indir ${scratch_dir_index[@]} \
						-c ${casename_index[@]} \
						-f ${field_names[@]} \
						--begin_yr $begin_yr \
						--end_yr $end_yr \
						--interp_grid ${interp_grid[@]} \
						--interp_method ${interp_method[@]} \
						--ref_begin_yr $ref_begin_yr \
						--ref_end_yr $ref_end_yr \
						--ref_case_dir ${ref_scratch_dir_index[@]} \
						--ref_case ${ref_case_index[@]} \
						--ref_interp_grid ${ref_interp_grid[@]} \
						--ref_interp_method ${ref_interp_method[@]} \
						--begin_month 0 \
						--end_month 11 \
						--aggregate 0 0\
						--index_names ${index_names[@]} \
						--no_ann 1 1\
						--stdize 0 0\
						--plots_dir $plots_dir >& $log_dir/plot_time_series_${casename}_$index_set_name.log &
exstatus=$?
if [ $exstatus -ne 0 ]; then
  echo
  echo "Failed plotting Nino indeces in the same plot"
  exit 1
fi



echo
echo Waiting for jobs to complete ...
echo

wait
echo ... Done.
echo
 	


