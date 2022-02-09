#!/bin/csh -f
#Leadt > 100

#source /glade/u/apps/ch/modulefiles/default/localinit/localinit.sh
#module purge
#module use /glade/p/ral/jntp/MET/MET_releases/modulefiles 
#module load met/9.0

setenv stat_analysis True
setenv grepScore False 

set scores = ('GSS' 'FAR' 'FBIAS' 'PODY')
set thresholds = ('>1.0' '>2.5' '>=5.0' '>=7.5' '>=10.0' '>=15.0' '>=20.0' '>=30.0' '>=40.0' '>=50.0' '>=70.0' '>=100' '>=150' '>=200' '>=250')
#setenv GSS True
#setenv FAR False #True
#setenv FBIAS False 
#setenv PODY Frue

if ($stat_analysis == True) then

stat_analysis -lookin 2018*/f*/precip/*/grid_stat*precip_???????L*stat \
 -config ../static/MET/met_config/StatAnalysisConfig -job summary \
 -line_type CTS -column PODY,FAR,GSS,FBIAS \
 -by MODEL,OBTYPE,FCST_LEAD,VX_MASK,FCST_THRESH,OBS_THRESH \
 -out_alpha 0.05 -out SA_summary.0p05_far_gss_pody_leadtgt100

stat_analysis -lookin 2018*/f*/precip/*/grid_stat*precip_??????L*stat \
 -config ../static/MET/met_config/StatAnalysisConfig -job summary \
 -line_type CTS -column PODY,FAR,GSS,FBIAS \
 -by MODEL,OBTYPE,FCST_LEAD,VX_MASK,FCST_THRESH,OBS_THRESH \
 -out_alpha 0.05 -out SA_summary.0p05_far_gss_pody_leadtlt100

endif

if ($grepScore == True) then
   set N=1
   while ($N <= ${#scores})
      set T=1
      while ($T <= ${#thresholds})
         rm log1 log2 log
         echo $scores[$N] $thresholds[$T]
#        grep 'GSS' SA_summary.0p05_far_gss_pody_leadtgt100 | grep '>=10.0' | & tee log2
         grep $scores[$N] SA_summary.0p05_far_gss_pody_leadtlt100 | grep $thresholds[$T] | & tee log1
         grep $scores[$N] SA_summary.0p05_far_gss_pody_leadtgt100 | grep $thresholds[$T] | & tee log2
         cat log1 log2 > log
         sed -e 's/  */ /g' log > $scores[$N]_$thresholds[$T] 
         @ T++
      end
      @ N++
   end
endif

#python score.py
  
