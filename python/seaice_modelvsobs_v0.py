
import os
import subprocess
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.colors as cols
from matplotlib.colors import BoundaryNorm
from matplotlib.colors import from_levels_and_colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mpas_xarray import preprocess_mpas, preprocess_mpas_timeSeriesStats, remove_repeated_time_index
import numpy as np
import numpy.ma as ma
import random as rd
import sys, math
import xarray as xr
import pandas as pd
from netCDF4 import Dataset as netcdf_dataset
#import calendar

try:
    get_ipython()
    # Place figures within document
    get_ipython().magic(u'pylab inline')
    #pylab.rcParams['figure.figsize'] = (18.0, 10.0) # Large figures
    get_ipython().magic(u'matplotlib inline')
    
    indir       = "/global/project/projectdirs/acme/ACMEv0_lowres/B1850C5_ne30_v0.4/ice/postprocessing/"
    ##indir       = "/usr/projects/climate/ACMEv0_lowres/B1850C5_ne30_v0.4/ice/postprocessing/"
    casename    = "B1850C5_ne30_v0.4"
    plots_dir  = "plots"
    obsdir    = "/global/project/projectdirs/acme/observations/SeaIce/"
    remapfile = "/global/project/projectdirs/acme/milena/remapfiles/map_gx1v6_TO_0.5x0.5degree_blin.160413.nc"
    climo_yr1 = 51
    climo_yr2 = 70
except:
    import argparse
    parser = argparse.ArgumentParser(description="Plot 2-d field on a polar stereographic projection")
    parser.add_argument("--indir", dest = "indir", required=True,
        help = "full path to climatological model data directory")
    parser.add_argument("-c", "--casename", dest = "casename", required=True,
        help = "casename of the run")
    parser.add_argument("--plots_dir", dest = "plots_dir", required=True,
        help = "full path to plot directory")
    parser.add_argument("--obsdir", dest = "obsdir", required=True,
        help = "full path to main observational data directory")
    parser.add_argument("--remapfile", dest = "remapfile", required=True,
        help = "remapping filename (with full path)")
    parser.add_argument("--climo_year1", dest = "climo_yr1", required=True,
        help = "first year over which seasonal climatologies will be computed")
    parser.add_argument("--climo_year2", dest = "climo_yr2", required=True,
        help = "second year over which seasonal climatologies will be computed")
    args = parser.parse_args()
    indir     = args.indir
    casename  = args.casename
    plots_dir = args.plots_dir
    obsdir    = args.obsdir
    remapfile = args.remapfile
    climo_yr1 = int(args.climo_yr1)
    climo_yr2 = int(args.climo_yr2)

indir_regridded = "%s/regridded" % indir
if os.path.isdir("%s" % indir_regridded) != True:
    print "\nRegridded directory does not exist. Create it...\n"
    os.mkdir("%s" % indir_regridded)
    
# v0 model climatological filenames (calculated previously)
climofile_winNH = "aice.%s.cice.h.years%04d-%04d.JFM" % (casename,climo_yr1,climo_yr2)
climofile_sumNH = "aice.%s.cice.h.years%04d-%04d.JAS" % (casename,climo_yr1,climo_yr2)
climofile_winSH = "aice.%s.cice.h.years%04d-%04d.DJF" % (casename,climo_yr1,climo_yr2)
climofile_sumSH = "aice.%s.cice.h.years%04d-%04d.JJA" % (casename,climo_yr1,climo_yr2)
climofile_on = "hi.%s.cice.h.years%04d-%04d.ON" % (casename,climo_yr1,climo_yr2)
climofile_fm = "hi.%s.cice.h.years%04d-%04d.FM" % (casename,climo_yr1,climo_yr2)

