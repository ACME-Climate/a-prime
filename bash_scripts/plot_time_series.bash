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

# Read in variable list for plotting climatologies  diagnostics
if [ "$ref_case" == "obs" ]; then
  source ${coupled_diags_home}/bash_scripts/var_list_time_series_model_vs_obs.bash
else
  source ${coupled_diags_home}/bash_scripts/var_list_time_series_model_vs_model.bash
fi

n_var=${#var_set[@]}

regs=('global' 'NH_high_lats' 'NH_mid_lats' 'tropics' 'SH_mid_lats' 'SH_high_lats')
names=('Global' '90N-50N' '50N-20N' '20N-20S' '20S-50S' '50S-90S')

# Generate plots for each field
k=0
while [ $k -lt $n_var ]; do
   var="${var_set[$k]}"
   interp_grid="${interp_grid_set[$k]}"
   interp_method="${interp_method_set[$k]}"

   echo
   echo "$casename $var"
   echo

   if [ "$ref_case" == "obs" ]; then
     ref_casename="$interp_grid"
     ref_interp_grid=0
     ref_interp_method=0
   else
     ref_casename="$ref_case"
     ref_interp_grid="$interp_grid"
     ref_interp_method="$interp_method"
   fi

   python ${coupled_diags_home}/python/plot_multiple_reg_seasonal_avg.py \
			--indir $scratch_dir \
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
			--begin_month 0 \
			--end_month 11 \
			--aggregate 1 \
			--regs ${regs[@]} \
			--names ${names[@]} \
			--plots_dir $plots_dir >& $log_dir/plot_time_series_${casename}_$var.log &
   exstatus=$?
   if [ $exstatus -ne 0 ]; then
     echo
     echo "Failed plotting timeseries plots for var=$var"
     exit 1
   fi

   k=$((k+1))
done

echo
echo "Waiting for jobs to complete ..."

wait

echo "...Done."
echo
