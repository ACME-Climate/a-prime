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
compute_climo_var_list_file=$3
begin_yr=$4
end_yr=$5

# Read in variable list for  diagnostics e.g FLUT, FSNT etc.
source $compute_climo_var_list_file
n_var=${#var_set[@]}

# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}
 
# Create Climatology of supplied fields
if [ "$casename" != "obs" ]; then

  i=0
  while [ $i -lt ${#var_set[@]} ]; do
     var="${var_set[$i]}"
     echo
     echo "$casename $var"
     echo

     ns=0
     while [ $ns -lt $n_seasons ]; do
	begin_month=${begin_month_set[$ns]}
	end_month=${end_month_set[$ns]}
	season_name="${season_name_set[$ns]}"

	outfile=$scratch_dir/${casename}_${season_name}_climo.$var.$begin_yr-$end_yr.nc

	if [ -f $outfile ]; then 
		echo "file $outfile exists! Not computing climatology."
	else

		python ${coupled_diags_home}/python/create_climatology.py --indir $scratch_dir \
						    -c $casename \
						    -f $var \
						    --begin_month $begin_month \
						    --end_month $end_month \
						    --begin_yr $begin_yr \
						    --end_yr $end_yr >& $log_dir/climo_${casename}_${var}_${season_name}_years$begin_yr-$end_yr.log &
                exstatus=$?
                if [ $exstatus -ne 0 ]; then
                  echo
                  echo "Failed computing climatologies for season $ns"
                  exit 1
                fi

	fi

        ns=$((ns+1))
     done
     i=$((i+1))
  done
fi

echo
echo "Waiting for jobs to complete ..."

wait
echo "...Done."
echo
