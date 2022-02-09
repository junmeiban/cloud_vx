from collections import defaultdict
from datetime import *
import os
import sys
import numpy as np
#from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import matplotlib.cm as cm
import matplotlib.axes as maxes
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from copy import deepcopy
import datetime as dt
import numpy.random as npr
import subprocess
from subprocess import Popen, PIPE
from netCDF4 import Dataset
import cartopy.crs as ccrs
from matplotlib.gridspec import GridSpec
from cartopy.feature import NaturalEarthFeature
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.mpl.ticker as cticker



TopDir="/glade/scratch/jban/pandac"
#control="cloud_vx_30km60km_2018_conv_1200km6km"
ncells=655362
staticFile="/glade/p/mmm/parc/liuz/pandac_common/static_from_duda/x1."+str(ncells)+".static.nc"
#expLongNames=['cloud_vx_30km60km_2018_conv_1200km6km','cloud_vx_30km60km_2018_conv_ama_1200km6km','cloud_vx_30km60km_2018_conv_amacld_1200km6km','cloud_vx_30km60km_2018_conv_amacld_mhs_1200km6km']
#expNames=['conv','clrama', 'cldama', 'clrmhs']

expLongNames=['30km60km_2018_conv_1200km6km']
expNames=['conv']

controlLongName=expLongNames[0]
controlName=expNames[0]

fcHours = 240 #os.getenv('fcHours', '0')
intervalHours=24 # os.getenv('intervalHours', '6')

SDATE = dt.datetime(2018,4,18,0,0,0)
EDATE = dt.datetime(2018,5,14,0,0,0)
fcRange = fcHours/24.
interval = intervalHours/24
DATEINC = dt.timedelta(days=interval)
#DATE = datetime.strptime(TDATE,'%Y%m%d%H')
print('fcRange,interval',fcRange, interval)

SKILL = "FBIAS" #"GSS" #,'PODY','FBIAS','FAR']
OBS_THRES="\>=10.0"
VX_MASK="FULL"
plotDiff = True
leadts = ['00', '24', '48', '72', '96', '120', '144', '168', '192', '216']
fcNums = len(leadts)
max_samples = 10000
expStats = SKILL+'_ci'

def getGridFile(date, fileDir, dataSource):
  print(date)
  d = datetime.strptime(date,'%Y%m%d%H')
  filedate= d.strftime('%Y-%m-%d_%H.%M.%S')

  if (dataSource == 'origFile'):
     gridFile = fileDir+'/mpasout.'+filedate+'.nc'
  elif (dataSource == 'unstructuredGrid'):
     #gridFile = fileDir+'/mpasout.'+filedate+'_rain.nc' 
     gridFile = fileDir+'/mpasout.'+date[:-2]+'_S000000-E235900_rain.nc'
  elif (dataSource == 'latlonGrid'):
     #gridFile = fileDir+'/mpasout.'+filedate+'_rain_latlon.nc'
     gridFile = fileDir+'/mpasout.'+date[:-2]+'_S000000-E235900_rain_latlon.nc' 
  elif (dataSource == 'CMORPH'):
     d = date[:-2]
     gridFile = fileDir+'/CMORPH/daily/CMORPH_V1.0_ADJ_0.25deg-DLY_00Z_'+d+'.nc'
  elif (dataSource == 'IMERG'):
     d = date[:-2]
     gridFile = fileDir+'/IMERG/daily/3B-DAY.MS.MRG.3IMERG.'+d+'-S000000-E235959.V06.nc4' 
     print('gridFile=',gridFile)
  return gridFile

def obsRead(date, gridFile, sourceObs):

  nc =Dataset(gridFile,'r')
  lats = np.array(nc.variables['lat'][:])
  lons = np.array(nc.variables['lon'][:])

  if (sourceObs == 'CMORPH'):
    varVals = np.array(nc.variables['cmorph'][0,:,:])
    varVals [varVals == -999.0] = 0. #np.NaN
  elif (sourceObs == 'IMERG'):
    varVals = np.array(nc.variables['precipitationCal'][0,:,:])
    varVals [varVals == -9999.9] = 0. #np.NaN
    varVals = varVals.reshape(len(lons),len(lats)).T

  return (lats,lons,varVals) 

