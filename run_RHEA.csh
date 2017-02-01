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
#       short_term_archive:     Adds /atm/hist after the casename. If the data sits in a different structure, add it after
#       the casename in test_casename 

#USER DEFINED CASE SPECIFIC VARIABLES TO SPECIFY (REQUIRED)

#Test case variables
setenv test_casename 			20161117.beta0.A_WCYCL1850S.ne30_oEC_ICG.edison
setenv test_native_res			ne30
setenv test_archive_dir 		/lustre/atlas1/cli115/proj-shared/mbranst  
setenv test_short_term_archive		0
setenv test_begin_yr_climo		15
setenv test_end_yr_climo		20
setenv test_begin_yr_ts			1
setenv test_end_yr_ts			18

#Atmosphere switches (True(1)/False(0)) to condense variables, compute climos, remap climos and condensed time series file
setenv test_condense_field_climo	1
setenv test_condense_field_ts		1
setenv test_compute_climo		1
setenv test_remap_climo			1
setenv test_remap_ts			1


#Reference case variables
#setenv ref_case				20160401.A_WCYCL2000.ne30_oEC.edison.alpha4_00H
#setenv ref_archive_dir 			/lustre/atlas1/cli115/proj-shared/mbranst
setenv ref_case				obs
setenv ref_archive_dir 			/lustre/atlas1/cli900/world-shared/obs_for_diagnostics

#ACMEv0 ref_case info for ocn/ice diags
# IMPORTANT: the ACMEv0 model data MUST have been pre-processed. If this pre-processed data is not available, set ref_case_v0 to None.
set projdir =                           $PROJWORK/cli115
setenv ref_case_v0                      B1850C5_ne30_v0.4
setenv ref_archive_v0_ocndir            $projdir/milena/ACMEv0_lowres/${ref_case_v0}/ocn/postprocessing
setenv ref_archive_v0_seaicedir         $projdir/milena/ACMEv0_lowres/${ref_case_v0}/ice/postprocessing

#The following are ignored if ref_case is obs
setenv ref_native_res             	ne30
setenv ref_short_term_archive     	0
setenv ref_begin_yr_climo         	1
setenv ref_end_yr_climo           	5
setenv ref_begin_yr_ts		  	1
setenv ref_end_yr_ts		  	5

setenv ref_condense_field_climo		1
setenv ref_condense_field_ts		1
setenv ref_compute_climo        	1
setenv ref_remap_climo          	1
setenv ref_remap_ts			1

#Set yr_offset for ocn/ice time series plots
#setenv yr_offset 1999    # for 2000 time slices
setenv yr_offset 1849   # for 1850 time slices

#Set ocn/ice specific paths to mapping files locations
# IMPORTANT: user will need to change mpas_meshfile and mpas_remapfile *if* MPAS grid varies.
#     EXAMPLES of MPAS meshfiles:
#      $projdir/milena/MPAS-grids/gridfile.oEC60to30.nc  for the EC60to30 grid
#     EXAMPLES of MPAS remap files:
#      $projdir/milena/mapping_files/map_oEC60to30_TO_0.5x0.5degree_blin.160412.nc  remap from EC60to30 to regular 0.5degx0.5deg grid
#      $projdir/milena/mapping_files/map_oRRS30to10_TO_0.5x0.5degree_blin.160412.nc remap from RRS30to10 to regular 0.5degx0.5deg grid
#      $projdir/milena/mapping_files/map_oRRS15to5_TO_0.5x0.5degree_blin.160412.nc  remap from RRS15to5 to regular 0.5degx0.5deg grid
#
#     Finally, note that pop_remapfile is not currently used
setenv mpas_meshfile              $projdir/milena/MPAS-grids/gridfile.oEC60to30.nc
setenv mpas_remapfile             $projdir/milena/mapping_files/map_oEC60to30_TO_0.5x0.5degree_blin.160412.nc
setenv pop_remapfile              $projdir/milena/mapping_files/map_gx1v6_TO_0.5x0.5degree_blin.160413.nc

#Select sets of diagnostics to generate (False = 0, True = 1)
setenv generate_atm_diags 		1
setenv generate_ocnice_diags 		1

#The following ocn/ice diagnostic switches are ignored if generate_ocnice_diags is set to 0
setenv generate_ohc_trends 		1
setenv generate_sst_trends 		1
setenv generate_sst_climo 		1
setenv generate_sss_climo               1
setenv generate_mld_climo               1
setenv generate_seaice_trends 		1
setenv generate_seaice_climo 		1

#Other diagnostics not working currently, work in progress
setenv generate_moc 			0
setenv generate_mht 			0
setenv generate_nino34 			0


#Generate standalone html file to view plots on a browser, if required
setenv generate_html 			1


###############################################################################################


#OTHER VARIABLES (NOT REQUIRED TO BE CHANGED BY THE USER - DEFAULTS SHOULD WORK, USER PREFERENCE BASED CHANGES)

#Set paths to scratch, logs and plots directories
setenv test_scratch_dir		  $PROJWORK/cli115/$USER/$test_casename.test.pp
setenv ref_scratch_dir		  $PROJWORK/cli115/$USER/$ref_case.test.pp
setenv plots_dir 		  $PROJWORK/cli115/$USER/coupled_diagnostics_${test_casename}-$ref_case
setenv log_dir 			  $PROJWORK/cli115/$USER/coupled_diagnostics_${test_casename}-$ref_case.logs

#Set atm specific paths to mapping and data files locations
setenv remap_files_dir		  $PROJWORK/cli115/mapping/maps
setenv GPCP_regrid_wgt_file 	  $remap_files_dir/$test_native_res-to-GPCP.conservative.wgts.nc
setenv CERES_EBAF_regrid_wgt_file $remap_files_dir/$test_native_res-to-CERES-EBAF.conservative.wgts.nc
setenv ERS_regrid_wgt_file        $remap_files_dir/$test_native_res-to-ERS.conservative.wgts.nc

#Set ocn/ice specific paths to data files locations
setenv mpas_climodir              $test_scratch_dir

setenv obs_ocndir                 $projdir/observations
setenv obs_seaicedir              $projdir/observations/SeaIce
setenv obs_sstdir                 $obs_ocndir/SST
setenv obs_sssdir                 $obs_ocndir/SSS
setenv obs_mlddir                 $obs_ocndir/MLD
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

#PUT THE PROVIDED CASE INFORMATION IN CSH ARRAYS TO FACILITATE READING BY OTHER SCRIPTS
csh_scripts/setup.csh

#RUN DIAGNOSTICS
if ($generate_atm_diags == 1) then
        ./ACME_atm_diags.csh
        set atm_status = $status
else
        set atm_status = 0
endif

if ($generate_ocnice_diags == 1) then
        ./ACME_ocnice_diags.csh
        set ocnice_status = $status
else
        set ocnice_status = 0
endif

#GENERATE HTML PAGE IF ASKED
echo
echo "Status of atmospheric diagnostics, 0 implies success or not invoked:" $atm_status
echo "Status of ocean/ice diagnostics, 0 implies success or not invoked:" $ocnice_status

if ($atm_status == 0 || $ocnice_status == 0) then
        source $log_dir/case_info.temp

        set n_cases = $#case_set

        @ n_test_cases = $n_cases - 1

        foreach j (`seq 1 $n_test_cases`)

                if ($generate_html == 1) then
                        csh csh_scripts/generate_html_index_file.csh    $j \
                                                                        $plots_dir \
                                                                        $www_dir
                endif
        end
else
        echo
        echo Neither atmospheric nor ocn/ice diagnostics were successful. HTML page not generated!
        echo
        echo
endif




