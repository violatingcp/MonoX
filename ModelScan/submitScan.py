#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from optparse import OptionParser
import argparse
from MonoX.ModelScan.config        import *

def check(fileName,med,dm,proc,iClean):
   lFile = ROOT.TFile().Open('root://eoscms//'+fileName)      
   lMono = [False,False]
   try:
      lFile.GetListOfKeys().GetEntries()
   except:
      return lMono
   for pFile in lFile.GetListOfKeys(): 
      pName1   = '_%s_%s_1.0'  % (str(med),str(dm))
      pName025 = '_%s_%s_0.25' % (str(med),str(dm))
      if pFile.GetName().find(pName1) > -1:
         lMono[0] = True
      if pFile.GetName().find(pName025) > -1:
         lMono[1] = True

   if iClean and not (lMono[0] and lMono[1]):
      print "Cleaning",fileName,lMono,lFile.GetListOfKeys()
      os.system('%s rm %s' % (eos,fileName))

   return lMono

def checkDetails(med,dm,proc,iClean=True):
   fileMonoJ='eos/cms/store/cmst3/group/monojet/mc/model4/MonoJ_%s_%s_%s.root' % (med,dm,proc)
   fileMonoW='eos/cms/store/cmst3/group/monojet/mc/model4/MonoW_%s_%s_%s.root' % (med,dm,proc)
   fileMonoZ='eos/cms/store/cmst3/group/monojet/mc/model4/MonoZ_%s_%s_%s.root' % (med,dm,proc)
   lFile = ROOT.TFile()
   lFile.Open('root://eoscms//'+fileMonoJ)
   lMonoJ = check(fileMonoJ,med,dm,proc,iClean)
   lMonoW = check(fileMonoW,med,dm,proc,iClean)
   lMonoZ = check(fileMonoZ,med,dm,proc,iClean)
   print "Med",med,"dm",dm,"proc",proc,"MonoJ",lMonoJ,"MonoW",lMonoW,"MonoZ",lMonoZ
   return [lMonoJ[0] and lMonoJ[1], lMonoW[0] and lMonoW[1], lMonoZ[0] and lMonoZ[1]]

