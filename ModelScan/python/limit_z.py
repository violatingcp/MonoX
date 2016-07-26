#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array    import array
from optparse import OptionParser
from MonoX.ModelScan.generate      import loadmonov,loadmonojet,getWidthXS
from MonoX.ModelScan.ntuple        import makeNtuple,ntuplexs
from MonoX.ModelScan.reweightmap   import obtainbase
from MonoX.ModelScan.config        import *
from MonoX.ModelScan.limittools    import *

parser = OptionParser()
parser.add_option('--dm'      ,action='store',type='float',dest='dm'       ,default=1,              help='Dark Matter Mass')
parser.add_option('--med'     ,action='store',type='float',dest='med'      ,default=125,            help='Mediator Mass')
parser.add_option('--width'   ,action='store',type='float',dest='width'    ,default=1,              help='Width (in Min width units)')
parser.add_option('--proc'    ,action='store',type='float',dest='proc'     ,default=805,            help='Process(800=V,801=A,805=S,806=P)')
parser.add_option('--gq'      ,action='store',type='float',dest='gq'       ,default=1,              help='coupling to quarks')
parser.add_option('--gdm'     ,action='store',type='float',dest='gdm'      ,default=1,              help='coupling to dark matter')
parser.add_option('--label'   ,action='store',type='string',dest='label'   ,default='model',        help='eos label')
parser.add_option('--monoV'   ,action='store_true',         dest='monov'   ,default=False,          help='Run mono V generation') # need a few more options for monoV
parser.add_option('--monoGGZ' ,action='store_true',         dest='monov'   ,default=False,          help='Run mono V generation') # need a few more options for monoV
(options,args) = parser.parse_args()

def runlimitFile(card='card.txt',basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/',scale=1):
   sub_file = open('runlimit.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('cd %s \n'% basedir)
   sub_file.write('eval `scramv1 runtime -sh` \n')
   sub_file.write('cd - \n')
   sub_file.write('combineCards %s > tmp.txt  \n' % (card))
   sub_file.write('combine -M  Asymptotic %s --rMin %s --rMax %s \n'  % (card,-10*scale,10*scale))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))
   
def checkrange():
   lTFile = ROOT.TFile('higgsCombineTest.Asymptotic.mH120.root')
   lTree  = lTFile.Get('limit')
   lTree.GetEntry(2)
   bestexp=lTree.limit
   scale=bestexp
   return scale

def runlimit(card='card.txt',basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/'):
   runlimitFile(card,basedir)
   scale=checkrange()
   if scale > 100 or scale < 0.05:
      runlimitFile('rescale'+card,basedir,scale)
      return scale
   return 1

def replace(iFile,iBin,iYield0,iYield1):
   with open('%s' % iFile            ,"wt") as fout:
      with open('%s' % iFile+"_fixed","rt") as fin:
         for line in fin:
            tmpline =    line.replace('qqBin%s' % iBin ,str(iYield0))
            tmpline = tmpline.replace('ggBin%s' % iBin ,str(iYield1))
            fout.write(tmpline)

def setupCard(iVFile,iGFile):
   lQQH  = 0
   lGGH  = 0
   if iVFile != '':
      lVFile = r.TFile(iVFile)
      lQQH   = lVFile.Get("")
   if iGFile != '':
      lGFile = r.TFile(iGFile)
      lGGH   = lFile.Get("")

   os.system('cp %s/templates/*.txt .' % basedir)
   for i0 in range(0,6):
      lYield0 = 0
      lYiled1 = 0
      if lQQH != 0:
         lYield0 = lQQH.GetBinContent(i0+1)
      if lGGH != 0:
         lYield1 = lGGH.GetBinContent(i0+1)
      replace('zll_bin%s.txt' % i0,i0,lYield0,lYield1)

def fullresults(iBase,label,dm,med,width,proc,g,gdm):
   xst=[1,1]
   setupCard(lVFile,lGFile)
   scale=runlimit('zll*.txt' ,basedir)
   xst=makeNtuple(0,True,1.,label,dm,med,width,proc,xst,gq,gdm,1.)

if __name__ == "__main__":
   label=options.label
   dm=options.dm
   med=options.med
   width=options.width
   gq=options.gq
   gdm=options.gdm
   proc=options.proc
   #Base results
   fullresults(dm,med,width,proc,options.gq,options.gdm)      
