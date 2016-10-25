#!/bin/csh -f

set scratch_dir = $argv[1]
set casename = $argv[2]
set compute_climo_var_list_file = $argv[3]


# Read in variable list for  diagnostics e.g FLUT, FSNT etc.
source $compute_climo_var_list_file
set n_var = $#var_set

# Read in list of seasons for which diagnostics are being computed
source $log_dir/season_info.temp
set n_seasons = $#begin_month_set
 
# Create Climatology of supplied fields
if ($casename != obs) then

	foreach i (`seq 1 $n_var`)
		set var = $var_set[$i]

		echo
		echo $casename $var
		echo

		foreach i (`seq 1 $n_seasons`)
			set begin_month = $begin_month_set[$i]
			set end_month   = $end_month_set[$i]
			set season_name = $season_name_set[$i]

			python python/create_climatology.py 	--indir $scratch_dir \
								-c $casename \
								-f $var \
								--begin_month $begin_month \
								--end_month $end_month >& $log_dir/climo_${casename}_${var}_$season_name.log &
		end
	end
endif

echo
echo Waiting for jobs to complete ...
echo

wait




