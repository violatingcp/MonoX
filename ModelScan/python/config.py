#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array import array
#from BaconAna.Utils.generate import *

basedir ='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_22_patch1/src/BaconAna/Utils/python/ntuples'
mjcut   ='(met > 0 && (jdphi < 1.8 || jpt_2 < 30) && abs(jeta_1) < 2.0 )'
monojet ='19.7*mcweight*(jpt_1 > 150 )*'+mjcut
boosted ='19.7*mcweight*(fjmtrim > 60 && fjmtrim < 112 && fjt2t1 < 0.5 && fjpt > 250 && met > -250)*'+mjcut
resolved='19.7*mcweight*(60 < mjj && mjj < 112 && ptjj > 160 && dm_pt > 250 && !(fjmtrim > 60 && fjmtrim < 112 && fjt2t1 < 0.5 && fjpt > 250) && jpt_1 > 30 && jpt_2 > 30)'