def fileExists(filename,label):
   sc=None
   print '%s ls eos/cms/store/cmst3/group/monojet/mc/%s/%s | wc -l' %(eos,label,filename)
   exists = commands.getoutput('%s ls eos/cms/store/cmst3/group/monojet/mc/%s/%s | wc -l' %(eos,label,filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   print exists
   return int(exists) == 1

def localFileExists(filename):
   print 'ls output/%s | wc -l' %(filename) 
   #exists = commands.getoutput('ls ntuples/Output/%s | wc -l' %(filename)  )
   exists = commands.getoutput('ls output/%s | wc -l' %(filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   print exists
   return int(exists) == 1

aparser = argparse.ArgumentParser()
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[300,325,350,400,500,600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[100,125,150,175,200,225,250,275,300,300,325,350,400,500,600,700,800,900,1000,1250,1500,1750,2000])
aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1,5,10,15,20,25,30,35,40,45,50,60,75,80,100,125,150,175,200,225,250,275,300,300,325,350,400,500,600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[75,80,100,125,150,175,200,225,250,275,300,300,325,350,400,500,600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[150,200,300,400,500,600,700,800,900,1000,1250,1500,1750,2000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1000,1250,1500,1750,2000,10000])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1,10,300,325,350,360,370,374])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1])
#aparser.add_argument('-dm' ,'--dmrange'   ,nargs='+',type=int,default=[1])
aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[1,5,10,20,30,40,50,60,70,80,90,100,125,150,175,200,225,250,275,300,325,350,400,500,525,600,725,800,925,1000,1125,1200,1250,1325,1400,1500,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[200])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[2500,3000,3500,4000,5000,6000,7000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[1000,1250,1500,2000,2500,3000,3500,4000,5000,6000,7000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[10,25,50,75,100,125,150,200,250,300,400,500,600,800,1000,1200,1600,2000,3000,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[150,200,300,400,500,600,800,1000,1200,1600,2000,3000,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[10,20,30,40,50,60,70,80,90,100,125,150,200,300,325,400,500,525,600,725,800,925,1000,1125,1200,1325,1400,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[1])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[10,20,30,40,50,60,70,80,90,100,125,150,175,200,300,325,400,525,600,725,800,925,1000,1125,1200,1325,1400,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[50,125,100,150,200,300,325,400,525,600,725,800,925,1000,1125,1200,1325,1400,1525,1600,1725,1800,1925,2000,2500,3000,3500,4000,5000])
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[10,20,50,100,200,300,500,1000,2000,10000]7)
#aparser.add_argument('-med','--medrange'  ,nargs='+',type=int,default=[750])
aparser.add_argument('-w'   ,'--widthrange',nargs='+',type=int,default=[1])#
#aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.005,0.01,0.05,0.07,0.1,0.13,0.15,0.17,0.19,0.21,0.23,0.25,0.27])
#aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.06,0.08,0.09,0.11,0.012,0.14,0.16,0.18,0.20,0.22,0.24,0.26])
#aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.1,0.5,1.0,1.5,2.0,2.5,3.0])
#aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[1.0,5.0,8.0,10.,15.0,20.0,25,30])
#aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.1,0.2,0.3,0.4,0.5,0.6,1.0,2.0])
#aparser.add_argument('-gdm' ,'--gdmrange'  ,nargs='+',type=int,default=[0.1,0.2,0.3,0.4,0.5,0.6,1.0,2.0])
#aparser.add_argument('-gdm' ,'--gdmrange'  ,nargs='+',type=int,default=[0.001,0.005,0.01,0.025,0.5,0.075])
#aparser.add_argument ('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0])
#parser.add_argument ('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.75, 1.25, 1.75, 2.25, 2.75, 6.0, 8.0, 10.0])
aparser.add_argument('-gq'  ,'--gqrange'   ,nargs='+',type=int,default=[0.25,1.0])
aparser.add_argument('-gdm' ,'--gdmrange'  ,nargs='+',type=int,default=[1.0])
aparser.add_argument('-proc','--procrange' ,nargs='+',type=int,default=[800,801,805,806])
#aparser.add_argument('-proc','--procrange' ,nargs='+',type=int,default=[800])
aparser.add_argument('-q'   ,'--q'         ,nargs='+',type=str,default=['2nd'])
aparser.add_argument('-o'   ,'--options'   ,nargs='+',type=str,default=[''])
aparser.add_argument('-m'   ,'--mod'       ,nargs='+',type=int,default=[2])

# Add couplings and mono X when they are ready
args = aparser.parse_args()
label=''
option=''
generate=False
limit=False
reweight=False

if args.options[0].find('--monoV') > 0:
    label='_1'
    option='--monoV'

if args.options[0].find('--hinv') > 0:
    label='_2'
    option='--hinv'

if args.options[0].find('--monoJ') > 0:
    label='_3'
    option='--monoJ'

if args.options[0].find('--monoW') > 0:
    label='_4'
    option='--monoW'

if args.options[0].find('--monoZ') > 0:
    label='_5'
    option='--monoZ'

if args.options[0].find('--bbDM') > 0:
    label='_6'
    option='--bbDM'

if args.options[0].find('--ttDM') > 0:
    label='_7'
    option='--ttDM'

if args.options[0].find('--VBF') > 0:
    label='_8'
    option='--VBF'

if args.options[0].find('--mono1J') > 0:
    label='_9'
    option='--mono1J'

if args.options[0].find('--mono2J') > 0:
    label='_10'
    option='--monoJJ'

if args.options[0].find('--dijet') > 0:
    label='_11'
    option='--dijet'

if args.options[0].find('--dijetzp') > 0:
    label='_12'
    option='--dijetzp'

if args.options[0].find('--monos') > 0:
    label='_13'
    option='--monoS'

if args.options[0].find('--monoggz') > 0:
    label='_14'
    option='--monoGGZ'

if args.options[0].find('--monoJMCFM') > 0:
    label='_15'
    option='--monoJMCFM'

if args.options[0].find('--monoV') > 0 and args.options[0].find('--monoGGZ') > 0 :
    label='_16'
    option='--monoV --monoGGZ'

if args.options[0].find('--generate') > 0:
    label=label+'g'
    generate=True

if args.options[0].find('--reweight') > 0:
    label=label+'r'
    reweight=True

if args.options[0].find('--limit') > 0:
    label=label+'l'
    limit=True

print option,"Submitting by ",args.mod[0]
counter=0
#os.system('rm runlimit*.sh')
for dm in args.dmrange:
    for med in args.medrange:
       #if dm * 2 != med:
       #    continue
        for width in args.widthrange:
           for proc in args.procrange:
              for gq in args.gqrange:
                 for gdm in args.gdmrange:
                    if option == '--hinv' and (proc==800 or proc==801 or proc > 809 or dm != 1):
                       continue
                    if generate or reweight or limit:
                    #width=0.25
                       procstr='V_'
                       if proc == 801:
                          procstr='A_'
                       if proc == 805:
                          procstr='S_'
                       if proc == 806:
                          procstr='P_'
                       #checkFileName='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'.root'
                       checkFileName='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(gdm)+'_'+str(int(proc))+'.root'
                       #checkFileName='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(proc))+'.root'
                       if label.find('_1') > -1:
                          checkFileName='MonoV_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
                       if label.find('_4') > -1:
                          #checkFileName='MonoW_'+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'.root'
                          checkFileName='MonoW_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(proc))+'.root'
                          #checkFileName='MonoW_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_signal.root'
                       if label.find('_5') > -1:
                          checkFileName='MonoZ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(proc))+'.root'
                          #checkFileName='MonoZ_'+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'.root'
                          #checkFileName='MonoZ_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_signal.root'
                       if label.find('_8') > -1:
                          #checkFileName='VBF_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'.root'
                          checkFileName='VBF_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_signal.root'
                          #checkFileName='MonoZ_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_signal.root'
                       if label.find('_11') > -1:
                          #checkFileName='VBF_'+procstr+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'.root'
                          checkFileName='dijet_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
                       if label.find('_12') > -1:
                          checkFileName='dijetzp_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
                       if label.find('_13') > -1:
                          checkFileName='monos_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
                       if label.find('_14') > -1:
                          checkFileName='monoggz_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
                       if label.find('_15') > -1:
                          checkFileName='monoj_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(gdm)+'_'+str(int(proc))+'_mcfm.root'
                       if fileExists(checkFileName,'model3_v2/'):
                          continue
                       #if localFileExists(checkFileName):
                       #   continue
                       if not generate and not limit:
                          #if localFileExists('model_'+str(int(med))+'_'+str(int(dm))+'_'+str(width)+'_'+str(int(proc))+'_0.root'):
                          #if fileExists(checkFileName,'model4/'):
                          #   continue
                          checks=checkDetails(med,dm,proc)
                          if checks[0] and checks[1] and checks[2]: 
                             continue
                       if counter ==  0: 
                          fileName=('jobs/runlimit_%s_%s_%s_%s_%s_%s%s.sh' % (dm,med,width,proc,gq,gdm,label))
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
                          sub_file.write('./generate.py --dm %s --med %s --width %s --proc %s --gq %s --gdm %s %s \n' % (dm,med,width,proc,gq,gdm,option))
                       elif reweight:
                          sub_file.write('cp %s/reweight.py . \n'%os.getcwd())
                          if not checks[0]:
                             sub_file.write('./reweight.py --dm %s --med %s --width %s --proc %s --gq %s --gdm %s \n' % (dm,med,width,proc,gq,gdm))
                          if not checks[1]:
                             sub_file.write('./reweight.py --dm %s --med %s --width %s --proc %s --gq %s --gdm %s --monoW \n' % (dm,med,width,proc,gq,gdm))
                          if not checks[2]:
                             sub_file.write('./reweight.py --dm %s --med %s --width %s --proc %s --gq %s --gdm %s --monoZ \n' % (dm,med,width,proc,gq,gdm))
                       else:
                          sub_file.write('cp %s/limit_z.py . \n'%os.getcwd()) 
                          sub_file.write('rm *.root        \n')
                          sub_file.write('./limit_z.py  --dm %s --med %s --width %s --proc %s %s \n' % (dm,med,width,proc,option))
                          if submit and not reweight:
                             sub_file.write('hadd model_%s_%s_%s_%s_%s.rootX model_*.rootX \n' % (dm,med,width,proc,label))
                             sub_file.write('mv model_%s_%s_%s_%s_%s.rootX %s/Output/ \n' % (dm,med,width,proc,label,basedir))
                       if reweight and submit:
                          name='MonoJ_%s_%s_%s.root' % (int(med),int(dm),int(proc))
                          if not checks[0]:
                             sub_file.write('hadd %s MonoJ_%s_%s_*_%s.root \n' % (name,int(med),int(dm),int(proc)))   
                             sub_file.write('%s rm /store/cmst3/group/monojet/mc/model4/%s \n'         % (eos,name))
                             sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/model4/%s \n'   % (name,name))
                          if not checks[1]:
                             name='MonoW_%s_%s_%s.root' % (int(med),int(dm),int(proc))
                             sub_file.write('hadd %s MonoW_%s_%s_*_%s.root \n' % (name,int(med),int(dm),int(proc)))
                             sub_file.write('%s rm /store/cmst3/group/monojet/mc/model4/%s \n'         % (eos,name))
                             sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/model4/%s \n'   % (name,name))
                          if not checks[2]:
                             name='MonoZ_%s_%s_%s.root' % (int(med),int(dm),int(proc))
                             sub_file.write('hadd %s MonoZ_%s_%s_*_%s.root \n' % (name,int(med),int(dm),int(proc)))
                             sub_file.write('%s rm /store/cmst3/group/monojet/mc/model4/%s \n'         % (eos,name))
                             sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/model4/%s \n'   % (name,name))
                       sub_file.close()
                       counter=counter+1
                       if submit:
                          counter = 0
                          fileName=('jobs/runlimit_%s_%s_%s_%s_%s_%s%s.sh' % (dm,med,width,proc,gq,gdm,label))
                          os.system('chmod +x %s' % os.path.abspath(sub_file.name))
                          os.system('bsub -q %s -o out.%%J %s' % (args.q[0],os.path.abspath(sub_file.name)))
                 
