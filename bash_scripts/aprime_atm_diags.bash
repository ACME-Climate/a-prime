#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#

# Checking if required mapping files exist, exiting otherwise
if [ ! -d $remap_files_dir ]; then
  echo "remap_files_dir $remap_files_dir does not exist! Please check." 
  echo "Exiting atmosphere diagnostics ..."
  echo 
  exit 1
fi

if [ ! -f $GPCP_regrid_wgt_file ]; then
  echo "GPCP_regrid_wgt_file $GPCP_regrid_wgt_file does not exist! Please check."
  echo "Exiting atmosphere diagnostics ..."
  echo
  echo
  exit 1
fi

if [ ! -f $CERES_EBAF_regrid_wgt_file ]; then
  echo "CERES_EBAF_regid_wgt_file $CERES_EBAF_regrid_wgt_file does not exist! Please check."
  echo "Exiting atmosphere diagnostics ..."
  echo 
  exit 1
fi

if [ ! -f $ERS_regrid_wgt_file ]; then
  echo "ERS_regrid_wgt_file $ERS_regrid_wgt_file does not exist! Please check."
  echo "Exiting atmosphere diagnostics ..."
  echo 
  exit 1
fi

# GENERATE ATMOSPHERIC DIAGNOSTICS

# Reading case info
source $log_dir/case_info.temp
n_cases=${#case_set[@]}

ref_case="${case_set[$n_cases-1]}"
ref_scratch_dir="${scratch_dir_set[$n_cases-1]}"

# Reading seasonal info 
source $log_dir/season_info.temp
n_seasons=${#begin_month_set[@]}

echo
echo "Generating atmospheric climatology diagnostics..."
echo


#CLIMATOLOGY

# Ensuring a unique set of fields to compute climatology to reduce redundancy in climatology computations
if [ "$ref_case" == "obs" ]; then
  var_list_file="${coupled_diags_home}/bash_scripts/var_list_climo_model_vs_obs.bash"
else
  var_list_file="${coupled_diags_home}/bash_scripts/var_list_climo_model_vs_model.bash"
fi

compute_climo_var_list_file="$log_dir/var_list_compute_climo.bash"

${coupled_diags_home}/bash_scripts/generate_unique_field_list.bash $var_list_file \
	   			               $compute_climo_var_list_file

# Condense climatology fields into individual files
j=0
while [ $j -lt $n_cases ]; do
   casename="${case_set[$j]}"
   archive_dir="${archive_dir_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   short_term_archive=${short_term_archive_set[$j]}
   begin_yr_climo=${begin_yr_climo_set[$j]}
   end_yr_climo=${end_yr_climo_set[$j]}

   condense_field_climo=${condense_field_climo_set[$j]}
   compute_climo=${compute_climo_set[$j]}

   archive_dir_atm="$archive_dir/$casename/run"

   if [ $short_term_archive -eq 1 ]; then
     echo "Using ACME short term archiving directory structure!"
     archive_dir_atm="$archive_dir/$casename/archive/atm/hist"
   fi

   if [ "$casename" == "obs" ]; then
     archive_dir_atm="$archive_dir"
   fi

   if [ ! -d $archive_dir_atm ]; then
     echo "$archive_dir_atm for $casename does not exist! Please check."
     echo "Exiting atmosphere diagnostics..."
     echo 
     exit 1
   fi

   if [ "$casename" != "obs" ]; then
     file_list=()
     for yr in `seq -f "%04g" $begin_yr_climo $end_yr_climo`; do
        for yr_file in "${archive_dir_atm}/*cam.h0.$yr*.nc"; do
           file_list=("${file_list[@]}" $yr_file)
        done
     done
     file_list2=`ls ${file_list[@]} 2>/dev/null`
     if [ -z "$file_list2" ]; then
       echo "****"
       echo "Atmosphere file list needed for climatologies is empty."
       echo "Check that begin_yr_climo is consistent with available data."
       echo "Exiting atmosphere diagnostics..."
       echo "****"
       exit 3
     fi
   fi

   if [ $condense_field_climo -eq 1 ] && [ $compute_climo -eq 1 ]; then
     ${coupled_diags_home}/bash_scripts/condense_field_bundle.bash $archive_dir_atm \
					       $scratch_dir \
					       $casename \
					       $begin_yr_climo \
					       $end_yr_climo \
					       $compute_climo_var_list_file
   else
     echo "condense_field set to 0 or casename is obs and compute_climo set to 0." 
     echo "Not condensing for climo variables for $casename!"
   fi

   j=$((j+1))
done

echo

# Compute climatology
j=0
while [ $j -lt $n_cases ]; do
   casename="${case_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   compute_climo=${compute_climo_set[$j]}
   begin_yr_climo=${begin_yr_climo_set[$j]}
   end_yr_climo=${end_yr_climo_set[$j]}

   if [ $compute_climo -eq 1 ]; then
     echo
     echo "Computing seasonal climatology for $casename"
     echo "Log files in $log_dir/climo_$casename..."
     echo
     ${coupled_diags_home}/bash_scripts/compute_climo.bash $scratch_dir \
				       $casename \
				       $compute_climo_var_list_file \
				       $begin_yr_climo \
				       $end_yr_climo
   else
     echo "compute_climo set to $compute_climo or casename is obs. Not computing climatology for $casename!"
   fi

   j=$((j+1))
done

echo

# Remap climatology
j=0
while [ $j -lt $n_cases ]; do
   casename="${case_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   native_res="${native_res_set[$j]}"
   remap_climo=${remap_climo_set[$j]}
   begin_yr_climo=${begin_yr_climo_set[$j]}
   end_yr_climo=${end_yr_climo_set[$j]}

   if [ $remap_climo -eq 1 ]; then
     echo
     echo "Remapping seasonal climatology files for $casename" 
     echo "Log files in $log_dir/remap_climo_$casename..."
     echo
     ${coupled_diags_home}/bash_scripts/remap_climo_nco.bash $scratch_dir \
				         $casename \
				         $begin_yr_climo \
		  		         $end_yr_climo \
				         $native_res \
				         $compute_climo_var_list_file
   else
     echo "remap_climo set to $remap_climo or casename is obs. Not remapping climatology for $casename!"
   fi

   j=$((j+1))
done

echo

# Plot climatologies and differences
echo
echo "Plotting seasonal climatology and differences"
echo "Log files in $log_dir/plot_climo..."
echo

ref_case="${case_set[$n_cases-1]}"
ref_scratch_dir="${scratch_dir_set[$n_cases-1]}"

if [ $ref_case == obs ]; then 
	ref_scratch_dir=${archive_dir_set[$n_cases-1]}
fi

ref_begin_yr_climo=${begin_yr_climo_set[$j-1]}
ref_end_yr_climo=${end_yr_climo_set[$j-1]}

echo "Reference Case: $ref_case"
echo

n_test_cases=$((n_cases-1))
j=0
while [ $j -lt $n_test_cases ]; do
   casename="${case_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   begin_yr_climo=${begin_yr_climo_set[$j]}
   end_yr_climo=${end_yr_climo_set[$j]}


   ${coupled_diags_home}/bash_scripts/plot_climo.bash $scratch_dir \
		 	          $casename \
			          $begin_yr_climo \
			          $end_yr_climo \
			          $ref_scratch_dir \
			          $ref_case \
			          $ref_begin_yr_climo \
			          $ref_end_yr_climo

   j=$((j+1))
done


# TIME TRENDS        

# Ensuring a unique set of fields to condense for time series
if [ "$ref_case" == "obs" ]; then
  var_list_file="${coupled_diags_home}/bash_scripts/var_list_time_series_model_vs_obs.bash"
else
  var_list_file="${coupled_diags_home}/bash_scripts/var_list_time_series_model_vs_model.bash"
fi

ts_var_list_file="$log_dir/ts_var_list.bash"

${coupled_diags_home}/bash_scripts/generate_unique_field_list.bash $var_list_file \
				               $ts_var_list_file

# Condense time series variables into individual files
j=0
while [ $j -lt $n_cases ]; do
   casename="${case_set[$j]}"
   archive_dir="${archive_dir_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   short_term_archive=${short_term_archive_set[$j]}
   begin_yr_ts=${begin_yr_ts_set[$j]}
   end_yr_ts=${end_yr_ts_set[$j]}
   condense_field_ts=${condense_field_ts_set[$j]}
   archive_dir_atm="$archive_dir/$casename/run"

   if [ $short_term_archive -eq 1 ]; then
     echo "Using ACME short term archiving directory structure!"
     archive_dir_atm="$archive_dir/$casename/archive/atm/hist"
   fi

   if [ "$casename" != "obs" ]; then
     file_list=()
     for yr in `seq -f "%04g" $begin_yr_ts $end_yr_ts`; do
        for yr_file in "${archive_dir_atm}/*cam.h0.$yr*.nc"; do
           file_list=("${file_list[@]}" $yr_file)
        done
     done
     file_list2=`ls ${file_list[@]} 2>/dev/null` 
     if [ -z "$file_list2" ]; then
       echo "****"
       echo "Atmosphere file list needed for time series is empty."
       echo "Check that begin_yr_ts is consistent with available data."
       echo "Exiting atmosphere diagnostics..."
       echo "****"
       exit 3
     fi
   fi

   if [ $condense_field_ts -eq 1 ]; then
     ${coupled_diags_home}/bash_scripts/condense_field_bundle.bash $archive_dir_atm \
					       $scratch_dir \
					       $casename \
					       $begin_yr_ts \
					       $end_yr_ts \
					       $ts_var_list_file
   else
     echo "condense_field_ts set to 0 or casename is obs."
     echo "Not condensing for time series variables for $casename!"
   fi

   j=$((j+1))
done

# Interpolate time series of fields to obs grids
j=0
while [ $j -lt $n_cases ]; do
   casename="${case_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   begin_yr_ts=${begin_yr_ts_set[$j]}
   end_yr_ts=${end_yr_ts_set[$j]}
   native_res="${native_res_set[$j]}"
   remap_ts=${remap_ts_set[$j]}

   if [ $remap_ts -eq 1 ]; then
     echo
     echo "Interpolating time series files for $casename"
     echo "Log files in $log_dir/remap_time_series_${casename}..."
     echo
     ${coupled_diags_home}/bash_scripts/remap_time_series_nco.bash $scratch_dir \
					       $casename \
					       $begin_yr_ts \
					       $end_yr_ts \
					       $native_res \
					       $ts_var_list_file 
   fi

   j=$((j+1))
done


# Plot trends for different regions
echo
echo "Plotting time series"
echo "Log files in $log_dir/"
echo

ref_case="${case_set[$n_cases-1]}"
ref_scratch_dir="${scratch_dir_set[$n_cases-1]}"

if [ $ref_case == obs ]; then 
	ref_scratch_dir=${archive_dir_set[$n_cases-1]}
fi

echo "Reference Case: $ref_case"
echo

n_test_cases=$((n_cases-1))
j=0
while [ $j -lt $n_test_cases ]; do
   casename="${case_set[$j]}"
   scratch_dir="${scratch_dir_set[$j]}"
   begin_yr_ts=${begin_yr_ts_set[$j]}
   end_yr_ts=${end_yr_ts_set[$j]}

   ${coupled_diags_home}/bash_scripts/plot_time_series.bash $scratch_dir \
				        $casename \
				        $begin_yr_ts \
				        $end_yr_ts \
				        $ref_scratch_dir \
				        $ref_case

   j=$((j+1))
done


# ENSO DIAGS

if [ $generate_atm_enso_diags == 1 ]; then

        # ENSO DIAGS: Climatology related diags (meridional avg. over the Tropical Pacific)       
        echo
        echo Computing ENSO diagnostics ...
        echo

        #Ensuring a unique set of fields to condense for enso diags related to climatology
        echo
        echo Computing climatology based ENSO diagnostics - meridional avg. over the Tropical Pacific - ...
        echo

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_climo.bash

        ts_var_list_file=$log_dir/ts_var_list.bash

        ${coupled_diags_home}/bash_scripts/generate_unique_field_list.bash $var_list_file \
                                                   $ts_var_list_file

        #Condense enso diags climo variables into individual files
	j=0
	while [ $j -lt $n_cases ]; do
		casename=${case_set[$j]}
		archive_dir=${archive_dir_set[$j]}
		scratch_dir=${scratch_dir_set[$j]}
		short_term_archive=${short_term_archive_set[$j]}
		begin_yr_climo=${begin_yr_climateIndex_set[$j]}
		end_yr_climo=${end_yr_climateIndex_set[$j]}

		condense_field_climo=${condense_field_enso_atm_set[$j]}
		
                archive_dir_atm=$archive_dir/$casename/run

                if [ $short_term_archive -eq 1 ]; then
                        echo Using ACME short term archiving directory structure!
                        archive_dir_atm=$archive_dir/$casename/archive/atm/hist
                fi

                if [ $condense_field_climo -eq 1 ]; then
                        ${coupled_diags_home}/bash_scripts/condense_field_bundle.bash $archive_dir_atm \
                                                                $scratch_dir \
                                                                $casename \
                                                                $begin_yr_climo \
                                                                $end_yr_climo \
                                                                $ts_var_list_file
                else
                        echo condense_field_ts set to 0 or casename is obs.
                        echo Not condensing for ENSO diags climo variables for $casename!

                fi

    		j=$((j+1))

        done

	# Compute climatology
	j=0
	while [ $j -lt $n_cases ]; do
	   casename="${case_set[$j]}"
	   scratch_dir="${scratch_dir_set[$j]}"
	   compute_climo=${compute_climo_enso_atm_set[$j]}
	   begin_yr_climo=${begin_yr_climateIndex_set[$j]}
	   end_yr_climo=${end_yr_climateIndex_set[$j]}

	   if [ $compute_climo -eq 1 ]; then
	     echo
	     echo "Computing seasonal climatology for $casename"
	     echo "Log files in $log_dir/climo_$casename..."
	     echo
	     ${coupled_diags_home}/bash_scripts/compute_climo.bash $scratch_dir \
					       $casename \
					       $ts_var_list_file \
					       $begin_yr_climo \
					       $end_yr_climo
	   else
	     echo "compute_climo set to $compute_climo or casename is obs. Not computing climatology for $casename!"
	   fi

	   j=$((j+1))

	done


	# Remap climatology
	j=0
	while [ $j -lt $n_cases ]; do
	   casename="${case_set[$j]}"
	   scratch_dir="${scratch_dir_set[$j]}"
	   native_res="${native_res_set[$j]}"
	   remap_climo=${remap_climo_enso_atm_set[$j]}
	   begin_yr_climo=${begin_yr_climateIndex_set[$j]}
	   end_yr_climo=${end_yr_climateIndex_set[$j]}

	   if [ $remap_climo -eq 1 ]; then
	     echo
	     echo "Remapping seasonal climatology files for $casename" 
	     echo "Log files in $log_dir/remap_climo_$casename..."
	     echo
	     ${coupled_diags_home}/bash_scripts/remap_climo_nco.bash $scratch_dir \
						 $casename \
						 $begin_yr_climo \
						 $end_yr_climo \
						 $native_res \
						 $ts_var_list_file
	   else
	     echo "remap_climo set to $remap_climo or casename is obs. Not remapping climatology for $casename!"
	   fi

	   j=$((j+1))
	done

	echo

        # ENSO Diags: Plot Meridional Average over the Tropical Pacific
        echo
        echo
        echo Plotting meridional average over the Tropical Pacific
        echo Log files in $log_dir/
        echo

	ref_case="${case_set[$n_cases-1]}"
	ref_scratch_dir="${scratch_dir_set[$n_cases-1]}"

        if [ $ref_case == obs ]; then 
                ref_scratch_dir=${archive_dir_set[$n_cases-1]}
        fi

	n_test_cases=$((n_cases-1))

	j=0
	while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_climo=${begin_yr_climateIndex_set[$j]}
                end_yr_climo=${end_yr_climateIndex_set[$j]}

                ${coupled_diags_home}/bash_scripts/plot_tropical_pacific_meridional_avg.bash \
						 $scratch_dir \
                                                 $casename \
                                                 $begin_yr_climo \
                                                 $end_yr_climo \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $var_list_file

		j=$((j+1))
        done



        #ENSO Diags: Time Series related diags (Nino index, regression, std. dev. and lead-lag regression)
        echo
        echo Computing time series based ENSO diagnostics ...
        echo

        #Ensuring a unique set of fields to condense for time series analysis
        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash

        ts_var_list_file= $log_dir/ts_var_list.bash

        ${coupled_diags_home}/bash_scripts/generate_unique_field_list.bash $var_list_file \
                                                   $ts_var_list_file


        #Condense time series variables into individual files
        j=0
        while [ $j -lt $n_cases ]; do
                casename=${case_set[$j]}
                archive_dir=${archive_dir_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                short_term_archive=${short_term_archive_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}

                condense_field_ts=${condense_field_enso_atm_set[$j]}

                archive_dir_atm=$archive_dir/$casename/run

                if [ $short_term_archive -eq 1 ]; then
                        echo Using ACME short term archiving directory structure!
                        archive_dir_atm=$archive_dir/$casename/archive/atm/hist
                fi

                if [ $condense_field_ts -eq 1 ]; then
                        ${coupled_diags_home}/bash_scripts/condense_field_bundle.bash $archive_dir_atm \
                                                                $scratch_dir \
                                                                $casename \
                                                                $begin_yr_ts \
                                                                $end_yr_ts \
                                                                $ts_var_list_file
                else
                        echo condense_field_ts set to 0 or casename is obs.
                        echo Not condensing for time series variables for $casename!

                fi
		
		j=$((j+1))

        done



        # ENSO Diags: Interpolate time series of fields to obs grids

        j=0
        while [ $j -lt $n_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                native_res=${native_res_set[$j]}
                remap_ts=${remap_ts_enso_atm_set[$j]}

                if [ $remap_ts -eq 1 ]; then
                        echo
                        echo Interpolating time series files for $casename
                        echo Log files in $log_dir/remap_time_series_${casename}...
                        echo
                        ${coupled_diags_home}/bash_scripts/remap_time_series_nco.bash $scratch_dir \
                                                                $casename \
                                                                $begin_yr_ts \
                                                                $end_yr_ts \
                                                                $native_res \
                                                                $ts_var_list_file
                fi

		j=$((j+1))
        done



        # ENSO Diags: Compute Nino and EQSOI indices
        echo
        echo Computing Nino and EQSOI index
        echo Log files in $log_dir/
        echo

        ref_case=${case_set[$n_cases-1]}
        ref_scratch_dir=${scratch_dir_set[$n_cases-1]}

        echo Reference Case: $ref_case
        echo

        n_test_cases=$((n_cases-1))

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash

        j=0
        while [ $j -lt $n_cases ]; do
                casename=${case_set[$j]}
                archive_dir=${archive_dir_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}

                if [ $casename != obs ]; then
                        archive_dir=$scratch_dir
                fi


                ${coupled_diags_home}/bash_scripts/compute_indices.bash $archive_dir \
                                                  $scratch_dir \
                                                  $casename \
                                                  $begin_yr_ts \
                                                  $end_yr_ts \
                                                  $var_list_file

		j=$((j+1))
        done


        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_eqsoi_index.bash 
 
        j=0
        while [ $j -lt $n_cases ]; do
                casename=${case_set[$j]}
                archive_dir=${archive_dir_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}

                if [ $casename != obs ]; then
                        archive_dir=$scratch_dir
                fi

                ${coupled_diags_home}/bash_scripts/compute_eqsoi_index.bash $archive_dir \
						      $scratch_dir \
						      $casename \
						      $begin_yr_ts \
						      $end_yr_ts \
						      $var_list_file

		j=$((j+1))
        done

        # ENSO Diags: Plot Nino and EQSOI time series 
 
        echo 
        echo Plotting Nino and EQSOI index 
        echo Log files in $log_dir/ 
        echo 
 
        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash 
 
        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]} 
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}
 
                ${coupled_diags_home}/bash_scripts/plot_multiple_index_same_plot.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $var_list_file 
		j=$((j+1))
        done



        # ENSO Diags: Plot Nino3, Nino3.4 and Nino4 index time series
        echo
        echo Plotting Nino3, Nino3.4 and Nino4 time series
        echo Log files in $log_dir/
        echo

        ref_case=${case_set[$n_cases-1]}
        ref_scratch_dir=${scratch_dir_set[$n_cases-1]}

        echo Reference Case: $ref_case
        echo

        if [ $ref_case == obs ]; then
                ref_scratch_dir=${archive_dir_set[$n_cases-1]}
        fi

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_nino_index.bash

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_enso_diags_time_series.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $var_list_file

                j=$((j+1))
        done


        # ENSO Diags: Plot Nino3, Nino3.4 and Nino4 index seasonality
        echo
        echo Plotting seasonality of Nino indices
        echo Log files in $log_dir/
        echo

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_enso_seasonality.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $var_list_file
        
                j=$((j+1))
        done

	
        #ENSO Diags: Plot Bjerknes Feedback (Nino4 TAUX vs. Nino3 SST) 

	index_field='TS'
	index_reg='Nino3'
	index_reg_name='Nino3'

	field_reg='Nino4'
	field_reg_name='Nino4'

	split_yfit_x_0=0

        echo
        echo Plotting Bjerkenes feedback
        echo Log files in $log_dir/
        echo

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_bjerknes_feedback.bash

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_enso_feedbacks.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $index_field \
                                                 $index_reg \
                                                 $index_reg_name \
                                                 $field_reg \
                                                 $field_reg_name \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $split_yfit_x_0 \
                                                 $var_list_file

                j=$((j+1))
        done


        #ENSO Diags: Plot Heat Flux - SST Feedbacks

	index_field='TS'
	index_reg='Nino3'
	index_reg_name='Nino3'

	field_reg='Nino3'
	field_reg_name='Nino3'

	split_yfit_x_0=1

        echo
        echo Plotting Nino3 heat flux-SST feedbacks
        echo Log files in $log_dir/
        echo

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_heat_flux-sst_feedbacks.bash

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_enso_feedbacks.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $index_field \
                                                 $index_reg \
                                                 $index_reg_name \
                                                 $field_reg \
                                                 $field_reg_name \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $split_yfit_x_0 \
                                                 $var_list_file

                j=$((j+1))
       
	done


	#ENSO Diags: Plot Regression

	index_field='TS'
	index_reg='Nino3'
	index_reg_name='Nino3'

	field_reg='global'
	field_reg_name='global'

        echo
        echo Plotting regression of variables against the $index_reg index
        echo Log files in $log_dir/
        echo

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_regr_nino34_fields.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $index_field \
                                                 $index_reg \
                                                 $index_reg_name \
                                                 $field_reg \
                                                 $field_reg_name \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $var_list_file

                j=$((j+1))
       
	done


        #ENSO Diags: Plot std. dev. over the Tropical Pacific
        echo
        echo Plotting std. dev. of fields over the Tropical Pacific
        echo Log files in $log_dir/

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash
        reg='Greater_Tropical_Pacific'

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_stddev.bash $scratch_dir \
                                           $casename \
                                           $reg \
                                           $begin_yr_ts \
                                           $end_yr_ts \
                                           $ref_scratch_dir \
                                           $ref_case \
                                           $ref_begin_yr_ts \
                                           $ref_end_yr_ts \
                                           $var_list_file


                j=$((j+1)) 
	done

	
	#ENSO Diags: ENSO Evolution

	index_field='TS'
	index_reg='Nino3.4'
	index_reg_name='Nino3.4'

	field_reg='global'
	field_reg_name='global'


        echo
        echo Plotting ENSO evolution: Lead lag regression of TAUX and TS against the Nino3.4 index
        echo Log files in $log_dir/
        echo

        var_list_file=${coupled_diags_home}/bash_scripts/var_list_enso_diags_time_series.bash

        j=0
        while [ $j -lt $n_test_cases ]; do
                casename=${case_set[$j]}
                scratch_dir=${scratch_dir_set[$j]}
                begin_yr_ts=${begin_yr_climateIndex_set[$j]}
                end_yr_ts=${end_yr_climateIndex_set[$j]}
                ref_begin_yr_ts=${begin_yr_climateIndex_set[$n_cases-1]}
                ref_end_yr_ts=${end_yr_climateIndex_set[$n_cases-1]}

                ${coupled_diags_home}/bash_scripts/plot_enso_evolution.bash $scratch_dir \
                                                 $casename \
                                                 $begin_yr_ts \
                                                 $end_yr_ts \
                                                 $index_field \
                                                 $index_reg \
                                                 $index_reg_name \
                                                 $field_reg \
                                                 $field_reg_name \
                                                 $ref_scratch_dir \
                                                 $ref_case \
                                                 $ref_begin_yr_ts \
                                                 $ref_end_yr_ts \
                                                 $var_list_file

                j=$((j+1))
       
	done

fi

echo
echo "Completed atmosphere diagnostics!"
echo
echo "Plots in $plots_dir"
echo
