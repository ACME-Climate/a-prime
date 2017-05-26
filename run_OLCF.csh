#!/bin/csh

#
# Template driver script to generate coupled diagnostics on titan/rhea
#   Note: this package is much slower on rhea!
#
# Basic usage:
#       1. copy this template to something like run_OLCF_$user.csh
#       2. open run_OLCF_$user.csh and set user defined, case-specific variables
#       3. execute: csh run_OLCF_$user.csh

# Meaning of acronym/words used in variable names below:
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

set projdir =                           $PROJWORK/cli115

# USER DEFINED CASE SPECIFIC VARIABLES TO SPECIFY (REQUIRED)

# Main directory where all analysis output is stored
# (e.g., plots will go in a specific subdirectory of $output_base_dir,
# as will log files, generated climatologies, etc)

setenv output_base_dir                  $projdir/$USER


# Test case variables
setenv test_casename 			20161117.beta0.A_WCYCL1850S.ne30_oEC_ICG.edison
setenv test_native_res			ne30

# one of the supported MPAS mesh names (e.g. oEC60to30v1, oEC60to30v3, oRRS18to6v1)
# NB: this may change with a different choice of test_casename!

setenv test_mpas_mesh_name              oEC60to30v1

setenv test_archive_dir 		/lustre/atlas1/cli115/proj-shared/mbranst
setenv test_short_term_archive		0
setenv test_begin_yr_climo		16
setenv test_end_yr_climo		20
setenv test_begin_yr_ts			1
setenv test_end_yr_ts			18
setenv test_begin_yr_climateIndex_ts	1
setenv test_end_yr_climateIndex_ts	9


# Atmosphere switches (True(1)/False(0)) to condense variables, compute climos, remap climos and condensed time series file
# If no pre-processing is done (climatology, remapping), all the switches below should be 1
# If a switch is 0, then the user should ensure that the needed files are in the scratch directory (defined below)
# If a switch is 0 for climo, then the user should ensure that the files in the scratch directory correspond to the intended begin and end years set above.

setenv test_condense_field_climo	1
setenv test_condense_field_ts		1
setenv test_compute_climo		1
setenv test_remap_climo			1
setenv test_remap_ts			1



# Reference case variables

#setenv ref_case				20160401.A_WCYCL2000.ne30_oEC.edison.alpha4_00H
#setenv ref_archive_dir 			/lustre/atlas1/cli115/proj-shared/mbranst

setenv ref_case				obs
setenv ref_archive_dir 			/lustre/atlas1/cli900/world-shared/obs_for_diagnostics


# ACMEv0 ref_case info for ocn/ice diags
#  IMPORTANT: the ACMEv0 model data MUST have been pre-processed.
#  If this pre-processed data is not available, set ref_case_v0 to None.

setenv ref_case_v0                      B1850C5_ne30_v0.4
setenv ref_archive_v0_ocndir            $projdir/milena/ACMEv0_lowres/${ref_case_v0}/ocn/postprocessing
setenv ref_archive_v0_seaicedir         $projdir/milena/ACMEv0_lowres/${ref_case_v0}/ice/postprocessing


# The following are ignored if ref_case is obs
setenv ref_native_res             	ne30
setenv ref_short_term_archive     	0
setenv ref_begin_yr_climo         	1
setenv ref_end_yr_climo           	5
setenv ref_begin_yr_ts		  	1
setenv ref_end_yr_ts		  	5
setenv ref_begin_yr_climateIndex_ts	1
setenv ref_end_yr_climateIndex_ts	9999

setenv ref_condense_field_climo		1
setenv ref_condense_field_ts		1
setenv ref_compute_climo        	1
setenv ref_remap_climo          	1
setenv ref_remap_ts			1

# Select sets of diagnostics to generate (False = 0, True = 1)
setenv generate_atm_diags 		1
setenv generate_ocnice_diags 		1

# The following ocn/ice diagnostic switches are ignored if generate_ocnice_diags is set to 0
setenv generate_ohc_trends 		1
setenv generate_sst_trends 		1
setenv generate_sst_climo 		1
setenv generate_sss_climo               1
setenv generate_mld_climo               1
setenv generate_moc 			1
setenv generate_mht 			1
setenv generate_seaice_trends 		1
setenv generate_seaice_climo 		1
setenv generate_nino34 			1

# Generate standalone html file to view plots on a browser, if required
setenv generate_html 			1


###############################################################################################

# OTHER VARIABLES (NOT REQUIRED TO BE CHANGED BY THE USER - DEFAULTS SHOULD WORK, USER PREFERENCE BASED CHANGES)

# Set paths to scratch, logs and plots directories
setenv test_scratch_dir           $output_base_dir/$test_casename.test.pp
setenv ref_scratch_dir            $output_base_dir/$ref_case.test.pp


