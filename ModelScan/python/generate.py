#! /usr/bin/env python
import commands,sys,os,subprocess
from optparse import OptionParser

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'

def parser():
   parser = OptionParser()
   parser.add_option('--override',action='store_true',     dest='override',default=False,help='Use Specified Ntuples') # need a few more options for monoV
   parser.add_option('--dm'   ,action='store',type='float',dest='dm'    ,default=10,  help='Dark Matter Mass')
   parser.add_option('--med'  ,action='store',type='float',dest='med'   ,default=2000,help='Mediator Mass')
   parser.add_option('--width',action='store',type='float',dest='width' ,default=1,   help='Width (in Min width units)')
   parser.add_option('--proc' ,action='store',type='float',dest='proc'  ,default=806, help='Process(800=V,801=A,805=S,806=P)')
   parser.add_option('--gq'   ,action='store',type='float',dest='gq'    ,default=1,help='coupling to quarks')
   parser.add_option('--gdm'  ,action='store',type='float',dest='gdm'   ,default=1,   help='coupling to dark matter')
   parser.add_option('--label',action='store',type='string',dest='label',default='model3_v2',help='eos label')
   parser.add_option('--monoV'   ,action='store_true',     dest='monov',default=False,help='Run mono V generation') # need a few more options for monoV
   parser.add_option('--bbDM'    ,action='store_true',     dest='bbdm' ,default=False,help='Run bb+DM generation') # need a few more options for monoV
   parser.add_option('--ttDM'    ,action='store_true',     dest='ttdm' ,default=False,help='Run tt+DM generation') # need a few more options for monoV
   parser.add_option('--writeLHE',action='store_true',     dest='lhe'  ,default=False,help='write LHE as well')
   parser.add_option('--hinv'    ,action='store_true',     dest='hinv' ,default=False,help='Higgs Invisible') # need a few more options for monoV
   parser.add_option('--monoJ'   ,action='store_true',     dest='monoJ'   ,default=False,help='Just Monojet') # need a few more options for monoV
   parser.add_option('--monoJMCFM',action='store_true',    dest='monoJMCFM',default=False,help='Just Monojet MCFM') # need a few more options for monoV
   parser.add_option('--monoJJ'  ,action='store_true',     dest='monoJJ'  ,default=False,help='dijet') # need a few more options for monoV
   parser.add_option('--mono1J'  ,action='store_true',     dest='mono1J'  ,default=False,help='one jet') # need a few more options for monoV
   parser.add_option('--monoS'   ,action='store_true',     dest='monoS'   ,default=False,help='750 jet') # need a few more options for monoV
   parser.add_option('--monoGGZ' ,action='store_true',     dest='monoGGZ' ,default=False,help='ggPhiZ jet') # need a few more options for monoV
   parser.add_option('--monoTop' ,action='store_true',     dest='monoTop' ,default=False,help='top + MET') # need a few more options for monoV
   parser.add_option('--dijet'   ,action='store_true',     dest='dijet'   ,default=False,help='dijet resonance') # need a few more options for monoV
   parser.add_option('--dijetzp' ,action='store_true',     dest='dijetzp' ,default=False,help='dijet resonance') # need a few more options for monoV
   parser.add_option('--mj'      ,action='store',          dest='mj'      ,default='ggH125_signal',help='Monojet Base') # need a few more options for monoV
   parser.add_option('--zh'      ,action='store',          dest='zh'      ,default='ZH125_signal',help='ZH Base') # need a few more options for monoV
   parser.add_option('--wh'      ,action='store',          dest='wh'      ,default='WH125_signal',help='WH Base') # need a few more options for monoV
   (options,args) = parser.parse_args()
   return options

