import os
import sys
import csv
import numpy
import numpy as np
#from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from copy import deepcopy
import datetime as dt
import fnmatch
import numpy.random as npr
import plot_utils as pu
import var_utils as vu

expLongNames = os.getenv('expLongNames', 'please set expLongNames')
expNames = os.getenv('expNames','please set expNames')
expLongNames = expLongNames.split()
expNames = expNames.split()
expDirectory = os.getenv('TopDir','/glade/scratch/$user/pandac/')
nExp  = len(expNames)
metrics = ['GSS'] #,'PODY'] #['FBIAS','GSS','FAR']
thresholds = ['>1.0', '>2.5', '>=5.0', '>=7.5', '>=10.0', '>=15.0', '>=20.0', '>=30.0', '>=40.0', '>=50.0', '>=70.0', '>=100', '>=150', '>=200', '>=250']
#thresholds = ['>=10.0']
def readdata():
  for metric in metrics: 
    for threshold in thresholds:
      for iexp, expName in enumerate(expNames):
        print(iexp, expName)
        with open(expDirectory+'/'+expLongNames[iexp]+'/metprd/'+metric+'_'+threshold+'_IMERG','r') as myfile:
          print('logplot')
          allvartmp = list(csv.reader(myfile, delimiter=" "))
          allvar = np.array(allvartmp[:])
          # 11: mean; 14: mean_bcl; 15: mean_bcu
          scoretmp = allvar[:,11]
          scoretmp_bcl = allvar[:,14]
          scoretmp_bcu = allvar[:,15]          
          score0 = scoretmp.astype(np.float)
          score0_bcl = scoretmp_bcl.astype(np.float)
          score0_bcu = scoretmp_bcu.astype(np.float)
          print(score0)
        if (iexp == 0):
          scorelist = [score0] 
          scorelist_bcl = [score0_bcl]
          scorelist_bcu = [score0_bcu] 
        else:
          scorelist = scorelist + [score0]
          scorelist_bcl = scorelist_bcl + [score0_bcl]
          scorelist_bcu = scorelist_bcu + [score0_bcu]

      plot(scorelist,scorelist_bcl,scorelist_bcu,metric,threshold)

def plot(scorelist,scorelist_bcl,scorelist_bcu,metric,threshold):

    fig,ax = plt.subplots(1,sharex=True)
    plt.grid(True)
    #forx = range(1,11)
    #forx = range(1,8)
    forx = range(1,6)

    SigColor = ['k', 'm', 'y', 'c','g']
    marker = ['.','.','.','.','.']
    linesty = ['-','-','-','-','-']
    plotSpecs = ['k-', 'm-', 'y-', 'c-','g-']

    print(forx)
    for iexp in range(0, nExp):
      print(iexp) 
      ax.plot(forx,scorelist[iexp],color=SigColor[iexp],ls=linesty[iexp],marker=marker[iexp])

    ax.set_title('(a) ', fontsize = 12,loc='left')
    ax.legend(expNames, loc='upper right',fontsize=12,frameon=False)
    ax.set_xlabel('Lead Time (day)',fontsize=16)
    ax.set_xticks(forx[::1])
    ax.set_xlim(forx[0], forx[len(forx)-1])
    ax.set_ylim(0.0,0.4)
    ax.set_ylabel(metric,fontsize=16)
    plt.savefig(metric+'_'+threshold+'.png',dpi=200,bbox_inches='tight')
    plt.close()

def main():
    readdata()

if __name__ == '__main__': main()   