def metpairsRead(date,leadt,fileDir):

  DATEINC = dt.timedelta(days=int(leadt)/24.)
  CDATE = datetime.strptime(date,'%Y%m%d%H')
  CDATE += DATEINC
  d = CDATE.strftime('%Y%m%d')
  
  #gridFile = fileDir+'/grid_stat_MPAS_F72_precip_720000L_20180421_000000V_pairs.nc' 
  gridFile = fileDir+'/grid_stat_MPAS_F'+str(leadt)+'_precip_'+str(leadt)+'0000L_'+d+'_000000V_pairs.nc'
  print('gridFile=',gridFile)
  nc =Dataset(gridFile,'r')
  lats = np.array(nc.variables['lat'][:])
  lons = np.array(nc.variables['lon'][:])
  model = np.array(nc.variables['FCST_MPAS_ALL_GLOBAL'][:,:])
  obs = np.array(nc.variables['OBS_CMORPH_ALL_GLOBAL'][:,:])
  return (lats,lons,model,obs)
 
def gridRead(date, gridFile):
  ncData = Dataset(gridFile, 'r')

  dims = ncData.dimensions.keys()

  if ('nCells' in dims):
     print('the vars are on unstructured grid, read static.nc for latCell and lonCell')
     # read static.nc file
     ncData = Dataset(staticFile, 'r')
     lats = np.array( ncData.variables['latCell'][:] ) * 180.0 / np.pi
     lons = np.array( ncData.variables['lonCell'][:] ) * 180.0 / np.pi

  if ('latitude' in dims):
     print('the vars are on lat lon grid')
     lats = np.array( ncData.variables['latitude'][:])
     lons = np.array( ncData.variables['longitude'][:])

  ncData.close()

  return (lats,lons)

def varRead(varName, gridFile):

  ncData = Dataset(gridFile, 'r')

  dims = ncData.dimensions.keys()

  if ('latitude' in dims):
     print('the vars are on lat lon grid')
     varVals = np.array(ncData.variables[varName][0,:,:])      
  if ('nCells' in dims):
     print('the vars are on unstructured grid, read static.nc for latCell and lonCell')
     # read static.nc file
     varVals = np.array(ncData.variables[varName][0,:])

  return varVals

def getRain(gridFile1, gridFile2):

  ncData1 = Dataset(gridFile1, 'r')
  ncData2 = Dataset(gridFile2, 'r')

  rainc1 = np.array(ncData1.variables['rainc'][0,:])
  rainnc1 = np.array(ncData1.variables['rainnc'][0,:])

  rainc2 = np.array(ncData2.variables['rainc'][0,:])
  rainnc2 = np.array(ncData2.variables['rainnc'][0,:])

  rain1 = rainnc1+rainc1
  rain2 = rainnc2+rainc2

  varVals = rain2 - rain1

  return varVals

def getData(fname,VX_MASK,OBS_THRES):

    # define the data parsing
    # $25:TOTAL, $26:FY_OY, $27:FY_ON, $28:FN_OY, $29:FN_ON
    cmd="more " + fname + " | grep " + VX_MASK + " | grep "+ OBS_THRES + "\
         | awk '{ print $25\" \"$26\" \"$27\" \"$28\" \"$29}'"

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.communicate()[0]
    output2=output.decode('ascii').split('\n')[:-1]
    output3=[i.split(' ') for i in output2]
    #output3[0] :  remove redundant square brackets in a list
    #print('output3=',output3)
    vdata=np.asarray(output3[0],dtype=float)
    return vdata
def Skill(data,metrics):
    n11 = sum(list(zip(*data))[1])
    n10 = sum(list(zip(*data))[2])
    n01 = sum(list(zip(*data))[3])
    n00 = sum(list(zip(*data))[4])
    if (metrics == "GSS"):
       total = sum(list(zip(*data))[0])
       C = (n11+n10)*(n11+n01)*(1/total)
       stats = (n11-C)/(n11+n10+n01-C)
    if (metrics == "FBIAS"):
       stats = (n11+n10)/(n11+n01)
    if (metrics == "PODY"):
       stats = n11/(n11+n01)
    if (metrics == "FAR"):
       stats = n10/(n10+n11)
    return stats

