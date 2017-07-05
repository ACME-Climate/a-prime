import numpy
from scipy import stats
from netCDF4 import Dataset

from read_monthly_data_ts import read_monthly_data_ts
from get_season_months_index import get_season_months_index
from get_days_in_season_months import get_days_in_season_months
from get_reg_area_avg import get_reg_area_avg
from aggregate_ts_weighted import aggregate_ts_weighted
from get_reg_seasonal_avg import get_reg_seasonal_avg
from get_season_name import get_season_name
from get_reg_avg_climo import get_reg_avg_climo
from remove_seasonal_cycle_monthly_data import remove_seasonal_cycle_monthly_data
from standardize_time_series import standardize_time_series
from regress_index_field import regress_index_field
from aggregate_time_series_data import aggregate_time_series_data
 
def get_regress_index_field (indir,
			   casename,
			   field_name,
			   interp_grid,
			   interp_method,
			   begin_yr,
			   end_yr,
			   begin_month,
			   end_month,
			   aggregate,
			   reg,
			   reg_name,
			   no_ann,
			   stdize,
			   debug = False):


	print __name__, 'casename: ', casename

	index, n_months_season, units_index = get_reg_seasonal_avg (
							  indir         = indir,
							  casename      = casename,
							  field_name    = field_name[1],
							  interp_grid   = interp_grid[1],
							  interp_method = interp_method[1],
							  begin_yr      = begin_yr,
							  end_yr        = end_yr,
							  begin_month   = begin_month[1],
							  end_month     = end_month[1],
							  reg           = reg[1],
							  aggregate     = aggregate,
							  debug         = debug)


	if aggregate == 0 and no_ann == 1:
		index_no_ann = remove_seasonal_cycle_monthly_data(index, n_months_season, debug = debug)
		index = index_no_ann

	if stdize == 1:
		index_stddize = standardize_time_series(index)
		index = index_stddize


        field, lat_reg, lon_reg, area_reg, units_out = read_monthly_data_ts(indir = indir,
                                 casename = casename,
                                 field_name = field_name[0],
                                 interp_grid = interp_grid[0],
                                 interp_method = interp_method[0],
                                 begin_yr = begin_yr,
                                 end_yr = end_yr,
                                 begin_month = begin_month[0],
                                 end_month = end_month[0],
                                 reg = reg[0],
                                 debug = debug)

	if aggregate == 1:
		a, n_months_season = get_season_months_index(begin_month[0], end_month[0])

		day_wgts = get_days_in_season_months(begin_month[0], end_month[0])
		if debug: print __name__, 'day_wgts: ', day_wgts
	
		field_seasonal_avg = aggregate_time_series_data(field, n_months_season, day_wgts)
		
		field = field_seasonal_avg

	regr_matrix, const_matrix, corr_matrix, t_test_matrix, stderr_matrix = regress_index_field(index, field)

	units = units_out + '/' + units_index

	if stdize == 1:
		units = units_out

	return regr_matrix, t_test_matrix, lat_reg, lon_reg, units

if __name__ == "__main__":
	get_regress_index_field (indir = indir,
			       casename = casename,
                               field_name = field_name,
			       interp_grid = interp_grid,
			       interp_method = interp_method,
                               begin_yr = begin_yr,
                               end_yr = end_yr,
                               begin_month = begin_month,
                               end_month = end_month,
                               reg = reg,
			       reg_name = reg_name,
			       aggregate = aggregate,
			       no_ann = no_ann,
			       stdize = stdize,
                               debug = debug)
