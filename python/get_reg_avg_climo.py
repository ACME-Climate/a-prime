import numpy
from netCDF4 			import Dataset

from get_season_name       	import get_season_name
from read_monthly_data_ts 	import read_monthly_data_ts
from get_season_months_index 	import get_season_months_index
from get_days_in_season_months 	import get_days_in_season_months
from get_reg_area_avg 		import get_reg_area_avg
from aggregate_ts_weighted 	import aggregate_ts_weighted
from read_climo_file		import read_climo_file

def get_reg_avg_climo (	  indir,
			  casename, 
			  field_name,
		          interp_grid,
			  interp_method,
			  begin_yr,
			  end_yr,
			  begin_month,
			  end_month,
			  reg,
			  debug = False):

	season = get_season_name(begin_month, end_month)

	field, lat_reg, lon_reg, units_out = read_climo_file(
						 indir = indir,
						 casename = casename,
						 field_name = field_name,
						 season = season,
						 begin_yr = begin_yr,
						 end_yr = end_yr,
						 interp_grid = interp_grid,
						 interp_method = interp_method,
						 reg = reg,
						 debug = debug)


	area_average = get_reg_area_avg(field = field,
					lat = lat_reg,
					lon = lon_reg,
					debug = True)

	a, n_months_season = get_season_months_index(begin_month, end_month)

	return area_average, units_out