def plot(lat,lon,var,Date, \
         source='', \
         titleDate1='', \
         titleDate2='', \
         dataSource='unstructuredGrid'):
        print('source=',source)
        crs = ccrs.PlateCarree()

        fig = plt.figure()
        gs = GridSpec(ncols=1, nrows=1, width_ratios=[1], wspace=0, hspace=0.0)
        ax = fig.add_subplot(gs[0], projection=crs)
        plot_background(ax)
        units = 'mm'

        clevs = [0, 1, 2.5, 5, 7.5, 10, 15, 20, 30, 40,
             50, 70, 100, 150, 200, 250] #, 300, 400, 500, 600, 750

        cmap_data = [(1.0, 1.0, 1.0),
                 (0.3137255012989044, 0.8156862854957581, 0.8156862854957581),
                 (0.0, 1.0, 1.0),
                 (0.0, 0.8784313797950745, 0.501960813999176),
                 (0.0, 0.7529411911964417, 0.0),
                 (0.501960813999176, 0.8784313797950745, 0.0),
                 (1.0, 1.0, 0.0),
                 (1.0, 0.6274510025978088, 0.0),
                 (1.0, 0.0, 0.0),
                 (1.0, 0.125490203499794, 0.501960813999176),
                 (0.9411764740943909, 0.250980406999588, 1.0),
                 (0.501960813999176, 0.125490203499794, 1.0),
                 (0.250980406999588, 0.250980406999588, 1.0),
                 (0.125490203499794, 0.125490203499794, 0.501960813999176),
                 (0.125490203499794, 0.125490203499794, 0.125490203499794),
                 (0.501960813999176, 0.501960813999176, 0.501960813999176)]
        cmap = mcolors.ListedColormap(cmap_data, 'precipitation')
        norm = mcolors.BoundaryNorm(clevs, cmap.N)
        print('chech figure0')
        if (dataSource == 'origFile' or dataSource == 'unstructuredGrid'):
           cs = ax.tripcolor(lon,lat,var, clevs, cmap=cmap, norm=norm, transform=crs)
        else:
           cs = ax.contourf(lon,lat,var,clevs, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())

        cbar1 = plt.colorbar(cs, orientation = 'horizontal', shrink=0.9, pad=0.045, ax=ax)
        cbar1.ax.tick_params(labelsize=6)
        if (dataSource == 'CMORPH' or dataSource == 'IMERG'):
          ax.set_title('Accumulated rainfall(mm) '+Date+' max:' +str(int(np.amax(var))),loc='center',fontsize=7)
          plt.savefig(source+'_'+Date+'.png',  bbox_inches='tight', dpi=300) 
        #elif (source == 'metpairs'):
        else:
          print('mpas source=',source)
          ax.set_title('Accumulated rainfall(mm) from '+titleDate1+' to '+titleDate2+' max:' +str(int(np.amax(var))),loc='center',fontsize=7)
          if (dataSource == 'origFile' or dataSource == 'unstructuredGrid'):
            plt.savefig(source+'_'+Date+'_S'+titleDate1+'_E'+titleDate2+'.png',  bbox_inches='tight', dpi=300)
          elif (dataSource == 'latlonGrid' or dataSource == 'metpairs'):
            plt.savefig(source+'_'+Date+'_S'+titleDate1+'_E'+titleDate2+'_latlon.png',  bbox_inches='tight', dpi=300)
#          elif (dataSource == 'latlonGrid'):

def plot_background(ax):
    ax.set_global()
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.8, edgecolor='black')
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='black', alpha=0.5, linestyle='dotted')
    gl.right_labels = False
    gl.top_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
    ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)
    gl.xlabel_style = {'size': 6}
    gl.ylabel_style = {'size': 6}
    return ax

def main():
    print ('This is not a runnable program.')
    os._exit(0)

if __name__ == '__main__': main()
