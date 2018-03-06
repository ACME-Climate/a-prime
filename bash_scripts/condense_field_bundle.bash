#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

if [ $# -eq 0 ]; then
  echo "Input arguments not set. Will stop!"
else
  archive_dir=$1
  scratch_dir=$2
  casename=$3
  begin_yr=$4
  end_yr=$5
  var_set_file=$6
fi

source $var_set_file

echo
echo "Condensing $casename fields:"
echo "${var_set[@]}"
echo
echo "Log files in $log_dir/condense_field_${casename}...log"
echo

i=0
while [ $i -lt ${#var_set[@]} ]; do
   var="${var_set[$i]}"
   echo "$var"

   outfile=$scratch_dir/$casename.cam.h0.$var.$begin_yr-$end_yr.nc

   if [ -f $outfile ]; then
	echo "file $outfile exists! Not condensing."
   else

   ${coupled_diags_home}/bash_scripts/condense_field.bash $archive_dir \
                                      $scratch_dir \
                                      $casename \
                                      $var \
                                      $begin_yr \
                                      $end_yr >& $log_dir/condense_field_${casename}_$var.$begin_yr-$end_yr.log &
   fi

   i=$((i+1))
done

wait