# Obs filenames
obs_iceconc_filenameNH_win1 = "%s/SSMI/NASATeam_NSIDC0051/SSMI_NASATeam_gridded_concentration_NH_jfm.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameNH_sum1 = "%s/SSMI/NASATeam_NSIDC0051/SSMI_NASATeam_gridded_concentration_NH_jas.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameSH_win1 = "%s/SSMI/NASATeam_NSIDC0051/SSMI_NASATeam_gridded_concentration_SH_djf.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameSH_sum1 = "%s/SSMI/NASATeam_NSIDC0051/SSMI_NASATeam_gridded_concentration_SH_jja.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameNH_win2 = "%s/SSMI/Bootstrap_NSIDC0079/SSMI_Bootstrap_gridded_concentration_NH_jfm.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameNH_sum2 = "%s/SSMI/Bootstrap_NSIDC0079/SSMI_Bootstrap_gridded_concentration_NH_jas.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameSH_win2 = "%s/SSMI/Bootstrap_NSIDC0079/SSMI_Bootstrap_gridded_concentration_SH_djf.interp0.5x0.5.nc" % obsdir
obs_iceconc_filenameSH_sum2 = "%s/SSMI/Bootstrap_NSIDC0079/SSMI_Bootstrap_gridded_concentration_SH_jja.interp0.5x0.5.nc" % obsdir
obs_icethick_filenameNH_on = "%s/ICESat/ICESat_gridded_mean_thickness_NH_on.interp0.5x0.5.nc" % obsdir
obs_icethick_filenameNH_fm = "%s/ICESat/ICESat_gridded_mean_thickness_NH_fm.interp0.5x0.5.nc" % obsdir
obs_icethick_filenameSH_on = "%s/ICESat/ICESat_gridded_mean_thickness_SH_on.interp0.5x0.5.nc" % obsdir
obs_icethick_filenameSH_fm = "%s/ICESat/ICESat_gridded_mean_thickness_SH_fm.interp0.5x0.5.nc" % obsdir
    
# Checks on directory/files existence:
if os.path.isdir("%s" % indir) != True:
    raise SystemExit("Model directory %s not found. Exiting..." % indir)
if os.path.isfile("%s/%s.nc" % (indir,climofile_winNH)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_winNH))
if os.path.isfile("%s/%s.nc" % (indir,climofile_sumNH)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_sumNH))
if os.path.isfile("%s/%s.nc" % (indir,climofile_winSH)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_winSH))
if os.path.isfile("%s/%s.nc" % (indir,climofile_sumSH)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_sumSH))
if os.path.isfile("%s/%s.nc" % (indir,climofile_on)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_on))
if os.path.isfile("%s/%s.nc" % (indir,climofile_fm)) != True:
    raise SystemExit("Model file %s/%s not found. Exiting..." % (indir,climofile_fm))
#
if os.path.isfile("%s" % obs_iceconc_filenameNH_win1) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameNH_win1)
if os.path.isfile("%s" % obs_iceconc_filenameNH_sum1) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameNH_sum1)
if os.path.isfile("%s" % obs_iceconc_filenameSH_win1) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameSH_win1)
if os.path.isfile("%s" % obs_iceconc_filenameSH_sum1) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameSH_sum1)
if os.path.isfile("%s" % obs_iceconc_filenameNH_win2) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameNH_win2)
if os.path.isfile("%s" % obs_iceconc_filenameNH_sum2) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameNH_sum2)
if os.path.isfile("%s" % obs_iceconc_filenameSH_win2) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameSH_win2)
if os.path.isfile("%s" % obs_iceconc_filenameSH_sum2) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_iceconc_filenameSH_sum2)
if os.path.isfile("%s" % obs_icethick_filenameNH_on) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_icethick_filenameNH_on)
if os.path.isfile("%s" % obs_icethick_filenameNH_fm) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_icethick_filenameNH_fm)
if os.path.isfile("%s" % obs_icethick_filenameSH_on) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_icethick_filenameSH_on)
if os.path.isfile("%s" % obs_icethick_filenameSH_fm) != True:
    raise SystemExit("Obs file %s not found. Exiting..." % obs_icethick_filenameSH_fm)


#subprocess.check_output(["which", "ncremap"], stderr=subprocess.STDOUT)


#plotting rules
axis_font = {'size':'16'}    
title_font = {'size':'20', 'color':'black', 'weight':'normal'}


