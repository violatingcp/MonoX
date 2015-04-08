#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array import array

def runlimitFile(card='card.txt',basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/'):
   sub_file = open('runlimit.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('cd %s \n'% basedir)
   sub_file.write('eval `scramv1 runtime -sh` \n')
   sub_file.write('cd - \n')
   sub_file.write('cp  %s/Cards/%s . \n' % (basedir,card))
   sub_file.write('cp  %s/mono-x-vtagged*.root . \n'            % (basedir))
   sub_file.write('cp  %s/photon_dimuon_*.root      . \n'            % (basedir))
   sub_file.write('combine -M  Asymptotic -C 0.90 -t -1 %s \n'  % card)
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

def rescalesignal(card='card.txt',scale=1):
   lFile=''
   lFile=os.popen('cat %s  | grep card | grep root | awk \'{print $4}\' | uniq' % card).read()
   lAFile=lFile.rstrip().split('\n')
   os.system('cp %s %s' % (card,'rescale'+card))
   for pFile in lAFile:
      lTFile  = ROOT.TFile(pFile)
      lTOFile = ROOT.TFile('rescale'+pFile,'RECREATE')
      old=''
      for key in lTFile.GetListOfKeys():
         pHist=key.ReadObj().Clone()
         if old == pHist.GetName():
            continue
         old=pHist.GetName()
         pHist.SetDirectory(0)
         pHist.Scale(scale)
         pHist.Write()
      with open("Xrescale%s" % card,    "wt") as fout:
         with open("rescale%s" % card, "rt") as fin:
            for line in fin:
               fout.write(line.replace(pFile, 'rescale'+pFile))
      os.system('cp %s %s' % ('Xrescale'+card,'rescale'+card))

def runlimit(card='card.txt',basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/'):
   runlimitFile(card,basedir)
   scale=checkrange()
   if scale > 100 or scale < 0.05:
      rescalesignal(card,scale)
      runlimitFile('rescale'+card,basedir)
      return scale
   return 1