def generateMonoJet(mass,med,width,process,gq,gdm,onejet,lhe=False):
   os.system('rm -rf POWHEG-BOX-V2')
   os.system('cmsStage /store/cmst3/user/pharris/gen/POWHEG-BOX-V2_gen2.tar.gz .')
   os.system('tar xzvf POWHEG-BOX-V2_gen2.tar.gz')
   #dty='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_4_12_patch1/src/MonoX/ModelScan/python'
   print './run.py --med %d --dm %d --proc %d --gsm %f --gdm %f' % (med,mass,process,gq,gdm)
   sub_file = open('runpowheg.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('scramv1 project CMSSW CMSSW_7_1_19 \n')
   sub_file.write('cd CMSSW_7_1_19/src \n')
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   pwg=''
   if process > 799 and process < 805:
      pwg='POWHEG-BOX-V2/DMV'
      sub_file.write('cd POWHEG-BOX-V2/DMV\n')
   if process > 804 and process < 808: 
      pwg='POWHEG-BOX-V2/DMS_tloop'
      sub_file.write('cd POWHEG-BOX-V2/DMS_tloop\n')
   sub_file.write('./run.py --med %d --dm %d --proc %d --gsm %f --gdm %f \n' %  (med,mass,process,gq,gdm))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))
   if not onejet:
      os.system('sed "s@1000021@1000022@g"  %s/pwgevents.lhe > test.lhe1' % pwg)
      os.system('sed "s@-1000022@1000022@g" test.lhe1        > test.lhe')
   else :
      os.system('sed "s@1000021@16@g"       %s/pwgevents.lhe > test.lhe' % pwg)
   xs=getPowhegXS(process)
   head = commands.getstatusoutput('cat   test.lhe | grep -in "<init>" | sed "s@:@ @g" | awk \'{print $1+1}\' | tail -1')[1]
   tail = commands.getstatusoutput('wc -l test.lhe | awk -v tmp="%s" \'{print $1-2-tmp}\' ' % head)[1]
   os.system("tail -%s test.lhe                           >  test.lhe_tail" % tail)
   os.system("head -%s test.lhe                           >  test.lhe_F" % head)
   os.system('echo "  %s   %s  1.00000000000E-00 100" >>  test.lhe_F' % (xs[0],xs[1]))
   os.system('echo "</init>"                                           >>  test.lhe_F')
   os.system("cat test.lhe_tail                                        >>  test.lhe_F")
   os.system("mv test.lhe_F test.lhe")
   
   #os.system('rm -r POWHEG-BOX-V2')
   if lhe:
      os.system('cmsStage test.lhe /store/cmst3/group/monojet/mc/lhe/DM_%s_%s_%s_%s_%s_%s.lhe'%(med,mass,width,process,gq,gdm))
   return

def generateMonoJetMCFM(mass,med,width,process,gq,gdm,lhe):
   os.system('rm -rf Bin')
   os.system('cmsStage /store/cmst3/user/pharris/gen/MCFM-6.8_v6_Bin.tgz  .')
   os.system('tar xzvf MCFM-6.8_v6_Bin.tgz')
   os.chdir('Bin')
   print './run.sh %d %d %d %d %d %d' % (med,mass,width,process,gq,gdm)
   print process
   if process > 799 and process < 810:
      os.system('./run.sh %d %d %d %d %d %d 13000' % (med,mass,width,process,gq,gdm))
   os.chdir('..')
   os.system('sed "s@-1000022@1000022@g" Bin/DM.lhe > test.lhe')
   os.system('rm -r Bin/')
   return