# Regrid v0 model fields
print "  Regrid previously computed climatologies of comparison model sea-ice fields..."
# TO-DO: add a check on whether regridded file already exists
climofile_winNH_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_winNH)
climofile_sumNH_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_sumNH)
climofile_winSH_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_winSH)
climofile_sumSH_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_sumSH)
climofile_on_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_on)
climofile_fm_regridded = "%s/%s_interp0.5x0.5.nc" % (indir_regridded,climofile_fm)

call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_winNH) + climofile_winNH_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call
#
call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_sumNH) + climofile_sumNH_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call
#
call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_winSH) + climofile_winSH_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call
#
call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_sumSH) + climofile_sumSH_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call
#
call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_on) + climofile_on_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call
#
call = "ncks -O --rnr=0.05 --map=" + remapfile + " %s/%s.nc " % (indir,climofile_fm) + climofile_fm_regridded
if subprocess.call(call, shell=True):
    print 'Error with call ', call


# Load in sea-ice data
print "  Load sea-ice data and observations..."
#  Model...
# ice concentrations
f = netcdf_dataset(climofile_winNH_regridded,mode='r')
iceconc_winNH = f.variables["aice"][:]
lons = f.variables["ni"][:]
lats = f.variables["nj"][:]
print "Min lon: ", np.amin(lons), "Max lon: ", np.amax(lons)
print "Min lat: ", np.amin(lats), "Max lat: ", np.amax(lats)
Lons, Lats = np.meshgrid(lons, lats)
f.close()

f = netcdf_dataset(climofile_sumNH_regridded,mode='r')
iceconc_sumNH = f.variables["aice"][:]
f.close()

f = netcdf_dataset(climofile_winSH_regridded,mode='r')
iceconc_winSH = f.variables["aice"][:]
f.close()

f = netcdf_dataset(climofile_sumSH_regridded,mode='r')
iceconc_sumSH = f.variables["aice"][:]
f.close()

# ice thickness
f = netcdf_dataset(climofile_on_regridded,mode='r')
icethick_on = f.variables["hi"][:]
f.close()

f = netcdf_dataset(climofile_fm_regridded,mode='r')
icethick_fm = f.variables["hi"][:]
f.close()

#  ...and observations
# ice concentrations from NASATeam (or Bootstrap) algorithm
f = netcdf_dataset(obs_iceconc_filenameNH_win1,mode='r')
obs_iceconc_winNH1 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameNH_sum1,mode='r')
obs_iceconc_sumNH1 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameSH_win1,mode='r')
obs_iceconc_winSH1 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameSH_sum1,mode='r')
obs_iceconc_sumSH1 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameNH_win2,mode='r')
obs_iceconc_winNH2 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameNH_sum2,mode='r')
obs_iceconc_sumNH2 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameSH_win2,mode='r')
obs_iceconc_winSH2 = f.variables["AICE"][:]
f.close()

f = netcdf_dataset(obs_iceconc_filenameSH_sum2,mode='r')
obs_iceconc_sumSH2 = f.variables["AICE"][:]
f.close()

# ice thickness from IceSat
f = netcdf_dataset(obs_icethick_filenameNH_on,mode='r')
obs_icethick_onNH = f.variables["HI"][:]
f.close()

f = netcdf_dataset(obs_icethick_filenameNH_fm,mode='r')
obs_icethick_fmNH = f.variables["HI"][:]
f.close()

f = netcdf_dataset(obs_icethick_filenameSH_on,mode='r')
obs_icethick_onSH = f.variables["HI"][:]
f.close()

f = netcdf_dataset(obs_icethick_filenameSH_fm,mode='r')
obs_icethick_fmSH = f.variables["HI"][:]
f.close()

# from % to fraction:
iceconc_winNH = 0.01*iceconc_winNH
iceconc_sumNH = 0.01*iceconc_sumNH
iceconc_winSH = 0.01*iceconc_winSH
iceconc_sumSH = 0.01*iceconc_sumSH
    
