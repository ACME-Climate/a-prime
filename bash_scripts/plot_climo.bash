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
ref_begin_yr=$7
ref_end_yr=$8

# Read in variable list for plotting climatologies  diagnostics
if [ "$ref_case" == "obs" ]; then
  source ${coupled_diags_home}/bash_scripts/var_list_climo_model_vs_obs.bash
else
  source ${coupled_diags_home}/bash_scripts/var_list_climo_model_vs_model.bash
fi

n_var=${#var_set[@]}

# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}

# Generate plots for each field and season
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

   ns=0
   while [ $ns -lt $n_seasons ]; do
      begin_month=${begin_month_set[$ns]}
      end_month=${end_month_set[$ns]}
      season_name="${season_name_set[$ns]}"

      if [ "$var" == "TAU" ]; then
        python ${coupled_diags_home}/python/plot_climo_vector.py \
			--indir $scratch_dir \
			-c $casename \
			-f $var \
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
			--plots_dir $plots_dir >& $log_dir/plot_climo_$casename-$ref_casename.$var.$season_name.log &
        exstatus=$?
        if [ $exstatus -ne 0 ]; then
          echo
          echo "Failed plotting $var climatology"
          exit 1
        fi

      else
        python ${coupled_diags_home}/python/plot_climo.py \
			--indir $scratch_dir \
			-c $casename \
			-f $var \
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
			--plots_dir $plots_dir >& $log_dir/plot_climo_$casename-$ref_casename.$var.$season_name.log &
        exstatus=$?
        if [ $exstatus -ne 0 ]; then
          echo
          echo "Failed plotting $var climatology"
          exit 1
        fi
      fi

      ns=$((ns+1))
   done

   k=$((k+1))
done

echo
echo "Waiting for jobs to complete ..."
echo

wait
