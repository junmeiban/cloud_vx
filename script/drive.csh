#!/bin/csh -f

#######################
# for IMGER: lon,lat -> lat,lon
#######################

#./ncpdq_IMERG_latlon.csh

#######################
#get accumulated rain total and convert_mpas
#  -tried to write accumulated rain by using python script, results same as by using NCO command
#######################
#./raintot.csh

#######################
#plot rainfall distribution: 
#  -ModelRain(unstructuredGrid and latlonGrid), ObsRain, METPairs
#######################
#python plotPrecip.py  #(import precip_util)

#######################
#setup MET and submit jobs
#  - cloud_vx/bin/MET/driver_script_with_python_manual_timeloop_mpmd.ksh
#  - cloud_vx/bin/MET/mpmd_cmdfile_grid
#  - cloud_vx/bin/python_stuff.py
#  - cloud_vx/static/MET/met_config/GridStatConfig_trad
#  #######################
cd /glade/scratch/jban/cloud_vx/bin/MET
qsub mpmd_pbs_submit_grid.bash

#######################
# get score:
#######################
#getscore.csh