if ($ref_case == obs) then
	setenv plots_dir_name	  coupled_diagnostics_${test_casename}_yr_${test_begin_yr_climo}-${test_end_yr_climo}_vs_$ref_case
else
	setenv plots_dir_name     coupled_diagnostics_${test_casename}_${test_begin_yr_climo}_${test_end_yr_climo}-${ref_case}_yr_${ref_begin_yr_climo}-${ref_end_yr_climo}
endif


#User can set a custom name for the $plot_dir_name here, if the default (above) is not ideal 
#setenv plots_dir_name		  XXYYY

setenv log_dir_name		  $plots_dir_name.logs

setenv plots_dir                  $output_base_dir/$plots_dir_name
setenv log_dir                    $output_base_dir/$log_dir_name


# Set atm specific paths to mapping and data files locations
setenv remap_files_dir		  $projdir/mapping/maps
setenv GPCP_regrid_wgt_file 	  $remap_files_dir/$test_native_res-to-GPCP.conservative.wgts.nc
setenv CERES_EBAF_regrid_wgt_file $remap_files_dir/$test_native_res-to-CERES-EBAF.conservative.wgts.nc
setenv ERS_regrid_wgt_file        $remap_files_dir/$test_native_res-to-ERS.conservative.wgts.nc

# Set ocn/ice specific paths to mapping and region masking file locations
#     remap from MPAS mesh to regular 0.5degx0.5deg grid
#     NB: if this file does not exist, it will be generated by the analysis

setenv mpas_remapfile             $projdir/mpas_analysis/mapping/map_${test_mpas_mesh_name}_to_0.5x0.5degree_bilinear.nc


#     MPAS-O region mask files containing masking information for the Atlantic basin
#     NB: this file, instead, *needs* to be present 

setenv mpaso_regions_file         $projdir/mpas_analysis/region_masks/${test_mpas_mesh_name}_Atlantic_region_and_southern_transect.nc

# Set ocn/ice specific paths to data file names and locations
setenv obs_ocndir                 $projdir/observations
setenv obs_seaicedir              $projdir/observations/SeaIce
setenv obs_sstdir                 $obs_ocndir/SST
setenv obs_sssdir                 $obs_ocndir/SSS
setenv obs_mlddir                 $obs_ocndir/MLD
setenv obs_ninodir                $obs_ocndir/Nino
setenv obs_mhtdir                 $obs_ocndir/MHT
setenv obs_iceareaNH              $obs_seaicedir/IceArea_timeseries/iceAreaNH_climo.nc
setenv obs_iceareaSH              $obs_seaicedir/IceArea_timeseries/iceAreaSH_climo.nc
setenv obs_icevolNH               $obs_seaicedir/PIOMAS/PIOMASvolume_monthly_climo.nc
setenv obs_icevolSH               none

# Location of website directory to host the webpage
setenv www_dir $HOME/www

##############################################################################
########### USER SHOULD NOT NEED TO CHANGE ANYTHING HERE ONWARDS #############

setenv coupled_diags_home $PWD

# LOAD THE ANACONDA-2.7-CLIMATE ENV THAT LOADS ALL REQUIRED PYTHON MODULES
module use /ccs/proj/cli115/pwolfram/modulefiles/all
module load python/anaconda-2.7-climate

# PUT THE PROVIDED CASE INFORMATION IN CSH ARRAYS TO FACILITATE READING BY OTHER SCRIPTS
csh_scripts/setup.csh

# RUN DIAGNOSTICS
if ($generate_atm_diags == 1) then
        # Check whether requested files for computing climatologies are available
        set rpointer_file = ${test_archive_dir}/${test_casename}/run/rpointer.atm
        set year_max = `grep -m 1 -Eo '\<[0-9]{4}\>' ${rpointer_file} | awk '{print $1-1}'`
        if (${test_end_yr_climo} <= ${year_max}) then
          ./ACME_atm_diags.csh
          set atm_status = $status
        else
          echo "Requested test_end_yr_climo is larger than the maximum simulation year. Exiting atm diagnostics..."
          set atm_status = 0
        endif
else
        set atm_status = 0
endif

if ($generate_ocnice_diags == 1) then
        # Check whether requested files for computing climatologies are available
        set rpointer_file = ${test_archive_dir}/${test_casename}/run/rpointer.ocn
        set year_max = `grep -m 1 -Eo '\<[0-9]{4}\>' ${rpointer_file} | awk '{print $1-1}'`
        if (${test_end_yr_climo} <= ${year_max}) then
          ./ACME_ocnice_diags.csh
          set ocnice_status = $status
        else
          echo "Requested test_end_yr_climo is larger than the maximum simulation year. Exiting ocn/ice diagnostics..."
          set ocnice_status = 0
        endif
else
        set ocnice_status = 0
endif


#COPY THIS RUN SCRIPT TO THE $plots_dir FOR PROVENANCE
cp $0 $plots_dir/$0


# GENERATE HTML PAGE IF ASKED
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
