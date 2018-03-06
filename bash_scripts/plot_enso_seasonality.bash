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

regs=('Nino3' 'Nino3.4' 'Nino4')
names=('Nino3' 'Nino3.4' 'Nino4')

index_set_name=NINO


# Generate plots for each field

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

	python ${coupled_diags_home}/python/plot_multiple_index_seasonality.py -d True --indir $scratch_dir \
							-c $casename \
							-f $var \
							--begin_yr $begin_yr \
							--end_yr $end_yr \
							--interp_grid $interp_grid \
							--interp_method $interp_method \
							--ref_begin_yr $ref_begin_yr \
							--ref_end_yr $ref_end_yr \
							--ref_case_dir $ref_scratch_dir \
							--ref_case $ref_casename \
							--ref_interp_grid $ref_interp_grid \
							--ref_interp_method $ref_interp_method \
							--begin_month 0 \
							--end_month 11 \
							--aggregate 0 \
							--regs ${regs[@]} \
							--names ${names[@]} \
							--index_set_name $index_set_name \
							--no_ann 1 \
							--stdize 0 \
							--plots_dir $plots_dir >& $log_dir/plot_seasonality_${casename}_${var}_$index_set_name.log &
        exstatus=$?
        if [ $exstatus -ne 0 ]; then
          echo
          echo "Failed plotting Nino index seasonality for var=$var"
          exit 1
        fi

done

echo
echo Waiting for jobs to complete ...
echo

wait
echo ... Done.
echo