# Mask concentration fields
#iceconc_winNH[ iceconc_winNH < 0.15 ] = ma.masked
#iceconc_sumNH[ iceconc_sumNH < 0.15 ] = ma.masked
#iceconc_winSH[ iceconc_winSH < 0.15 ] = ma.masked
#iceconc_sumSH[ iceconc_sumSH < 0.15 ] = ma.masked
## For some reason the following:
## obs_iceconc_winNH1[ obs_iceconc_winNH1 < 0.15 ] = ma.masked
## does not work... Milena's workaround:
#obs_iceconc_winNH1[ obs_iceconc_winNH1 < 0.15 ] = -9999
#obs_iceconc_winNH1 = ma.masked_values(obs_iceconc_winNH1,-9999)
#obs_iceconc_sumNH1[ obs_iceconc_sumNH1 < 0.15 ] = -9999
#obs_iceconc_sumNH1 = ma.masked_values(obs_iceconc_sumNH1,-9999)
#obs_iceconc_winSH1[ obs_iceconc_winSH1 < 0.15 ] = -9999
#obs_iceconc_winSH1 = ma.masked_values(obs_iceconc_winSH1,-9999)
#obs_iceconc_sumSH1[ obs_iceconc_sumSH1 < 0.15 ] = -9999
#obs_iceconc_sumSH1 = ma.masked_values(obs_iceconc_sumSH1,-9999)
#obs_iceconc_winNH2[ obs_iceconc_winNH2 < 0.15 ] = -9999
#obs_iceconc_winNH2 = ma.masked_values(obs_iceconc_winNH2,-9999)
#obs_iceconc_sumNH2[ obs_iceconc_sumNH2 < 0.15 ] = -9999
#obs_iceconc_sumNH2 = ma.masked_values(obs_iceconc_sumNH2,-9999)
#obs_iceconc_winSH2[ obs_iceconc_winSH2 < 0.15 ] = -9999
#obs_iceconc_winSH2 = ma.masked_values(obs_iceconc_winSH2,-9999)
#obs_iceconc_sumSH2[ obs_iceconc_sumSH2 < 0.15 ] = -9999
#obs_iceconc_sumSH2 = ma.masked_values(obs_iceconc_sumSH2,-9999)

# Mask thickness fields
icethick_on[ icethick_on == 0 ] = ma.masked
icethick_fm[ icethick_fm == 0 ] = ma.masked
obs_icethick_onNH = ma.masked_values(obs_icethick_onNH,0)
obs_icethick_fmNH = ma.masked_values(obs_icethick_fmNH,0)
obs_icethick_onSH = ma.masked_values(obs_icethick_onSH,0)
obs_icethick_fmSH = ma.masked_values(obs_icethick_fmSH,0)
# Obs thickness should be nan above 86 (ICESat data)
obs_icethick_onNH[ Lats > 86 ] = -9999
obs_icethick_onNH = ma.masked_values(obs_icethick_onNH,-9999)
obs_icethick_fmNH[ Lats > 86 ] = -9999
obs_icethick_fmNH = ma.masked_values(obs_icethick_fmNH,-9999)

# Find differences model-obs
diff_winNH1 = iceconc_winNH - obs_iceconc_winNH1
diff_sumNH1 = iceconc_sumNH - obs_iceconc_sumNH1
diff_winSH1 = iceconc_winSH - obs_iceconc_winSH1
diff_sumSH1 = iceconc_sumSH - obs_iceconc_sumSH1

diff_winNH2 = iceconc_winNH - obs_iceconc_winNH2
diff_sumNH2 = iceconc_sumNH - obs_iceconc_sumNH2
diff_winSH2 = iceconc_winSH - obs_iceconc_winSH2
diff_sumSH2 = iceconc_sumSH - obs_iceconc_sumSH2

diff_onNH = icethick_on - obs_icethick_onNH
diff_onSH = icethick_on - obs_icethick_onSH
diff_fmNH = icethick_fm - obs_icethick_fmNH
diff_fmSH = icethick_fm - obs_icethick_fmSH

#ind_iceext = modelArray_NH2 > 0.15
#modelArray_NH2 = modelArray_NH2.where(ind_iceext)

#degrees_to_radians = math.pi / 180.0