def basicFileExists(filename,label):
   #cmsStage %s /store/cmst3/group/monojet/mc/%s/%s' %(filename,label,filename)
   sc=None
   print '%s ls %s/%s | wc -l' %(eos,label,filename)
   exists = commands.getoutput('%s ls %s/%s | wc -l' %(eos,label,filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   print exists
   return int(exists) == 1

def generateMonoJetMadgraph(mass,med,width,process,gq,gdm,lhe):
   name='DMSpin0_ggPhi12j_g1_%s_%s_%s_tarball.tar.xz' % (med,mass,process)
   if not basicfileExists(name,'eos/cms/store/cmst3/user/pharris/gen_mg_012j'):
      return
   os.system('cmsStage /store/cmst3/user/pharris/gen_mg_012j/%s' % name)
   os.system('unxz %s' % name)
   os.system('tar xvf %s' % name.replace('.xz','') )
   print './run.sh %d %d %d %d %d %d' % (med,mass,width,process,gq,gdm)
   os.system('./runcmsgrid 500 $RANDOM 1')
   os.system('sed "s@99000032@32@g;s@91000012@18@g" cmsgrid.lhe > test.lhe')
   return

def generateMonoS(mass,med,width,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMG13_750.sh .')
   os.system('chmod +x runMG13_750.sh')
   os.system('./runMG13_750.sh %d %d %f %d %d %f ' % (med,mass,gq,805,10,gdm))

def generateMonoGGZ(mass,med,width,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMG13_MonoZ.sh .')
   os.system('chmod +x runMG13_MonoZ.sh')
   os.system('./runMG13_MonoZ.sh %d %d %f %d %d %f ' % (med,mass,gq,process,1,gdm))

def generateMonoTop(mass,med,width,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMG13_MonoTop.sh .')
   os.system('chmod +x runMG13_MonoTop.sh')
   os.system('./runMG13_MonoTop.sh %d %d %f %d %d %f ' % (med,mass,gq,process,1,gdm))

def generateDiJetMG(mass,med,width,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMGJJ.sh .')
   os.system('chmod +x runMGJJ.sh')
   if process == 800 : 
      os.system('./runMGJJ.sh %d %d %f %s %d %f ' % (med,mass,gq,'V',1,gdm))
   if process == 801 : 
      os.system('./runMGJJ.sh %d %d %f %s %d %f ' % (med,mass,gq,'A',1,gdm))

def generateDiJetMGZP(mass,med,width,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMGJ.sh .')
   os.system('chmod +x runMGJ.sh')
   if process == 800 : 
      os.system('./runMGJ.sh %d %d %f %s %d %f ' % (med,mass,gq,'V',1,gdm))
   if process == 801 : 
      os.system('./runMGJ.sh %d %d %f %s %d %f ' % (med,mass,gq,'A',1,gdm))

def getVBFnloXS(process):
   xs=[-1,-1]
   xs[0] = commands.getstatusoutput("cat brckkw.out | grep Total | awk '{print $11}'  "% pwg)[1]
   return xs

def getPowhegXS(process):
   xs=[-1,-1]
   pwg='POWHEG-BOX-V2/DMV'
   if process > 804 and process < 808:
      pwg='POWHEG-BOX-V2/DMS_tloop'
   xs[0] = commands.getstatusoutput("cat %s/pwg-stat.dat | grep Total | awk '{print $4}' "% pwg)[1]
   xs[1] = commands.getstatusoutput("cat %s/pwg-stat.dat | grep Total | awk '{print $6}' "% pwg)[1]
   print xs
   return xs

def generateMonoV_AV(mass,width,med,process,gq,gdm):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMG13.sh .' )
   os.system('chmod +x runMG13.sh')
   Xgq='1.0'
   Xgdm='1.0'
   if gq  == 0.25:
      Xgq = '0.25'
   if gdm != 1.0:
      Xgdm = str(gdm)
   if process == 800 : 
      print '    ./runMG13.sh %d %d %s %s %s %s ' % (med,mass,Xgq,'V','1',Xgdm)
      os.system('./runMG13.sh %d %d %s %s %s %s ' % (med,mass,Xgq,'V','1',Xgdm))
   if process == 801 : 
      print '    ./runMG13.sh %d %d %s %s %s %s ' % (med,mass,Xgq,'A','1',Xgdm)
      os.system('./runMG13.sh %d %d %s %s %s %s ' % (med,mass,Xgq,'A','1',Xgdm))


def generateHFDM(mass,width,med,process,gq,gdm,finalstate):
   os.system('cp -r  /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/runMG13_scalar.sh .' )
   os.system('chmod +x runMG13_scalar.sh')
   os.system('./runMG13_scalar.sh %d %d %d %d %d ' % (med,mass,gq,process,finalstate))
   
def generateMonoV_VH(mass,width,med,process,gq,gdm,label,filename,dty="/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_19/src/BaconAnalyzer/GenSelection/prod/"):
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
   sub_file.write('cd CMSSW_7_1_19/src \n')
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   sub_file.write('cmsRun VHProd.py > out \n')
   sub_file.write('cmsRun makingBacon_LHE_Gen_v1.py \n')
   #sub_file.write('cp -r %s/../bin/files . \n' % dty)
   sub_file.write('xs=`cat out  | grep subprocess | sed "s@D@E@g"  | awk \'{print $10*1000000000*1.9}\'` \n')
   sub_file.write('runMV  %s $xs 1 2 \n' % filename)
   sub_file.write('mv Output.root %s \n' % filename)
   sub_file.write('cmsRm       /store/cmst3/group/monojet/mc/%s/%s \n' %(label,filename))
   sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/%s/%s \n' %(filename,label,filename))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))

def generateMonoVAH(mass,width,med,process,gq,gdm,label,filename,dty="/afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter"):
   os.system('cp %s/runJHU13.sh             .'%dty)
   os.system('./runJHU13.sh  %s %s %s        '% ( med, str(int(process)),filename))
   os.system('%s rm       /store/cmst3/group/monojet/mc/%s/%s ' %(eos,label,filename))
   os.system('cmsStage %s /store/cmst3/group/monojet/mc/%s/%s ' %(filename,label,filename))

def generateGen(xs,filename,label,monoV,dty="/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_4_12_patch1/src/BaconAnalyzer/GenSelection/prod/"):
   os.system('cp %s/makingBacon_LHE_Gen.py .'%dty)
   cmscfg="LHEProd.py"
   if filename.find('MG') > -1:
      cmscfg='LHEProd_MLM.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff_MLM.py .'%dty)   
   elif filename.find("MonoJJ") > -1 and not filename.find("807") > -1 and not filename.find("808") > -1:
      cmscfg='LHEProd_2parton.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff_2parton.py .'%dty)   
   elif filename.find("Mono1J") > -1:
      cmscfg='LHEProd_1parton.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff_1parton.py .'%dty)   
   elif filename.find("MonoS") > -1:
      cmscfg='LHEProd_MLM2.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff_MLM2.py .'%dty)   
   elif filename.find("zprime") > -1:
      cmscfg='LHEProd_MLM4.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff_MLM4.py .'%dty)   
   else:
      cmscfg='LHEProd.py'
      os.system('cp %s/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py .'%dty)   
   os.system('cp %s/%s .' % (dty,cmscfg))
   
   with open("makingBacon_LHE_Gen_v1.py", "wt") as fout:
    with open("makingBacon_LHE_Gen.py", "rt") as fin:
       for line in fin:
          fout.write(line.replace('!BBB', filename))
   sub_file = open('runpythia.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('scramv1 project CMSSW CMSSW_7_1_19 \n')
   sub_file.write('cd CMSSW_7_1_19/src \n')
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   sub_file.write('cmsRun %s > /dev/null \n' % cmscfg)
   sub_file.write('cd %s \n'%dty)
   sub_file.write('eval `scramv1 runtime -sh`\n')
   sub_file.write('cd %s \n' % os.getcwd())
   sub_file.write('cmsRun makingBacon_LHE_Gen_v1.py \n')
   #sub_file.write('cp -r %s/../bin/files . \n' % dty)
   sub_file.write('runGen  -1 %s %s 0 \n' % (filename,xs))
   sub_file.write('mv Output.root %s \n' % filename)
   sub_file.write('%s rm       /store/cmst3/group/monojet/mc/%s/%s \n' %(eos,label,filename))
   sub_file.write('cmsStage %s /store/cmst3/group/monojet/mc/%s/%s \n' %(filename,label,filename))
   if filename.find("dijet") > -1:
      sub_file.write('cmsStage minlo_tau_8TeV.root /store/cmst3/group/monojet/mc/%s/gen/%s \n' %(label,filename))
   #sub_file.write('cmsRm       /store/cmst3/user/pharris/mc/%s/%s \n' %(label,filename))
   #sub_file.write('cmsStage %s /store/cmst3/user/pharris/mc/%s/%s \n' %(filename,label,filename))
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))

def getWidthXS(mass,med,width,process,gq,gdm,iYuk=True):
   xs=[-1,-1]
   yuk=0
   if iYuk:
      yuk=1
   os.system('cp -r /afs/cern.ch/user/p/pharris/pharris/public/bacon/Darkmatter/MCFM-6.8_v2/Bin .')
   os.chdir('Bin')
   if process > 799 and process < 810:
      os.system('./run.sh %s %s %s %s %s %s %s > Xout'  % (med,mass,width,process,gq,gdm,yuk))
   if process > 809 and process < 820:
      process2=process-10
      os.system('./runZ0.sh  %s %s %s %s %s %s %s > Xout' % (med,mass,width,process2,gq,gdm,yuk))
   if process > 819 and process < 830:
      process2=process-20
      os.system('./runZM1.sh %s %s %s %s %s %s %s > Xout' % (med,mass,width,process2,gq,gdm,yuk))
   if process > 830 and process < 840:
      process2=process-30
      os.system('./run.sh    %s %s %s %s %s %s 1 > Xout' % (med,mass,width,process2,gq,gdm))

   xs[0] = commands.getstatusoutput("cat Xout  | grep Value | awk '{print $7}'")
   xs[1] = commands.getstatusoutput("cat Xout  | grep Width | awk '{print $3}'"                                  )
   os.chdir('..')
   xs[0] = xs[0][1]
   xs[1] = xs[1][1]
   os.system('rm -r Bin/')
   print "xs Gamma :",xs[0],xs[1],"Yukawa",yuk
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
   
def loadmonojet(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   #filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'_8TeV.root'
   filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'.root'
   #filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'_MG.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      #generateMonoJetMadgraph(dm,med,width,proc,gq,gdm,lhe)
      generateMonoJet(dm,med,width,proc,gq,gdm,lhe)
      #generateGen(1.,filename,label,False)
      xs=getPowhegXS(proc)
      generateGen(xs[0],filename,label,False)

def loadmonojetMCFM(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'_mcfm.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoJetMCFM(dm,med,width,proc,gq,gdm,lhe)
      generateGen(1.,filename,label,False)

def loadonejet(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='Mono1J_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoJet(dm,med,width,proc,gq,gdm,True)
      generateGen(-1,filename,label,False)

def loadmonos(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='MonoS_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'_v4.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoS(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)

def loadmonoggz(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='MonoGGZ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoGGZ(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)

def loadmonotop(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='MonoTop_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+"_"+str(gdm)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateMonoTop(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)

def loaddijet(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   #filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'_8TeV.root'
   filename='MonoJJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateDiJet(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)

def loaddijetRes(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   #filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'_8TeV.root'
   filename='dijet_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateDiJetMG(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)

#3 2j 180
#4 2j 500
#5 3j 500
def loaddijetZP(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   #filename='MonoJ_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'_8TeV.root'
   filename='dijet_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'_zprime5.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateDiJetMGZP(dm,med,width,proc,gq,gdm)
      generateGen(-1,filename,label,False)
  
def loadmonov(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='MonoV_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
   print "!!!!! filename",filename
   if proc == 805 or proc == 806:
      filename='MonoV_'+str(int(med))+'_'+str(int(dm))+'_'+str(gq)+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      if proc == 800 or proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821 : 
         generateMonoV_AV(dm,width,med,proc,gq,gdm)
         generateGen(-1,filename,'model3',True)
      else :
         #generateMonoV_VH(dm,width,med,proc,gq,gdm,label,filename)
         generateMonoVAH(dm,width,med,proc,gq,gdm,'model3',filename)
         
def loadttDM(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='ttDM_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateHFDM(dm,width,med,proc,gq,gdm,1)
      generateGen(-1,filename,label,True)

def loadbbDM(dm,med,width=1,proc=805,gq=1,gdm=1,label='model3',lhe=False):
   filename='bbDM_'+str(int(med))+'_'+str(int(dm))+'_'+str(int(width))+'_'+str(int(proc))+'.root'
   if fileExists(filename,label):
      os.system('cmsStage /store/cmst3/group/monojet/mc/%s/%s .' %(label,filename))
   else:
      generateHFDM(dm,width,med,proc,gq,gdm,0)
      generateGen(-1,filename,label,True)
            
if __name__ == "__main__":
    options = parser()
    print options.dm,options.med,options.width,options.proc
    if options.ttdm :
       loadttDM(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.bbdm :
       loadbbDM(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.dijet :
       loaddijetRes(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.dijetzp :
       loaddijetZP(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.monoJJ:
       loaddijet(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.monoJMCFM:
       loadmonojetMCFM(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.mono1J:
       loadonejet(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.monoS:
       loadmonos(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.monoGGZ:
       loadmonoggz(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if options.monoTop:
       loadmonotop(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
       exit()

    if not options.monov : 
       loadmonojet(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label,options.lhe)
    else : 
       loadmonov(options.dm,options.med,options.width,options.proc,options.gq,options.gdm,options.label+'M',options.lhe)
