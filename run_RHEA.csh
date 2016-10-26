#!/bin/csh

#
# Template driver script to generate coupled diagnostics on rhea
#
#Basic usage:
#       1. copy this template to something like run_RHEA_$user.csh
#       2. open run_RHEA_$user.csh and set user defined, case-specific variables
#       3. execute: csh run_RHEA_$user.csh

#Meaning of acronym/words used in variable names below:
#	test:		Test case
#	ref:		Reference case
#	ts: 		Time series; e.g. test_begin_yr_ts, here ts refers to time series
#	climo: 		Climatology
#	begin_yr: 	Model year to start analysis 
#	end_yr:		Model year to end analysis
#	condense:	Create a new file with time series data for only one variable.
#			This is used to create climatology and in generating time series plots
#	archive_dir:	Location of model generated output directory
#	scratch_dir:	Location of directory where the user wants to store files generated by the diagnostics.
#			This includes climos, remapped climos, condensed files and data files used for plotting. 

echo 'Running template version of run_RHEA!'
echo 'Please copy template to run_RHEA_$user.csh and modify/run that instead'
echo 'Exiting...'
exit

#USER DEFINED CASE SPECIFIC VARIABLES TO SPECIFY (REQUIRED)

#Test case variables
setenv test_casename 			20160428.A_WCYCL1850.ne30_oEC.edison.alpha5_00 
setenv test_native_res			ne30
setenv test_archive_dir 		/lustre/atlas1/cli115/proj-shared/mbranst  
setenv test_short_term_archive		1
setenv test_begin_yr_climo		15
setenv test_end_yr_climo		20
setenv test_begin_yr_ts			1
setenv test_end_yr_ts			18

#Switches (True(1)/False(0)) to condense variables, compute climos, remap climos and condensed time series file
setenv test_condense_field_climo	1
setenv test_condense_field_ts		1
setenv test_compute_climo		1
setenv test_remap_climo			1
setenv test_remap_ts			1


#Reference case variables
setenv ref_case				20160401.A_WCYCL2000.ne30_oEC.edison.alpha4_00H
setenv ref_archive_dir 			/lustre/atlas1/cli115/proj-shared/mbranst
#setenv ref_case			obs
#setenv ref_archive_dir 		$WORLDWORK/csc121/obs_data

#The following are ignored if ref_case is obs
setenv ref_native_res             	ne30
setenv ref_short_term_archive     	1
setenv ref_begin_yr_climo         	1
setenv ref_end_yr_climo           	5
setenv ref_begin_yr_ts		  	1
setenv ref_end_yr_ts		  	5

setenv ref_condense_field_climo		1
setenv ref_condense_field_ts		1
setenv ref_compute_climo        	1
setenv ref_remap_climo          	1
setenv ref_remap_ts			1

#ref_case info for oceans
set projdir = 				$PROJWORK/cli115/$USER
setenv casename_model_tocompare   	B1850C5_ne30_v0.4
setenv ocndir_model_tocompare     	$projdir/ACMEv0_lowres/${casename_model_tocompare}/ocn/postprocessing
setenv seaicedir_model_tocompare  	$projdir/ACMEv0_lowres/${casename_model_tocompare}/ice/postprocessing

#Select sets of diagnostics to generate (False = 0, True = 1)
setenv generate_atm_diags 		1
setenv generate_ocnice_diags 		0
setenv generate_ohc_trends 		1
setenv generate_sst_trends 		1
setenv generate_seaice_trends 		1
setenv generate_seaice_climo 		1

#Other diagnostics not working currently, work in progress
setenv generate_sst_climo 		0
setenv generate_moc 			0
setenv generate_mht 			0
setenv generate_nino34 			0


#Generate standalone html file to view plots on a browser, if required
setenv generate_html 			1


###############################################################################################


#OTHER VARIABLES (NOT REQUIRED TO BE CHANGED BY THE USER - DEFAULTS SHOULD WORK, USER PREFERENCE BASED CHANGES)

#Set paths to scratch, logs and plots directories
setenv test_scratch_dir		  $PROJWORK/cli106/$USER/$test_casename.test.pp
setenv ref_scratch_dir		  $PROJWORK/cli106/$USER/$ref_case.test.pp
setenv plots_dir 		  $PROJWORK/cli106/$USER/coupled_diagnostics_${test_casename}-$ref_case
setenv log_dir 			  $PROJWORK/cli106/$USER/coupled_diagnostics_${test_casename}-$ref_case.logs

#Set atm specific paths to mapping and data files locations
#setenv remap_files_dir		  $WORLDWORK/csc121/4ue/grids
setenv remap_files_dir		  $PROJWORK/cli106/salil/archive/grids
setenv GPCP_regrid_wgt_file 	  $WORLDWORK/csc121/4ue/grids/$test_native_res-to-GPCP.conservative.wgts.nc
setenv CERES_EBAF_regrid_wgt_file $WORLDWORK/csc121/4ue/grids/$test_native_res-to-CERES-EBAF.conservative.wgts.nc
setenv ERS_regrid_wgt_file        $PROJWORK/cli106/salil/archive/grids/$test_native_res-to-ERS.conservative.wgts.nc

#Set ocn/ice specific paths to mapping and data files locations
setenv mpas_meshfile              $projdir/milena/MPAS-grids/ocn/gridfile.oEC60to30.nc
setenv mpas_remapfile             $projdir/mapping/maps/map_oEC60to30_TO_0.5x0.5degree_blin.160412.nc
setenv model_tocompare_remapfile  $projdir/mapping/maps/map_gx1v6_TO_0.5x0.5degree_blin.160413.nc
setenv mpas_climodir              $test_scratch_dir

setenv obs_ocndir                 $projdir/observations/Ocean

setenv obs_seaicedir              $projdir/observations/SeaIce
setenv obs_iceareaNH              $obs_seaicedir/IceArea_timeseries/iceAreaNH_climo.nc
setenv obs_iceareaSH              $obs_seaicedir/IceArea_timeseries/iceAreaSH_climo.nc
setenv obs_icevolNH               $obs_seaicedir/PIOMAS/PIOMASvolume_monthly_climo.nc
setenv obs_icevolSH               none



#Location of website directory to host the webpage
setenv www_dir $HOME/www




##############################################################################
###USER SHOULD NOT NEED TO CHANGE ANYTHING HERE ONWARDS######################

setenv coupled_diags_home $PWD

#LOAD THE ANACONDA-2.7-CLIMATE ENV THAT LOADS ALL REQUIRED PYTHON MODULES

module use /ccs/proj/cli115/pwolfram/modulefiles/all
module load python/anaconda-2.7-climate

module load nco
setenv PATH $PATH\:/autofs/nccs-svm1_home1/zender/bin_rhea


#PUT THE PRESCRIBED INFORMATION IN CSH ARRAYS TO FACILITATE READING BY OTHER SCRIPTS
csh_scripts/setup.csh


#RUN DIAGNOSTICS
if ($generate_atm_diags == 1) then
	./ACME_atm_diags.csh
endif

if ($generate_ocnice_diags == 1) then
	./ACME_ocn_diags.csh
endif


#GENERATE HTML PAGE IF ASKED
source $log_dir/case_info.temp 

set n_cases = $#case_set

@ n_test_cases = $n_cases - 1

foreach j (`seq 1 $n_test_cases`)

	if ($generate_html == 1) then
		csh csh_scripts/generate_html_index_file.csh 	$j \
								$plots_dir \
								$www_dir
	endif
end

