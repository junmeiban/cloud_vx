#from __future__ import print_function
import os
import sys
import numpy as np
from datetime import *
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
#### for Plotting
import matplotlib.cm as cm
import matplotlib.axes as maxes
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
from matplotlib.cm import ScalarMappable
from matplotlib.gridspec import GridSpec
from cartopy.feature import NaturalEarthFeature
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.mpl.ticker as cticker
import precip_util as pru
#matplotlib.use('Agg')
#plt.switch_backend('agg')

startTime = datetime.now()

#choose data type you want to plot:
#dataSource = 'origFile'          #MPAS original ouput on unstructuredGrid
#dataSource = 'unstructuredGrid'  #MPAS unstructuredGrid: based on "dataSource = 'origFile'", total rain computed from ncbo, ncap2 
#dataSource = 'latlonGrid'        #MPAS latlon grid: based on "dataSource = 'unstructuredGrid'", converted by convert_mpas
#dataSource = 'metpairs'          #MET output pairs
#dataSource = 'CMORPH'            #OBS
dataSource = 'IMERG'             #OBS

if (dataSource == 'metpairs'):
  obsName = "CMORPH"
  #obsName = "IMERG"

def readdata():

  CDATE = pru.SDATE
  while CDATE <= pru.EDATE: 
    DATE = CDATE.strftime('%Y%m%d%H') 
    print('DATE=',DATE,dataSource)

    if (dataSource == 'CMORPH' or dataSource == 'IMERG'):

      print('plot obs',dataSource)
      # /glade/work/jban/OBS
      fileDir = pru.TopDir[:-7]+'/OBS'
      gridFile = pru.getGridFile(DATE,fileDir,dataSource)
      
      lats,lons,var = pru.obsRead(DATE,gridFile,dataSource)
      #pru.plot(lats,lons,var,iexp,expName,DATE,Date1,Date2,unstructuredGrid)
      print('var=',var)
      pru.plot(lats,lons,var,DATE,dataSource,"","",dataSource)

    else:
      print('plot others') 
      ###### !!!!! 
      for fcTDelta in np.arange(0, pru.fcRange+pru.interval, pru.interval):

        fcDate1 = CDATE + timedelta(days=fcTDelta)
        Date1=fcDate1.strftime("%Y%m%d%H")
        fcDate2 = CDATE + timedelta(days=fcTDelta+pru.interval)
        Date2= fcDate2.strftime("%Y%m%d%H")

        for iexp, expName in enumerate(pru.expNames):
          if (dataSource == 'metpairs'):

            print('plot metpairs',fcTDelta)
            leadt = int(fcTDelta *24)
            fileDir = pru.TopDir+'/cloud_vx_'+pru.expLongNames[iexp]+'/metprd/'+DATE+'/f'+str(leadt)+'/precip/CMORPH/'
            lats,lons,modelrain,obsrain = pru.metpairsRead(DATE,leadt,fileDir)

            pru.plot(lats,lons,modelrain,DATE,expName+'Pairs',Date1,Date2,dataSource)
            pru.plot(lats,lons,obsrain,DATE,obsName+'Pairs',Date1,Date2,dataSource)

          if (dataSource == 'origFile' or dataSource == 'unstructuredGrid' or dataSource == 'latlonGrid'):

            fileDir = pru.TopDir+'/'+pru.expLongNames[iexp]+'/FC2/'+DATE
            gridFile1 = pru.getGridFile(Date1,fileDir,dataSource)
            print('gridFile1=',gridFile1)
            lats, lons = pru.gridRead(Date1,gridFile1)

            if (dataSource == 'origFile'):
              gridFile2 = pru.getGridFile(Date2,fileDir,dataSource)
              print('gridFile2=',gridFile2)
              var = pru.getRain(gridFile1,gridFile2)
            else:
              var = pru.varRead('rain',gridFile1) 
              #print(var.size,var.shape,np.max(var[:,:]),np.min(var[:,:]))

            if (dataSource == 'origFile' or dataSource == 'unstructuredGrid'):
              print('check min=',var.shape, var.shape,max(var),min(var))
              for i in range(len(lons)):
                if lons[i] > 180:
                  lons[i] = lons[i]-360
 
            pru.plot(lats,lons,var,DATE,expName,Date1,Date2,dataSource)
          #print('time used:',datetime.now() - startTime)
    CDATE += pru.DATEINC

def main():
    readdata()

if __name__ == '__main__': main()
