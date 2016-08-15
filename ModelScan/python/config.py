#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array import array

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
basedir ='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_4_12_patch1/src/MonoX/ModelScan'
#eosbasedir ='/store/user/rgerosa/MONOJET_ANALYSIS/GenTreeForInterpolation/'
eosbasedir ='/store/cmst3/user/pharris/monojet13/reweight'
eostopbasedir ='/store/user/snarayan/monotop80/private'
mjcut       ='(v_pt > 0 )'
monojet     ='1.0'#*(jpt_1 > 100)*(fjm < 60 || fjm > 112 || fjpt < 250)'
boosted     ='1.0*(fjm > 40 && fjm < 112 && fjpt > 150 && fjt2t1 < 0.6)*'+mjcut
monoz       ='0.067*12.9/8.6' # the factor of two is because the Z' DM model is majorana, the 1.1 based on closure
monojetReco ='1.0*genWeight'#*(genAK4JetPt > 100)*(genAK8JetMass < 60 || genAK8JetMass > 112 || genAK8JetPt < 250)'
boostedReco ='1.*(genAK8JetMass > 40 && genAK8JetMass < 112 && genAK8JetPt > 150 && genAK8JetTau2Tau1 < 0.6)'
monozReco   ='1.0'#mcWeight'
monot       ='0.001' 
monotReco   ='1.0'

mvrbins = [250,300,350,400,500,600,1000]
mvgbins = [100.,150.,200.,250,300,350,400,500,600,1000]
mvrcut  = "weight*(pfMetPt>250 && pfMetPt < 10000 && id==2)"
mjrbins = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]
mjgbins = [100.,150.,180.,200., 230., 260.0, 290.0, 320.0,350.0,370.0,390.0,410.0,430.0,450.0,470.0,490.0,510.0,530.0,550.0,570.0,590.0,615.0,640.0,665.0,690.0,715.0,740.0,765.0,790.0,815.0,840.0,870.,900.0,930.0,960.0,990.0,1020.0,1055.0,1090.0,1125.,1160.,1200.0,1250.0,1350.,1500.0]
mjrcut  = "weight*(pfMetPt>200 && pfMetPt < 10000 && id==1)"
mzrbins = [50.,100.,125.,150.,175.,200.,250.,350.]
mzgbins = [0.,50.,75.,100.,125.,150.,175.,200.,225.,250.,275.,300.,325.,350.,400.]
mzrcut  = "totalWeight*(totalWeight > 0)"
mtrbins = [250.,280.,310.,350.,400.,450.,600.,1000.]
mtgbins = [0.,100.,200.,220.,250.,280.,310.,350.,375.,400.,425.,450,500.,550.,600,700.,800.,1000.,1000000.]
mtrcut  = "signalWeight*(signalWeight > 0)"


