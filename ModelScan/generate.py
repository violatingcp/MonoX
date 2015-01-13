#! /usr/bin/env python
import commands,sys,os,subprocess
from optparse import OptionParser

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'

parser = OptionParser()
parser.add_option('--dm'   ,action='store',type='float',dest='dm'    ,default=10,  help='Dark Matter Mass')
parser.add_option('--med'  ,action='store',type='float',dest='med'   ,default=2000,help='Mediator Mass')
parser.add_option('--width',action='store',type='float',dest='width' ,default=1,   help='Width (in Min width units)')
parser.add_option('--proc' ,action='store',type='float',dest='proc'  ,default=806, help='Process(800=V,801=A,805=S,806=P)')
parser.add_option('--gq'   ,action='store',type='float',dest='gq'    ,default=1,   help='coupling to quarks')
parser.add_option('--gdm'  ,action='store',type='float',dest='gdm'   ,default=1,   help='coupling to dark matter')
parser.add_option('--label',action='store',type='string',dest='label',default='model',help='eos label')
#parser.add_option('-MCFMGen' ,action='store',type='string',dest='mcfmg'   ,help='Location of MCFM Generation')
#parser.add_option('-MCFMRaw' ,action='store',type='string',dest='mcfmr'   ,help='Location of MCFM un constrained gen')
#parser.add_option('-eos'     ,action='store',type='string',dest='eos'     ,help='eos directory to store the samples in')
parser.add_option('--monoV'   ,action='store_true',     dest='monov',default=False,help='Run mono V generation') # need a few more options for monoV
parser.add_option('--writeLHE',action='store_true',     dest='lhe'  ,default=False,help='write LHE as well')
parser.add_option('--hinv'    ,action='store_true',     dest='hinv' ,default=False,help='Higgs Invisible') # need a few more options for monoV
parser.add_option('--monoJ'   ,action='store_true',     dest='monoJ',default=False,help='Just Monojet') # need a few more options for monoV
(options,args) = parser.parse_args()

def generateMonoJet(mass,med,width,process,gq,gdm,lhe):
   os.system('cp -r /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/MCFM-6.8/Bin .')
   os.chdir('Bin')
   print './run.sh %d %d %d %d %d %d' % (med,mass,width,process,gq,gdm)
   print process
   if process > 799 and process < 810:
      os.system('./run.sh %d %d %d %d %d %d' % (med,mass,width,process,gq,gdm))
   if process > 809 and process < 820:
      process2=process-10
      os.system('./runZ0.sh %d %d %d %d %d %d' % (med,mass,width,process2,gq,gdm))
   if process > 819 and process < 830:
      process2=process-20
      os.system('./runZM1.sh %d %d %d %d %d %d' % (med,mass,width,process2,gq,gdm))
   os.chdir('..')
   os.system('sed "s@-1000022@1000022@g" Bin/DM.lhe > test.lhe')
   os.system('rm -r Bin/')
   if lhe:
      os.system('cmsStage test.lhe /store/cmst3/group/monojet/mc/lhe/DM_%s_%s_%s_%s_%s_%s.lhe'%(med,mass,width,process,gq,gdm))
   return

def generateMonoV_AV(mass,width,med,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/Kristian/runZP.sh .' )
   os.system('chmod +x runZP.sh')
   if process == 800 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'V',1))
   if process == 801 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'A',1))
   if process == 810 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'V',0))
   if process == 811 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'A',0))
   if process == 820 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'V',-1))
   if process == 821 : 
      os.system('./runZP.sh %d %d %d %s %d ' % (med,mass,gq,'A',-1))
   #os.system('cp Events/run_01/unweighted_events.lhe.gz .' )
   #os.system('gunzip unweighted_events.lhe.gz ' )
   #os.system('mv unweighted_events.lhe DM.lhe' )

