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

index_set_name=Nino

index_names=('Nino3' 'Nino3.4' 'Nino4')
field_names=('TS' 'TS' 'TS')
regs=('Nino3' 'Nino3.4' 'Nino4') 

interp_grid_temp=(0 0 0)
interp_method_temp=(0 0 0)

n_index=${#index_names[@]}

# Get grid information about the indices

for ((i=0; i<$n_index; i++)); do
	for ((k=0; k<$n_var; k++)); do
		if [ "${field_names[$i]}" == "${var_set[$k]}" ]; then
			interp_grid_temp[$i]=${interp_grid_set[$k]}
			interp_method_temp[$i]=${interp_method_set[$k]}
		fi
	done
done


# Generate plots for each field
for ((i=0; i<$n_index; i++)); do

	case=$casename
	field_name=${field_names[$i]}
	interp_grid=${interp_grid_temp[$i]}
	interp_method=${interp_method_temp[$i]}
	reg=${regs[$i]}
	index_name=${index_names[$i]}

	if [ $casename == obs ]; then
		case=${interp_grid_temp[$i]}
		interp_grid=0
                interp_method=0
	fi

	python ${coupled_diags_home}/python/compute_index.py -d True --archive_dir $archive_dir \
							--indir $scratch_dir \
							-c $case \
							-f $field_name \
							--begin_yr $begin_yr \
							--end_yr $end_yr \
							--interp_grid $interp_grid \
							--interp_method $interp_method \
							--begin_month 0 \
							--end_month 11 \
							--aggregate 0 \
							--reg ${reg[@]} \
							--index_name ${index_name[@]} \
							--no_ann 1 \
							--stdize 0 \
							--write_netcdf 1 >& $log_dir/compute_index_${case}_$index_name.log &
       exstatus=$?
       if [ $exstatus -ne 0 ]; then
         echo
         echo "Failed computing Nino indeces"
         exit 1
       fi

done

echo
echo Waiting for jobs to complete ...
echo

wait

echo ...Done.