def plot_polar_comparison(
    Lons, 
    Lats, 
    modelArray, 
    obsArray, 
    diffArray,
    title=None, 
    fileout="plot_polar_comparison.png",
    plotProjection = "npstere",
    latmin =  50.0,
    lon0 = 0,
    #modelObsMin = None, 
    #modelObsMax = None,
    #diffMin = None,
    #diffMax = None,
    modelTitle = "Model",
    obsTitle = "Observations",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = None,
    cmapDiff="RdBu_r",
    clevsDiff = None,
    #cmapLinear = "false",
    cbarlabel = "%",
    xFigSize=8,
    yFigSize=22,
    figDPI=300):

    ## get array min maxes
    #modelArrayMin = modelArray.min()
    #modelArrayMax = modelArray.max()
    #obsArrayMin = obsArray.min()
    #obsArrayMax = obsArray.max()
    #diffArrayMin = diffArray.min()
    #diffArrayMax = diffArray.max()

    #modelObsMinData = min(modelArrayMin,obsArrayMin)
    #modelObsMaxData = max(modelArrayMax,obsArrayMax)
    ##modelObsMinData = 0
    ##modelObsMaxData = 1
    
    #diffLargerMinMax = max(abs(diffArrayMin),abs(diffArrayMax))
    
    #if (modelObsMin == None and modelObsMax == None):
    #    modelObsMin = modelObsMinData
    #    modelObsMax = modelObsMaxData

    #if (diffMin == None and diffMax == None):
    #    diffMin = -diffLargerMinMax
    #    diffMax =  diffLargerMinMax
            
    # set up figure
    fig = plt.figure(1, figsize=(xFigSize, yFigSize), dpi=figDPI)
    if (title != None):
        fig.suptitle(title, y=0.95, **title_font)
    m = Basemap(projection=plotProjection,boundinglat=latmin,lon_0=lon0,resolution='l')
    x, y = m(Lons, Lats) # compute map proj coordinates
    #if (clevsModelObs != None and cmapLinear == "false"):
    if clevsModelObs != None:
        nice_cmap = plt.get_cmap(cmapModelObs)
        # choose numbers between 0 and 255 (number of colors in nice_cmap):
        lev_cmap = nice_cmap([20,80,110,140,170,200,230,255]) # good for inferno
        #lev_cmap = nice_cmap([10,80,110,140,170,200,210,240]) # better for spectral
        new_cmap = cols.ListedColormap(lev_cmap,"mv_cmap")
        norm = mpl.colors.BoundaryNorm(clevsModelObs, new_cmap.N)
    if clevsDiff != None:
        nice_cmapdiff = plt.get_cmap(cmapDiff)
        lev_cmapdiff = nice_cmapdiff([0,40,80,127,127,170,210,255]) # good for RdBu_r
        new_cmapdiff = cols.ListedColormap(lev_cmapdiff,"mv_cmapdiff")
        normdiff = mpl.colors.BoundaryNorm(clevsDiff, new_cmapdiff.N)

    ax = plt.subplot(3,1,1)
    plt.title(modelTitle, y=1.06, **axis_font)
    m.drawcoastlines()
    m.fillcontinents(color='grey',lake_color='white')
    #m.drawparallels(np.arange(-80.,81.,10.),labels=[True,True,False,False])
    #m.drawmeridians(np.arange(-180.,181.,20.),labels=[False,False,True,True])
    m.drawparallels(np.arange(-80.,81.,10.))
    m.drawmeridians(np.arange(-180.,181.,20.),labels=[True,True,True,True])
    if clevsModelObs != None:
        cs = m.contourf(x,y,modelArray,cmap=new_cmap,norm=norm,spacing='uniform',levels=clevsModelObs)
        #if cmapLinear == "false":
        #    cs = m.contourf(x,y,modelArray,cmap=new_cmap,norm=norm,spacing='uniform',levels=clevsModelObs)
        #else:
        #    cs = m.contourf(x,y,modelArray,cmap=cmapModelObs,spacing='uniform',levels=clevsModelObs)     
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True',ticks=clevsModelObs, boundaries=clevsModelObs)
    else:
        cs = m.contourf(x,y,modelArray,cmap=cmapModelObs,spacing='uniform')
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True')
    cbar.set_label(cbarlabel)
    #xlb1,ylb1 = m(-5,82)
    #xlb2,ylb2 = m(-5,62)
    #ax1 = pylab.gca()
    #t = ax1.text(xlb1,ylb1,u"%g\N{DEGREE SIGN}N" % 80)
    #t = ax1.text(xlb2,ylb2,u"%g\N{DEGREE SIGN}N" % 60)

    ax = plt.subplot(3,1,2)
    plt.title(obsTitle, y=1.06, **axis_font)
    m.drawcoastlines()
    m.fillcontinents(color='grey',lake_color='white')
    m.drawparallels(np.arange(-80.,81.,10.))
    m.drawmeridians(np.arange(-180.,181.,20.),labels=[True,True,True,True])
    if clevsModelObs != None:
        cs = m.contourf(x,y,obsArray,cmap=new_cmap,norm=norm,spacing='uniform',levels=clevsModelObs)
        #if cmapLinear == "false":
        #    cs = m.contourf(x,y,obsArray,cmap=new_cmap,norm=norm,spacing='uniform',levels=clevsModelObs)
        #else:
        #    cs = m.contourf(x,y,obsArray,cmap=cmapModelObs,spacing='uniform',levels=clevsModelObs)    
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True',ticks=clevsModelObs, boundaries=clevsModelObs)
    else:
        cs = m.contourf(x,y,obsArray,cmap=cmapModelObs,spacing='uniform')
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True')
    cbar.set_label(cbarlabel)

    ax = plt.subplot(3,1,3)
    plt.title(diffTitle, y=1.06, **axis_font)
    m.drawcoastlines()
    m.fillcontinents(color='grey',lake_color='white')
    m.drawparallels(np.arange(-80.,81.,10.))
    m.drawmeridians(np.arange(-180.,181.,20.),labels=[True,True,True,True])
    if clevsDiff != None:
        cs = m.contourf(x,y,diffArray,cmap=new_cmapdiff,norm=normdiff,spacing='uniform',levels=clevsDiff)
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True',ticks=clevsDiff, boundaries=clevsDiff)
    else:
        cs = m.contourf(x,y,diffArray,cmap=cmapDiff,spacing='uniform')
        cbar = m.colorbar(cs,location='right',pad="15%",spacing='uniform',extendfrac='auto',                          extendrect='True')    
    cbar.set_label(cbarlabel)
    
    plt.savefig(fileout)