def generateMonoV_VH(mass,width,med,process,gq,gdm,label,filename,dty="/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_19/src/BaconAnalyzer/BaconGenAnalyzer/prod/"):
   os.system('cp %s/VHProd.py      .'%dty)
   os.system('cp %s/HIG-Summer12-02280-fragment_template.py      .'%dty)
   os.system('cp %s/makingBacon_LHE_Gen.py .'%dty)
   os.system('sed "s@MASS@%s@g" HIG-Summer12-02280-fragment_template.py > HIG-Summer12-02280-fragment.py ' % med)
   with open("makingBacon_LHE_Gen_v1.py", "wt") as fout:
    with open("makingBacon_LHE_Gen.py", "rt") as fin:
       for line in fin:
          fout.write(line.replace('!BBB', filename))
   #!!Currently we ignore DM Mass and width couplings just used for cross section
   sub_file = open('runpythia.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('cd %s \n'%dty)
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   sub_file.write('cmsRun VHProd.py > out \n')
   sub_file.write('cmsRun makingBacon_LHE_Gen_v1.py \n')
   sub_file.write('cp -r %s/../bin/files . \n' % dty)
   sub_file.write('xs=`cat out  | grep subprocess | sed "s@D@E@g"  | awk \'{print $10*1000000000*1.9}\'` \n')
   sub_file.write('runMV  %s $xs 1 2 \n' % filename)
   sub_file.write('mv Output.root %s \n' % filename)
   sub_file.write('cmsRm       /store/cmst3/group/monojet/mc/%s/%s \n' %(label,filename))
   sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/%s/%s \n' %(filename,label,filename))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))


def generateGen(xs,filename,label,monoV,dty="/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_19/src/BaconAnalyzer/BaconGenAnalyzer/prod/"):
   os.system('cp %s/LHEProd.py             .'%dty)
   os.system('cp %s/makingBacon_LHE_Gen.py .'%dty)
   os.system('cp %s/Hadronizer_MgmMatchTune4C_8TeV_madgraph_pythia8_cff.py .'%dty)
   #f = open('makingBacon_LHE_Gen.py')
   with open("makingBacon_LHE_Gen_v1.py", "wt") as fout:
    with open("makingBacon_LHE_Gen.py", "rt") as fin:
       for line in fin:
          fout.write(line.replace('!BBB', filename))
   sub_file = open('runpythia.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('cd %s \n'%dty)
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   sub_file.write('cmsRun LHEProd.py \n')
   sub_file.write('cmsRun makingBacon_LHE_Gen_v1.py \n')
   sub_file.write('cp -r %s/../bin/files . \n' % dty)
   if monoV:
      sub_file.write('runMV  %s 1 %s 0 \n' % (filename,xs))
   else:
      sub_file.write('runMJ  %s 1 %s 0 \n' % (filename,xs))
   sub_file.write('mv Output.root %s \n' % filename)
   sub_file.write('cmsRm       /store/cmst3/group/monojet/mc/%s/%s \n' %(label,filename))
   sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/%s/%s \n' %(filename,label,filename))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))

def getWidthXS(mass,med,width,process,gq,gdm):
   xs=[-1,-1]
   os.system('cp -r /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/MCFM-6.8_v2/Bin .')
   os.chdir('Bin')
   if process > 799 and process < 810:
      os.system('./run.sh %s %s %s %s %s %s > Xout'  % (med,mass,width,process,gq,gdm))
   if process > 809 and process < 820:
      process2=process-10
      os.system('./runZ0.sh %s %s %s %s %s %s > Xout' % (med,mass,width,process2,gq,gdm))
   if process > 819 and process < 830:
      process2=process-20
      os.system('./runZM1.sh %s %s %s %s %s %s > Xout' % (med,mass,width,process2,gq,gdm))

   xs[0] = commands.getstatusoutput("cat Xout  | grep Value | awk '{print $7}'")
   xs[1] = commands.getstatusoutput("cat Xout | grep Width | awk '{print $3}'"                                  )
   os.chdir('..')
   xs[0] = xs[0][1]
   xs[1] = xs[1][1]
   os.system('rm -r Bin/')
   print "xs Gamma :",xs[0],xs[1]
   return xs

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
   
def loadmonojet(dm,med,width=1,proc=805,gq=1,gdm=1,label='model',lhe=False):
   filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoJet(dm,med,width,proc,gq,gdm,lhe)
      xs=getWidthXS(dm,med,width,proc,gq,gdm)
      #xs=[1,1]
      generateGen(xs[0],filename,label,False)

def loadmonov(dm,med,width=1,proc=805,gq=1,gdm=1,label='model',lhe=False):
   filename='MonoV_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      if proc == 800 or proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821 : 
         generateMonoV_AV(dm,width,med,proc,gq,gdm)
         generateGen(-1,filename,label,True)
      else :
         generateMonoV_VH(dm,width,med,proc,gq,gdm,label,filename)

if __name__ == "__main__":
    print options.dm,options.med,options.width,options.proc
    if not options.monov : 
       loadmonojet(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
    else : 
       loadmonov(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
