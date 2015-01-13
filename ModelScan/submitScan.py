#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from optparse import OptionParser
import argparse
#from BaconAna.Utils.generate import fileExists

#parser = OptionParser()
#parser.add_option('--q'         ,action='store',type='string',dest='q'   ,default='8nh', help='queue')

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_22_patch1/src/BaconAna/Utils/python/ntuples'

def fileExists(filename,label):
   #cmsStage %s /store/cmst3/group/monojet/mc/%s/%s' %(filename,label,filename)
   sc=None
   print '%s ls eos/cms//store/cmst3/group/monojet/mc/%s/%s | wc -l' %(eos,label,filename)
   exists = commands.getoutput('%s ls eos/cms//store/cmst3/group/monojet/mc/%s/%s | wc -l' %(eos,label,filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   print exists
   return int(exists) == 1

def localFileExists(filename):
   print 'ls ntuples/Output/%s | wc -l' %(filename) 
   exists = commands.getoutput('ls ntuples/Output/%s | wc -l' %(filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   print exists
   return int(exists) == 1

aparser = argparse.ArgumentParser()
aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1,5,10,25,50,100,150,200,300,400,500,600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1000,1250,1500,1750,2000])
aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[50,100,125,200,300,325,400,525,600,725,800,925,1000,1125,1200,1325,1400,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[1125,1200,1325,1400,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
aparser.add_argument('-w'  ,'--widthrange',nargs='+',type=int,default=[1])
#aparser.add_argument('-proc','--procrange',nargs='+',type=int,default=[800,801,805,806,810,811,820,821])
aparser.add_argument('-proc','--procrange',nargs='+',type=int,default=[805,806])
aparser.add_argument('-q'   ,'--q'        ,nargs='+',type=str,default=['1nd'])
aparser.add_argument('-o'   ,'--options'  ,nargs='+',type=str,default=[''])
aparser.add_argument('-m'   ,'--mod'      ,nargs='+',type=int,default=[8])


# Add couplings and mono X when they are ready
args = aparser.parse_args()

label=''
option=''
generate=False
if args.options[0].find('--monoV') > 0:
    label='_1'
    option='--monoV'

if args.options[0].find('--hinv') > 0:
    label='_2'
    option='--hinv'

if args.options[0].find('--monoJ') > 0:
    label='_3'
    option='--monoJ'

if args.options[0].find('--generate') > 0:
    label=label+'g'
    generate=True

print option,"Submitting by ",args.mod[0]
counter=0
#os.system('rm runlimit*.sh')
for dm in args.dmrange:
    for med in args.medrange:
        for width in args.widthrange:
           for proc in args.procrange:
              if option == '--hinv' and (proc==800 or proc==801 or proc > 809 or dm != 1):
                 continue
              if generate:
                 checkFileName='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
                 if label.find('_1') > -1:
                    checkFileName='MonoV_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
                 if fileExists(checkFileName,'model'):
                    continue
              #if not generate:
              #   if localFileExists('model_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'_0.root'):
              #      continue
              if counter ==  0: 
                 fileName=('runlimit_%s_%s_%s_%s%s.sh' % (dm,med,width,proc,label))
                #sub_file = open('runlimit_%s_%s_%s_%s%s.sh' % (dm,med,width,proc,label),'a')
              submit=counter % args.mod[0] == args.mod[0]-1
              sub_file  = open(fileName,'a')
              print "updating",fileName,counter
              if counter % args.mod[0] == 0:
                 sub_file.write('#!/bin/bash\n')
                 sub_file.write('cd %s \n'%os.getcwd())
                 sub_file.write('eval `scramv1 runtime -sh`\n')
                 sub_file.write('cd - \n')
              if generate:
                 sub_file.write('cp %s/generate.py . \n'%os.getcwd()) 
                 sub_file.write('./generate.py --dm %s --med %s --width %s --proc %s %s \n' % (dm,med,width,proc,option))
              else:
                 sub_file.write('cp %s/limit.py . \n'%os.getcwd()) 
                 sub_file.write('rm *.root        \n')
                 sub_file.write('./limit.py    --dm %s --med %s --width %s --proc %s %s \n' % (dm,med,width,proc,option))
              if submit:
                 sub_file.write('hadd model_%s_%s_%s_%s_%s.rootX model_*.rootX \n' % (dm,med,width,proc,label))
                 sub_file.write('mv model_%s_%s_%s_%s_%s.rootX %s/Output/ \n' % (dm,med,width,proc,label,basedir))
              sub_file.close()
              counter=counter+1
              if submit:
                 counter = 0
                 fileName=('runlimit_%s_%s_%s_%s%s.sh' % (dm,med,width,proc,label))
                 os.system('chmod +x %s' % os.path.abspath(sub_file.name))
                 os.system('bsub -q %s -o out.%%J %s' % (args.q[0],os.path.abspath(sub_file.name)))
                 
