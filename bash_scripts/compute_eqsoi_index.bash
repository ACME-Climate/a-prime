#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

archive_dir=$1
scratch_dir=$2
casename=$3
begin_yr=$4
end_yr=$5
var_list_file=$6


# Read in variable list for plotting climatologies  diagnostics
source $var_list_file

n_var=${#var_set[@]}

index_set_name=EQSOI

regs=('EPAC' 'INDO')
names=('EPAC' 'INDO')

# Compute indices
for ((k=0; k<$n_var; k++)); do

	case=$casename
	var=${var_set[$k]}
	interp_grid=${interp_grid_set[$k]}
	interp_method=${interp_method_set[$k]}

	echo
	echo $casename $var
	echo

        if [ $casename == obs ]; then 
                case=${interp_grid[$i]}
                interp_grid=0
                interp_method=0

	fi

	python ${coupled_diags_home}/python/compute_diff_index.py -d True 	--archive_dir $archive_dir \
							--indir $scratch_dir \
							-c $case \
							-f $var \
							--begin_yr $begin_yr \
							--end_yr $end_yr \
							--interp_grid $interp_grid \
							--interp_method $interp_method \
							--begin_month 0 \
							--end_month 11 \
							--regs ${regs[@]} \
							--names ${names[@]} \
							--index_set_name $index_set_name \
							--aggregate 0 \
							--no_ann 1 \
							--stdize 1 \
							--write_netcdf 1 >& $log_dir/compute_index_${casename}_${var}_$index_set_name.log &
       exstatus=$?
       if [ $exstatus -ne 0 ]; then
         echo
         echo "Failed computing Nino eqsoi_index"
         exit 1
       fi

done

echo
echo Waiting for jobs to complete ...
echo

wait
echo ... Done.
echo