print "  Make winter ice concentration plots for the NH and SH..."
# Plot Northern Hemisphere JFM sea-ice concentration (NASATeam algorithm)
suptitle = "Ice concentration"
# Choose 9 levels (for 8-color colormap):
clevsModelObs = [0.15,0.4,0.7,0.9,0.94,0.96,0.98,0.99,1]
clevsDiff = [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8] 

plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_winNH, 
    obs_iceconc_winNH1, 
    diff_winNH1,
    title="%s (JFM, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcNASATeamNH_%s_JFM_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I NASATeam)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    #cmapModelObs = "spectral",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Northern Hemisphere JFM sea-ice concentration (Bootstrap algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_winNH, 
    obs_iceconc_winNH2, 
    diff_winNH2,
    title="%s (JFM, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcBootstrapNH_%s_JFM_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I Bootstrap)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    #cmapModelObs = "spectral",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Southern Hemisphere JJA sea-ice concentration (NASATeam algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_sumSH, 
    obs_iceconc_sumSH1, 
    diff_sumSH1,
    title="%s (JJA, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcNASATeamSH_%s_JJA_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I NASATeam)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Southern Hemisphere JJA sea-ice concentration (Bootstrap algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_sumSH, 
    obs_iceconc_sumSH2, 
    diff_sumSH2,
    title="%s (JJA, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcBootstrapSH_%s_JJA_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I Bootstrap)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


print "  Make summer ice concentration plots for the NH and SH..."
# Plot Northern Hemisphere JAS sea-ice concentration (NASATeam algorithm)
clevsModelObs = [0.15,0.3,0.5,0.7,0.8,0.85,0.9,0.95,1]
clevsDiff = [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8]

plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_sumNH, 
    obs_iceconc_sumNH1, 
    diff_sumNH1,
    title="%s (JAS, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcNASATeamNH_%s_JAS_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I NASATeam)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Northern Hemisphere JAS sea-ice concentration (Bootstrap algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_sumNH, 
    obs_iceconc_sumNH2, 
    diff_sumNH2,
    title="%s (JAS, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcBootstrapNH_%s_JAS_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I Bootstrap)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Southern Hemisphere DJF sea-ice concentration (NASATeam algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_winSH, 
    obs_iceconc_winSH1, 
    diff_winSH1,
    title="%s (DJF, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcNASATeamSH_%s_DJF_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I NASATeam)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


# Plot Southern Hemisphere DJF sea-ice concentration (Bootstrap algorithm)
plot_polar_comparison(
    Lons, 
    Lats, 
    iceconc_winSH, 
    obs_iceconc_winSH2, 
    diff_winSH2,
    title="%s (DJF, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/iceconcBootstrapSH_%s_DJF_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0.15,
    #modelObsMax = None,
    #diffMin = -0.80,
    #diffMax = 0.80,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (SSM/I Bootstrap)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "false",
    cbarlabel = "%")


print "  Make ice thickness plots for the NH..."
# Plot Northern Hemisphere FM sea-ice thickness
suptitle = "Ice thickness"
# Choose 9 levels (for 8-color colormap):
#clevsModelObs = [0.2,0.6,1,1.4,1.8,2.2,2.6,3,3.4,3.8]
clevsModelObs = [0,0.25,0.5,1,1.5,2,2.5,3,3.5]
#clevsDiff = [-3,-2,-0.5,-0.1,0,0.1,0.5,2,3]
clevsDiff = [-2.5,-2,-0.5,-0.1,0,0.1,0.5,2,2.5]

plot_polar_comparison(
    Lons, 
    Lats, 
    icethick_fm, 
    obs_icethick_fmNH, 
    diff_fmNH,
    title="%s (FM, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/icethickNH_%s_FM_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0,
    #modelObsMax = None,
    #diffMin = None,
    #diffMax = None,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (ICESat)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "true",
    cbarlabel = "m")


# Plot Northern Hemisphere ON sea-ice thickness
plot_polar_comparison(
    Lons, 
    Lats, 
    icethick_on, 
    obs_icethick_onNH, 
    diff_onNH,
    title="%s (ON, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/icethickNH_%s_ON_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "npstere",
    latmin =  50,
    lon0 = 0,
    #modelObsMin = 0,
    #modelObsMax = None,
    #diffMin = None,
    #diffMax = None,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (ICESat)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "true",
    cbarlabel = "m")


print "  Make ice thickness plots for the SH..."
# Plot Southern Hemisphere ON sea-ice thickness
clevsModelObs = [0,0.2,0.4,0.6,0.8,1,1.5,2,2.5]

plot_polar_comparison(
    Lons, 
    Lats, 
    icethick_on, 
    obs_icethick_onSH, 
    diff_onSH,
    title="%s (ON, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/icethickSH_%s_ON_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0,
    #modelObsMax = None,
    #diffMin = None,
    #diffMax = None,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (ICESat)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "true",
    cbarlabel = "m")


# Plot Southern Hemisphere FM sea-ice thickness
plot_polar_comparison(
    Lons, 
    Lats, 
    icethick_fm, 
    obs_icethick_fmSH, 
    diff_fmSH,
    title="%s (FM, years %04d-%04d)" % (suptitle,climo_yr1,climo_yr2),
    fileout="%s/icethickSH_%s_FM_years%04d-%04d.png" % (plots_dir,casename,climo_yr1,climo_yr2),
    plotProjection = "spstere",
    latmin =  -50,
    lon0 = 180,
    #modelObsMin = 0,
    #modelObsMax = None,
    #diffMin = None,
    #diffMax = None,
    modelTitle = "%s" % casename,
    obsTitle = "Observations (ICESat)",
    diffTitle = "Model-Observations",
    cmapModelObs = "inferno",
    clevsModelObs = clevsModelObs,
    cmapDiff="RdBu_r",
    #cmapDiff="bwr",
    #cmapDiff="seismic",
    clevsDiff = clevsDiff,
    #cmapLinear = "true",
    cbarlabel = "m")



