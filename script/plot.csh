#!/bin/csh -f
##set echo
#PBS -N plot 
#PBS -l select=1:ncpus=1:mpiprocs=1
#PBS -l walltime=4:59:59
#PBS -q regular
#PBS -A NMMM0043
#PBS -j oe
#PBS -o plot.log.out
#PBS -e plot.log.err

setenv currdir `basename "$PWD"`

setenv getscore  True 
setenv plotscore False 

setenv S_DATE  2019050100 #2018041800 #2020072400 #2020072400
setenv E_DATE  2019050500
setenv C_DATE  ${S_DATE}  # current-cycle date
setenv CYCLE_HOUR  24     # interval for forecast initialization time

set target = ('liuz_15km_coldstart' 'liuz_7km_coldstart' 'liuz_7km_coldstart_TP' 'liuz_15km_coldstart_TP')
set targetN = ('15kmColdStart' '7kmColdStart' '7kmColdStartCP' '15kmColdStartCP')

setenv expLongNames "$target"
setenv expNames     "$targetN"

setenv TopDir   /glade/scratch/jban/pandac/
setenv BIN_DIR  /glade/u/home/jban/bin
setenv ResultFromUser jban 

if ($ResultFromUser != $USER) then
   setenv TOP_origDir    /glade/scratch/liuz/pandac
   #mkdir ${TOP_DIR}/$currdir/
endif

if ($getscore == True) then

   set N=1
   while ($N <= ${#targetN})
      echo $TopDir/$target[$N]/metprd
      cp getscore.csh $TopDir/$target[$N]/metprd
      cd $TopDir/$target[$N]/metprd
      ./getscore.csh
      @ N++
   end
 
endif

if ($plotscore == True) then
   python score_nexp.py
endif

exit 0

