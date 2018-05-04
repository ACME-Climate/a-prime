#!/bin/bash
#
# Copyright (c) 2017, UT-BATTELLE, LLC
# All rights reserved.
# 
# This software is released under the BSD license detailed
# in the LICENSE file in the top level a-prime directory
#
#
# calling sequence: ./generate_html_index_file.csh casename plots_dir www_dir
#

if [ $# -eq 0 ]; then
  echo "Input arguments not set. Will stop!"
else
  case_no=$1
  plots_dir=$2
  www_dir=$3
fi

# Reading case information from file
source $log_dir/case_info.temp
n_cases=${#case_set[@]}

casename="${case_set[$case_no-1]}"
ref_case="${case_set[$n_cases-1]}"

begin_yr_climo=${begin_yr_climo_set[$case_no-1]}
end_yr_climo=${end_yr_climo_set[$case_no-1]}
begin_yr_ts=${begin_yr_ts_set[$case_no-1]}
end_yr_ts=${end_yr_ts_set[$case_no-1]}
begin_yr_climateIndex=${begin_yr_climateIndex_set[$case_no-1]}
end_yr_climateIndex=${end_yr_climateIndex_set[$case_no-1]}

ref_begin_yr_climo=${begin_yr_climo_set[$n_cases-1]}
ref_end_yr_climo=${end_yr_climo_set[$n_cases-1]}
ref_begin_yr_ts=${begin_yr_ts_set[$n_cases-1]}
ref_end_yr_ts=${end_yr_ts_set[$n_cases-1]}

# padding begin_yr and end_yr with zeroes
begin_yr=`echo $begin_yr_climo | awk '{printf "%04d",$1}'`
end_yr=`echo $end_yr_climo | awk '{printf "%04d",$1}'`

cd $plots_dir

# Setting up text for ref case
if [ "$ref_case" == "obs" ]; then
  ref_case_text="$ref_case (climo)" 
  ref_case_text_ts="$ref_case (climo)"
else
  ref_case_text="$ref_case (Years: $ref_begin_yr_climo-$ref_end_yr_climo)"
  ref_case_text_ts="$ref_case (Years: $ref_begin_yr_ts-$ref_end_yr_ts)"
fi

if [ $machname == "nersc" ]; then
  www_link="http://portal.nersc.gov/project/acme/$USER/$plots_dir_name"
  mpas_www_link="http://portal.nersc.gov/project/acme/$USER/$mpas_www_link"
elif [ $machname == "olcf" ]; then
  www_link="http://projects.olcf.ornl.gov/acme/$USER/$plots_dir_name"
  mpas_www_link="http://projects.olcf.ornl.gov/acme/$USER/$mpas_www_link"
elif  [ $machname == "aims4" ]; then
  www_link="https://aims4.llnl.gov/$USER/$plots_dir_name"
  mpas_www_link="https://aims4.llnl.gov/$USER/$mpas_www_link"
elif [ $machname == "acme1" ]; then
  www_link="https://acme-viewer.llnl.gov/$USER/$plots_dir_name"
  mpas_www_link="https://acme-viewer.llnl.gov/$USER/$mpas_www_link"
else
  www_link=""
fi

# Beginning to write index.html file
cat > index.html << EOF
<HTML>

<BODY BGCOLOR="ivory">

<HEAD>
<TITLE>ACME Coupled Diagnostic Plots</TITLE>
</HEAD>

<br>
<p><img src="acme-banner_1.jpg" style="float:right;width:500px;height:100px;">
</p>

<br>
<br>
<div style="text-align:center">
<font color=seagreen size=+3><b>ACME Coupled Priority Metrics</b></font><br>
</div>

<br>
<br>
<br>
<div style="text-align:center">
<font color=sienna size=+2><b>
${casename}<br>(Climatological years: $begin_yr_climo-$end_yr_climo) vs. $ref_case_text
</b></font>
</div>
EOF

if [ $generate_ocnice_diags -eq 1 ]; then
  if [ $www_link != "" ]; then
    cat >> index.html << EOF
    <br>
    <hr noshade size=2 size="100%">
    <br>
    <br>
    <font color=red size=+1.5><b>Click <a href=$mpas_www_link>here</a> to view full MPAS-Analysis results (only ocn/sea-ice trends are still shown below)</b></font><br>
    </div>
EOF
  else
    cat >> index.html << EOF
    <br>
    <hr noshade size=2 size="100%">
    <br>
    <br>
    <font color=red size=+1.5><b>Full MPAS-Analysis results are available in $mpas_www_dir (only ocn/sea-ice trends are still shown below)</b></font><br>
    </div>
EOF
  fi
fi

if [ $generate_atm_diags -eq 1 ]; then
  cat >> index.html << EOF
  <br>
  <br>
  <hr noshade size=2 size="100%">

  <font color=red size=+1><b>Time Series Plots: Global and Zonal-band means (ATM)</b></font><br>

  <div style="text-align:left">
  <font color=peru size=-1>$casename (Years: $begin_yr_ts-$end_yr_ts)</font><br>
  <font color=peru size=-1>$ref_case_text_ts</font>
  </div>

  <hr noshade size=2 size="100%">

  <TABLE>
EOF

  # Generating time series part of index.html file
  if [ "$ref_case" == "obs" ]; then
    source $coupled_diags_home/bash_scripts/var_list_time_series_model_vs_obs.bash
  else
    source $coupled_diags_home/bash_scripts/var_list_time_series_model_vs_model.bash
  fi

  var_grp_unique_set=()
  grp_interp_grid_set=()

  i=0
  while [ $i -lt ${#var_group_set[@]} ]; do

     add_var=1

     j=0
     while [ $j -lt ${#var_grp_unique_set[@]} ]; do
        if [[ "${var_group_set[$i]}" =~ "${var_grp_unique_set[$j]}" ]]; then
          add_var=0
        fi
        j=$((j+1))
     done

     if [ $add_var -eq 1 ]; then
       var_grp_unique_set=("${var_grp_unique_set[@]}" "${var_group_set[$i]}")
       grp_interp_grid_set=("${grp_interp_grid_set[@]}" ${interp_grid_set[$i]})
     fi

     i=$((i + 1))
  done

  i=0
  while [ $i -lt ${#var_grp_unique_set[@]} ]; do
     if [ "$ref_case" == "obs" ]; then
       grp_text="${var_grp_unique_set[$i]} (${grp_interp_grid_set[$i]})"
     else
       grp_text="${var_grp_unique_set[$i]}"
     fi

     cat >> index.html << EOF
	<TR>
	  <TH><BR>
	  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
EOF

     j=0
     while [ $j -lt ${#var_set[@]} ]; do
        var="${var_set[$j]}"
        if [ "${var_group_set[$j]}" == "${var_grp_unique_set[$i]}" ]; then
          if [ "$ref_case" == "obs" ]; then
            ref_casename_plot="${interp_grid_set[$j]}"
          else
            ref_casename_plot="$ref_case"
          fi

          cat >> index.html << EOF
		<TR>
		  <TH ALIGN=LEFT><A HREF="${casename}_${var}_ANN_reg_ts.png">$var</a> 
		  <TD ALIGN=LEFT>${var_name_set[$j]}
EOF
        fi
        j=$((j + 1))
     done

     cat >> index.html << EOF
	<TR>
	  <TD><BR>
EOF
     i=$((i + 1))
  done

  cat >> index.html << EOF
  </TABLE>
EOF
fi

if [ $generate_ocnice_diags -eq 1 ]; then
  if [ $generate_ohc_trends -eq 1 ] || \
     [ $generate_sst_trends -eq 1 ] || \
     [ $generate_seaice_trends -eq 1 ]; then
       
    # Generating time series ocn/ice part of index.html file
    cat >> index.html << EOF
    <br>
    <br>
    </TABLE>
    <hr noshade size=2 size="100%">

    <font color=red size=+1><b>Time Series Plots: Global/Hemispheric means (OCN/ICE)</b></font>
    </b></font>

    <div style="text-align:left">
    <font color=peru size=-1>$casename (Years: $begin_yr_ts-$end_yr_ts)</font><br>
    </div>

    <hr noshade size=2 size="100%">

    <TABLE>
EOF
    if [ $generate_sst_trends -eq 1 ]; then
      cat >> index.html << EOF
      <TR>
        <TH ALIGN=LEFT><A HREF="sst_global_${casename}.png">Global SST</a>
EOF
    fi
    if [ $generate_ohc_trends -eq 1 ]; then
      cat >> index.html << EOF
      <TR>
        <TH ALIGN=LEFT><A HREF="OHCAnomaly_global_${casename}.png">Global OHC</a>
EOF
    fi
    if [ $generate_seaice_trends -eq 1 ]; then
      cat >> index.html << EOF
      <TR>
        <TH ALIGN=LEFT><A HREF="iceAreaNH_${casename}.png">NH Ice Area</a>
      <TR>
        <TH ALIGN=LEFT><A HREF="iceAreaSH_${casename}.png">SH Ice Area</a>
      <TR>
        <TH ALIGN=LEFT><A HREF="iceVolumeNH_${casename}.png">NH Ice Volume</a>
      <TR>
        <TH ALIGN=LEFT><A HREF="iceVolumeSH_${casename}.png">SH Ice Volume</a>
EOF
    fi
  fi
fi


if [ $generate_atm_diags -eq 1 ]; then
  # Generating climatology (atm) part of index.html file
  cat >> index.html << EOF
  <TR>
  <TD><BR>
  </TABLE>
  <hr noshade size=2 size="100%">
  <font color=red size=+1><b>Climatology Plots (ATM)</b></font><br>

  <div style="text-align:left">
  <font color=peru size=-1>$casename (Years: $begin_yr_climo-$end_yr_climo)</font><br>
  <font color=peru size=-1>$ref_case_text</font>
  </div>

  <hr noshade size=2 size="100%">

  <TABLE>
EOF

  if [ "$ref_case" == "obs" ]; then
    source $coupled_diags_home/bash_scripts/var_list_climo_model_vs_obs.bash
  else
    source $coupled_diags_home/bash_scripts/var_list_climo_model_vs_model.bash
  fi

  var_grp_unique_set=()
  grp_interp_grid_set=()

  i=0
  while [ $i -lt ${#var_group_set[@]} ]; do

     add_var=1

     j=0
     while [ $j -lt ${#var_grp_unique_set[@]} ]; do
        if [[ "${var_group_set[$i]}" =~ "${var_grp_unique_set[$j]}" ]]; then
          add_var=0
        fi
        j=$((j+1))
     done

     if [ $add_var -eq 1 ]; then
       var_grp_unique_set=("${var_grp_unique_set[@]}" "${var_group_set[$i]}")
       grp_interp_grid_set=("${grp_interp_grid_set[@]}" "${interp_grid_set[$i]}")
     fi

     i=$((i + 1))
  done


  i=0
  while [ $i -lt ${#var_grp_unique_set[@]} ]; do

     if [ "$ref_case" == "obs" ]; then
       grp_text="${var_grp_unique_set[$i]} (${grp_interp_grid_set[$i]})"
     else
       grp_text="${var_grp_unique_set[$i]}"
     fi

     cat >> index.html << EOF
	<TR>
	  <TH><BR>
	  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
	  <TH>DJF
	  <TH>JJA
	  <TH>ANN
EOF

     j=0
     while [ $j -lt ${#var_set[@]} ]; do
        var="${var_set[$j]}"

        if [ "${var_group_set[$j]}" == "${var_grp_unique_set[$i]}" ]; then
          if [ "$ref_case" == "obs" ]; then
            ref_casename_plot="${interp_grid_set[$j]}"
          else
            ref_casename_plot="$ref_case"  
          fi

          cat >> index.html << EOF
		<TR>
		  <TH ALIGN=LEFT>$var 
		  <TD ALIGN=LEFT>${var_name_set[$j]}
		  <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_climo_DJF.png">plot</a>
		  <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_climo_JJA.png">plot</a>
		  <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_climo_ANN.png">plot</a>
EOF
        fi
        j=$((j + 1))
     done

     cat >> index.html << EOF
	<TR>
	  <TD><BR>
EOF

     i=$((i + 1))
  done

  cat >> index.html << EOF
  </TABLE>
EOF
fi

# Generate ENSO diags section

if [ $generate_atm_enso_diags -eq 1 ]; then

  cat >> index.html << EOF
  <br>
  <hr noshade size=2 size="100%">

  <font color=red size=+1><b>ENSO Diagnostics (ATM)</b></font><br>

  <div style="text-align:left">
  <font color=peru size=-1>$casename (Years: $begin_yr_climateIndex-$end_yr_climateIndex)</font><br>
  <font color=peru size=-1>$ref_case_text_ts</font>
  </div>

  <hr noshade size=2 size="100%">

<!-- 
  <br>
  <font color=green size=+1><b>Equatorial SOI Index</b></font><br>
  <TABLE>
        <TR>
          <TH ALIGN=LEFT><A HREF="${casename}_PSL_ANN_EQSOI.png">EQSOI</a> 
        <TR>
          <TD><BR>
  </TABLE>
-->

  <br>
  <font color=green size=+1><b>NINO Index</b></font><br>
  <TABLE>
        <TR>
          <TH ALIGN=LEFT><A HREF="${casename}_TS_ANN_NINO.png">Nino3, Nino3.4, Nino4</a> 
        <TR>
          <TD><BR>
  </TABLE>


  <br>
  <font color=green size=+1><b>EQSOI and Nino3.4 Index</b></font><br>
  <TABLE>
        <TR>
          <TH ALIGN=LEFT><A HREF="${casename}_ANN_EQSOI_Nino3.4.png">EQSOI, Nino 3.4</a> 
        <TR>
          <TD><BR>
  </TABLE>


  <br>
  <font color=green size=+1><b>ENSO Seasonality</b></font><br>
  <TABLE>
        <TR>
          <TH ALIGN=LEFT><A HREF="${casename}_TS_seasonality_NINO.png">Nino3, Nino3.4, Nino4</a> 
        <TR>
          <TD><BR>
  </TABLE>
EOF


  if [ $ref_case == obs ]; then
        source $coupled_diags_home/bash_scripts/var_list_enso_diags_climo.bash
  else
        source $coupled_diags_home/bash_scripts/var_list_enso_diags_model_vs_model.bash
  fi

  var_grp_unique_set=()
  grp_interp_grid_set=()

  i=0

  for grp in "${var_group_set[@]}"; do

        add_var=1

        for temp_grp in "${var_grp_unique_set[@]}"; do
                if [ "$grp" == "$temp_grp" ]; then
                        add_var=0
                fi
        done

        if [ $add_var -eq 1 ]; then
                var_grp_unique_set=("${var_grp_unique_set[@]}" "$grp")
                grp_interp_grid_set=("${grp_interp_grid_set[@]}" "${interp_grid_set[$i]}")
        fi

        i=$((i+1))
  done


  j=0

  cat >> index.html << EOF
        <br>
        <font color=green size=+1><b>Meridional Avg. Over Tropical Pacific (5S-5N)</b></font><br>
        <br>

        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do

        if [ $ref_case == obs ]; then
                grp_text="$grp (${grp_interp_grid_set[$j]})"
        else
                grp_text=$grp
        fi

        cat >> index.html << EOF
        <TR>
          <TH><BR>
          <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
          <TH>DJF
          <TH>JJA
          <TH>ANN
EOF

        i=0
        for var in "${var_set[@]}"; do

                if [ "${var_group_set[$i]}" == "$grp" ]; then

                        if [ $ref_case == obs ]; then
                                ref_casename_plot=${interp_grid_set[$i]}
                        else
                                ref_casename_plot=$ref_case
                        fi

                        cat >> index.html << EOF
                        <TR>
                          <TH ALIGN=LEFT>$var 
                          <TD ALIGN=LEFT>${var_name_set[$i]}
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_meridional_avg_Tropical_Pacific_DJF.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_meridional_avg_Tropical_Pacific_JJA.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_meridional_avg_Tropical_Pacific_ANN.png">plot</a>
EOF
                fi
                i=$((i+1))
        done

        cat >> index.html << EOF
        <TR>
          <TD><BR>
EOF

        j=$((j+1))
  done


  cat >> index.html << EOF
  </TABLE>
EOF

# Generating index.html section for Bjerkenes feedbacks plots

  var_list_file=$coupled_diags_home/bash_scripts/var_list_enso_diags_bjerknes_feedback.bash
  source $var_list_file

  temp_unique_grp_list_file=$log_dir/temp_unique_grp_list_file.bash

  bash $coupled_diags_home/bash_scripts/generate_unique_group_list.bash $var_list_file $temp_unique_grp_list_file

  source $temp_unique_grp_list_file


  j=0

  cat >> index.html << EOF
        <br>
        <br>
        <font color=green size=+1><b>Bjerknes Feedback: (Nino4 TAUX vs. Nino3 SST)</b></font><br>
        <br>
        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do

        if [ "$grp" != "Temperature" ]; then

		if [ $ref_case == obs ]; then
			grp_text="$grp (${grp_interp_grid_set[$j]})"
		else
			grp_text=$grp
		fi

                cat >> index.html << EOF
                <TR>
                  <TH><BR>
                  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
                  <TH>Scatter Plot
EOF

		i=0
		for var in "${var_set[@]}"; do

			if [ "${var_group_set[$i]}" == "$grp" ]; then

				if [ $ref_case == obs ]; then
					ref_casename_plot=${interp_grid_set[$i]}
				else
					ref_casename_plot=$ref_case
				fi

                                cat >> index.html << EOF
                                <TR>
                                  <TH ALIGN=LEFT>$var 
                                  <TD ALIGN=LEFT>${var_name_set[$i]}
                                  <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_feedback_${var}_Nino4_ANN_TS_Nino3_ANN.png">plot</a>
EOF
                        fi
                        i=$((i+1))
                done

                cat >> index.html << EOF
                <TR>
                  <TD><BR>
EOF

        fi

        j=$((j+1))

  done
  cat >> index.html << EOF
  </TABLE>
EOF

# Generating index.html section for ENSO heat flux-SST feedbacks plots

  var_list_file=$coupled_diags_home/bash_scripts/var_list_enso_diags_heat_flux-sst_feedbacks.bash
  source $var_list_file

  temp_unique_grp_list_file=$log_dir/temp_unique_grp_list_file.bash

  bash $coupled_diags_home/bash_scripts/generate_unique_group_list.bash $var_list_file $temp_unique_grp_list_file

  source $temp_unique_grp_list_file


  j=0

  cat >> index.html << EOF
        <br>
        <br>
        <font color=green size=+1><b>Heat Flux-SST Feedbacks: Nino3 Region</b></font><br>
        <br>
        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do

        if [ "$grp" != "Temperature" ]; then

		if [ $ref_case == obs ]; then
			grp_text="$grp (${grp_interp_grid_set[$j]})"
		else
			grp_text=$grp
		fi

                cat >> index.html << EOF
                <TR>
                  <TH><BR>
                  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
                  <TH>Scatter Plot
EOF

		i=0
		for var in "${var_set[@]}"; do

			if [ "${var_group_set[$i]}" == "$grp" ]; then

				if [ $ref_case == obs ]; then
					ref_casename_plot=${interp_grid_set[$i]}
				else
					ref_casename_plot=$ref_case
				fi

                                cat >> index.html << EOF
                                <TR>
                                  <TH ALIGN=LEFT>$var 
                                  <TD ALIGN=LEFT>${var_name_set[$i]}
                                  <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_feedback_${var}_Nino3_ANN_TS_Nino3_ANN.png">plot</a>
EOF
                        fi
                        i=$((i+1))
                done

                cat >> index.html << EOF
                <TR>
                  <TD><BR>
EOF

        fi

        j=$((j+1))

  done
  cat >> index.html << EOF
  </TABLE>
EOF

# Generating index.html section for std. dev. and ENSO Evolution Plots

  var_list_file=$coupled_diags_home/bash_scripts/var_list_enso_diags_time_series.bash
  source $var_list_file

  temp_unique_grp_list_file=$log_dir/temp_unique_grp_list_file.bash

  bash $coupled_diags_home/bash_scripts/generate_unique_group_list.bash $var_list_file $temp_unique_grp_list_file

  source $temp_unique_grp_list_file


  j=0

  cat >> index.html << EOF
        <br>
        <br>
        <font color=green size=+1><b>Tropical Pacific: Inter-annual Std. Dev.</b></font><br>
        <br>
        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do


	if [ $ref_case == obs ]; then
		grp_text="$grp (${grp_interp_grid_set[$j]})"
	else
		grp_text=$grp
	fi

	cat >> index.html << EOF
	<TR>
	  <TH><BR>
	  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
	  <TH>DJF
	  <TH>JJA
	  <TH>ANN
EOF

	i=0
	for var in "${var_set[@]}"; do

		if [ "${var_group_set[$i]}" == "$grp" ]; then

			if [ $ref_case == obs ]; then
				ref_casename_plot=${interp_grid_set[$i]}
			else
				ref_casename_plot=$ref_case
			fi

			cat >> index.html << EOF
                        <TR>
                          <TH ALIGN=LEFT>$var 
                          <TD ALIGN=LEFT>${var_name_set[$i]}
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_stddev_Greater_Tropical_Pacific_DJF.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_stddev_Greater_Tropical_Pacific_JJA.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}-${ref_casename_plot}_${var}_stddev_Greater_Tropical_Pacific_ANN.png">plot</a>
EOF
		fi
		i=$((i+1))
	done

	cat >> index.html << EOF
	<TR>
	  <TD><BR>
EOF


        j=$((j+1))

  done
  cat >> index.html << EOF
  </TABLE>
EOF


#Generate index.html section for Regression Plots


  j=0

  cat >> index.html << EOF
        <br>
        <br>
        <font color=green size=+1><b>Regression on Nino3 Index</b></font><br>
        <br>
        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do


	if [ $ref_case == obs ]; then
		grp_text="$grp (${grp_interp_grid_set[$j]})"
	else
		grp_text=$grp
	fi

	cat >> index.html << EOF
	<TR>
	  <TH><BR>
	  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
	  <TH>DJF
	  <TH>JJA
	  <TH>ANN
EOF

	i=0
	for var in "${var_set[@]}"; do

		if [ "${var_group_set[$i]}" == "$grp" ]; then

			if [ $ref_case == obs ]; then
				ref_casename_plot=${interp_grid_set[$i]}
			else
				ref_casename_plot=$ref_case
			fi

			cat >> index.html << EOF
                        <TR>
                          <TH ALIGN=LEFT>$var 
                          <TD ALIGN=LEFT>${var_name_set[$i]}
                          <TD ALIGN=LEFT><A HREF="${casename}_regr_${var}_global_DJF_TS_Nino3_DJF.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}_regr_${var}_global_JJA_TS_Nino3_JJA.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}_regr_${var}_global_ANN_TS_Nino3_ANN.png">plot</a>
EOF
		fi
		i=$((i+1))
	done

	cat >> index.html << EOF
	<TR>
	  <TD><BR>
EOF


        j=$((j+1))

  done
  cat >> index.html << EOF
  </TABLE>
EOF



#Generate index.html section for ENSO evolution Plots


  j=0

  cat >> index.html << EOF
        <br>
        <br>
	<font color=green size=+1><b>ENSO Evolution: Lead-lag Regression/Correlation on Nino3.4 Index</b></font><br>
        <br>
        <TABLE>
EOF

  for grp in "${var_grp_unique_set[@]}"; do

	if [ $ref_case == obs ]; then
		grp_text="$grp (${grp_interp_grid_set[$j]})"
	else
		grp_text=$grp
	fi

	cat >> index.html << EOF
	<TR>
	  <TH><BR>
	  <TH ALIGN=LEFT><font color=brown size=+1>$grp_text</font>
          <TH>Regression
          <TH>Correlation
EOF

	i=0
	for var in "${var_set[@]}"; do

		if [ "${var_group_set[$i]}" == "$grp" ]; then

			if [ $ref_case == obs ]; then
				ref_casename_plot=${interp_grid_set[$i]}
			else
				ref_casename_plot=$ref_case
			fi

			cat >> index.html << EOF
                        <TR>
                          <TH ALIGN=LEFT>$var 
                          <TD ALIGN=LEFT>${var_name_set[$i]}
                          <TD ALIGN=LEFT><A HREF="${casename}_ENSO_evolution_regr_${var}_global_ANN_TS_Nino3.4_ANN.png">plot</a>
                          <TD ALIGN=LEFT><A HREF="${casename}_ENSO_evolution_corr_${var}_global_ANN_TS_Nino3.4_ANN.png">plot</a>
EOF
		fi
		i=$((i+1))
	done

	cat >> index.html << EOF
	<TR>
	  <TD><BR>
EOF


        j=$((j+1))

  done
  cat >> index.html << EOF
  </TABLE>
EOF


fi


cat >> index.html << EOF
  <hr noshade size=2 size="100%">
  </BODY>
  </HTML>
EOF

cp -u $coupled_diags_home/images/acme-banner_1.jpg $www_dir/$plots_dir_name
mv index.html $www_dir/$plots_dir_name
chmod -R a+rx $www_dir/$plots_dir_name

echo
echo "Standalone HTML file with links to coupled diagnostic plots generated!"
echo "$plots_dir/index.html"
echo

if [ $www_link == "" ]; then
  echo "Viewable link not available..."
  echo "Machine $machname either not supported for that or online shared space not available for it"
else
  echo "Viewable at: $www_link"
fi
echo

cd -
