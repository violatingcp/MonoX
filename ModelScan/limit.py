#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array import array
from BaconAna.Utils.generate import *

#basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_22_patch1/src/BaconAna/Utils/python/data/'
basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_5_3_22_patch1/src/BaconAna/Utils/python/ntuples'
mjcut='(met > 0 && (jdphi < 1.8 || jpt_2 < 30) && abs(jeta_1) < 2.0 )'
monojet='19.7*mcweight*(jpt_1 > 150 && met > -200)*'+mjcut
boosted='19.7*mcweight*(fjmtrim > 60 && fjmtrim < 112 && fjt2t1 < 0.5 && fjpt > 250 && met > -250)*'+mjcut
resolved='19.7*mcweight*(60 < mjj && mjj < 112 && ptjj > 160 && dm_pt > 250 && !(fjmtrim > 60 && fjmtrim < 112 && fjt2t1 < 0.5 && fjpt > 250) && jpt_1 > 30 && jpt_2 > 30)'
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
parser.add_option('--hinv'    ,action='store_true',     dest='hinv' ,default=False,help='Higgs Invisible') # need a few more options for monoV
parser.add_option('--monoJ'   ,action='store_true',     dest='monoJ',default=False,help='Just Monojet') # need a few more options for monoV

(options,args) = parser.parse_args()

#generates if need be and computes gen histogram, pulls gen histo out of datacard and adds modified & builds data card 
def makeHist(filename,var,baseweight,treename,label,normalize=False):
   x = array( 'd' )
   #for i0 in range(0,25):
   #   x.append(100+i0*5+2.*i0*i0)
      #x.append(100+i0*15)
   y=[100.0,200.0,210.0,220.0,230.0,240.0,250.0 , 260.0 , 270.0 , 280.0 , 290.0 , 300.0 , 310.0 , 320.0 , 330.0,340,360,380,420,710,1200,1500]
   for i0  in range(0,len(y)):
      x.append(y[i0])
 
   lFile = ROOT.TFile(filename)
   lHist = ROOT.TH1F(label,label,len(x)-1,x)
   lTree = lFile.Get(treename)
   lTree.Draw(var+'>>'+label,baseweight)
   lHist.SetDirectory(0)
   if normalize:
      lHist.Scale(1./lTree.GetEntriesFast())
   return lHist

def ntuplexs(filename,treename):
   lFile = ROOT.TFile(filename)
   lTree = lFile.Get(treename)
   lTree.GetEntry(0)
   return lTree.mcweight

def fixNorm(filename,treename,cut):
   lFile = ROOT.TFile(filename)
   lTree = lFile.Get(treename)
   scale=float(lTree.GetEntriesFast())/float(lTree.GetEntries(cut))
   return scale

def reweight(label,DM,Med,Width,gq,gdm,process,basentuple,basename,basecut,iOutputName,monoV=False,iBR=1):
   xs = [1,1]
   scale = 1
   if not monoV:
      loadmonojet(DM,Med,Width,process,gq,gdm)
      #xs=getWidthXS(DM,Med,Width,process,gq,gdm)
      scale=ntuplexs(('MonoJ_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'Events')
      print "scale:",float(xs[0])/float(scale)
      h1=makeHist(('MonoJ_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'dm_pt',basecut,'Events','model',True)
      if process != 805 and process != 806:
         h2=makeHist('%s/%s' % (basedir, basentuple) ,'dm_pt',basecut,basename,'base',True)           
      else: #apply higgs pt weight
         h2=makeHist('%s/%s' % (basedir, basentuple) ,'dm_pt',basecut,basename,'base',True)           
      h1.Scale(iBR/1000.)
   else:
      loadmonov(DM,Med,Width,process,gq,gdm)
      #xs=ntuplexs('MonoV_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process))),'Events')
      xs=1
      #Add yukawa coupling by computing BR to inv vs B-quark
      if process == 806 or process == 805:
         xs=xs*iBR
         xs=xs*1.25*1.1 # k-factor to NNLO + Corr factor
      if process == 800 or process == 801 or process == 810 or process == 811 or process == 820 or process == 821:
         if basecut.find('23') > 0:
            xs=xs*3*1.43
         else:
            xs=xs*3*1.48

      h1=makeHist(('MonoV_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'dm_pt',basecut,'Events','model',True)
      h2=makeHist('%s/%s' % (basedir, basentuple),'dm_pt',basecut+"*ptw",basename,'base',True)           
      h1.Scale(xs)
      print "Scaling :",xs
      #h2.Scale(xs)
      #print "Hist Int ",h1.Integral()," W Hist ",h2.Integral()
      #h2.Scale(xs)
      #h1=makeHist(('MonoV_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'dmpt',basecut,'Events','model',True)
      #h2=makeHist('%s/MonoVBase.root' % basedir,'dmpt',basecut,treename,'base')           
      
   h1.Divide(h2)
   h1.Fit('pol3',"","R",250,1000)
   h1.Draw()
   lOFile = ROOT.TFile(iOutputName,'RECREATE')
   h1.Write()
   lOFile.Close()
   return xs

def reweightNtuple(iFile,iTreeName,iHistName,iKevin=False,histlabel='model'):
   if iFile.find('combo'):
      iKevin=True
   lHFile = ROOT.TFile('%s' % (iHistName))
   h1     = lHFile.Get(histlabel)
   lFile  = ROOT.TFile('%s/%s' % (basedir, iFile) )
   lTree  = lFile.Get(iTreeName)
   lOFile = ROOT.TFile('RWTree%s' % (iHistName),'UPDATE')
   lOTree = lTree.CloneTree(0)
   w2 = numpy.zeros(1, dtype=float)
   lOTree.Branch("w2",w2,"w2/D")
   for i0 in range(lTree.GetEntriesFast()):
      lTree.GetEntry(i0)
      if not iKevin:
         jet1pt = lTree.dmpt_#lTree.jet1pt_
      else :
         jet1pt = lTree.dmpt
      w2[0] = 1
#      w2[0] = h1.GetFunction('pol3').Eval(jet1pt)
#      if jet1pt > 700:
#         w2[0]=h1.GetFunction('pol3').Eval(700)
      if jet1pt < 1500:
         w2[0]=h1.GetBinContent(h1.FindBin(jet1pt))
      lOTree.Fill()
   lOTree.Write()
   lOFile.Close()
   #return makeHist('BaseOut.root','jpt','(mvamet > 200)',treename,'baseout').Integral()
   return 

def makeDataCardVBF(card,med,proc,iBR,label='signal_vbf',xs='VBFXS.root'):
   lFile  = ROOT.TFile('%s/%s' % (basedir,xs))
   lXS    = lFile.Get('xs')
   lXS125 = lXS.Eval(125)
   lXSMed = lXS.Eval(med)
   lScale = lXSMed/lXS125*iBR
   if proc != 805 and proc != 806:
      lScale = 1e-10
   if med > 1000:
      lScale = 1e-10
   print "VBF Scale :",lScale
   lFile  = ROOT.TFile('%s/%s' % (basedir,card))
   lH1    = lFile.Get(label)
   lOFile  = ROOT.TFile('%s' % card,'UPDATE')
   lOH1   = lH1.Clone()   
   lOH1.Scale(lScale)
   lOH1.Write()
   lOFile.Close()

def makeDataCard(card,newntuple='BaseOut.root',treename='GGH0',label='GGH'):
   #import os.path
   #if not os.path.isfile('tmp/%s' % card): 
   #   os.system('mkdir tmp')
   #   os.system('cp %s/%s tmp/%s' % (basedir,card,card))

   print "Reweighting:",card,label,"Ntuple :",newntuple,treename
   lFile  = ROOT.TFile('%s/%s' % (basedir,card))
   lH1    = lFile.Get(label)
   lH0    = lFile.Get(label+'_MetUp')
   lH2    = lFile.Get(label+'_MetDown')
   lH1.SetDirectory(0)
   if lH0 : 
      lH0.SetDirectory(0)
      lH2.SetDirectory(0)
   
   iKevin=False
   if newntuple.find('combo'):
      iKevin=True
   lTFile = ROOT.TFile(newntuple)
   lTree  = lTFile.Get(treename)
   lWHist = lH1.Clone('Weight')
   lFHist = lH1.Clone('Flat')
   for i0 in range(1,lH1.GetNbinsX()+1) : 
      lWHist.SetBinContent(i0,0)
      lFHist.SetBinContent(i0,0)
   if not iKevin:
      lTree.Draw('mvamet_>>Weight','w2*weight')
      lTree.Draw('mvamet_>>Flat','weight')
   else:
      lTree.Draw('mvamet>>Weight','w2*weight')
      lTree.Draw('mvamet>>Flat','weight')
   lWHist.Divide(lFHist)
   print "Card :",card
   lOFile  = ROOT.TFile('%s' % card,'UPDATE')
   lOH1   = lH1.Clone()
   print lOH1.Integral(),'!!!!!!!-1'
   lOH1.Multiply(lWHist)
   print lOH1.Integral(),'!!!!!!!-2'
   lOH1.Write()
   #for hist in lFile.GetListOfKeys():
   #   print "Writing :",hist.ReadObj().GetName()
   #   if hist.ReadObj().GetName() != lH1.GetName():
   #      hist.ReadObj().Write()
   if lH0 :
      lOH0   = lH0.Clone()
      lOH2   = lH2.Clone()
      lOH0.Multiply(lWHist)
      lOH2.Multiply(lWHist)
      lOH0.Write()
      lOH2.Write()
   os.system('cp %s tmp' % card)
   lOFile.Close()

def runlimitFile(card='card.txt',limitdty='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/'):
   sub_file = open('runlimit.sh','w')
   sub_file.write('#!/bin/bash\n')
   sub_file.write('cd %s \n'% basedir)
   sub_file.write('eval `scramv1 runtime -sh` \n')
   sub_file.write('cd - \n')
   sub_file.write('cp  %s/Cards/%s . \n' % (basedir,card))
   sub_file.write('cp  %s/mono-x-vtagged.root . \n'            % (basedir))
   sub_file.write('cp  %s/photon_dimuon_combined_model.root      . \n'            % (basedir))
   #sub_file.write('cp  %s/photon_dimuon_combined_model.root_vFix . \n'            % (basedir))
   sub_file.write('combine -M  Asymptotic -C 0.9 -t -1 %s \n'  % card)
   sub_file.close()
   os.system('chmod +x %s' % os.path.abspath(sub_file.name))
   os.system('%s' % os.path.abspath(sub_file.name))
   
def makeNtuple(iId,scale,label,DM,Med,Width,process,xst,gq=1,gdm=1,BR=1):
   #if xst[0] == 0:
   #   xst=getWidthXS(DM,Med,Width,process,gq,gdm)
   bestobs=-1
   lTFile = ROOT.TFile('higgsCombineTest.Asymptotic.mH120.root')
   lTree  = lTFile.Get('limit')
   lTree.GetEntry(2)
   bestexp=lTree.limit*scale
   xs=ntuplexs(('MonoJ_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'Events')
   xsW=-1#ntuplexs(('MonoV_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'Events')
   truewidth=BR#xst[1]
   #Should probably write this in python
   os.system('cp %s/Code/fillTree.C .'%basedir)
   os.system('root -b -q fillTree.C\(%s\,%s\,%s\,%s\,%s\,%s\,%s\,%s\,%s\,%s\,%s\,%s\)' % 
             (iId,DM,Med,Width,process,gq,gdm,bestobs,bestexp,xs,xsW,truewidth))
   #print 'mv Output.root %s/Output/%s_%s_%s_%s_%s_%s.root '%(basedir,label,str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)),iId)
   os.system('mv Output.root %s_%s_%s_%s_%s_%s.rootX '%(label,str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)),iId))

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

def runlimit(card='card.txt',limitdty='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/'):
   runlimitFile(card,limitdty)
   scale=checkrange()
   if scale > 100 or scale < 0.05:
      rescalesignal(card,scale)
      runlimitFile('rescale'+card,limitdty)
      return scale
   return 1

if __name__ == "__main__":
   label=options.label
   dm=options.dm
   med=options.med
   width=options.width
   gq=options.gq
   gdm=options.gdm
   proc=options.proc
   zcut="*(abs(v_id)==23)";
   wcut="*(abs(v_id)==24)";
   BR=1
   #compute BR assuming DM yukawa coupling
   if (proc == 805 or proc == 806) and not options.hinv:
      DMyuk=getWidthXS(dm,med,width,proc,gq,gdm)
      bmass=5.2
      if med > 1500:
         bmass =52.
      MByuk=getWidthXS(bmass,med,width,proc,gq,gdm)
      BR=float(DMyuk[0])/float(MByuk[0])*0.577
      if med > 1500:
         BR=BR*90.
      print "test yuk:",BR,DMyuk[0],MByuk[0]
   BRGG=1
   if options.hinv:
      BRGG=50.76
      #BRGG=47.76

   category =['monojet'            ,'boosted'          , 'resolved']
   cut      =[monojet              ,boosted            , resolved]
   files    =['monojet-combo.root' ,'boosted-combo.root'     ,'resolved-combo.root']
   cardfiles=['card_monojet.root'  ,'card_boosted.root','card_resolved.root']
   rwfil=    ['ggHRW'    ,'WHRW'  ,'ZHRW']
   trees=    ['ggH125_signal' ,'WH125_signal'   , 'ZH125_signal']
   labels=   ['signal_ggH'    ,'signal_wh'      , 'signal_zh']
   if options.monoJ:
      category =['monojet']
      cut      =[monojet  ]
      files    =['monojet-combo.root']
      cardfiles=['card_monojet.root' ]
      rwfil=    ['ggHRW']
      trees=    ['ggH_signal']
      labels=   ['signal_ggH']

   catd   = dict(zip(files,category))
   rwfild = dict(zip(trees,rwfil))
   filed  = dict(zip(files,cardfiles))
   labeld = dict(zip(trees,labels))
   cutd   = dict(zip(category,cut))
   for cat in category: 
      xsGG=reweight(label,dm,med,width,gq,gdm,proc,'H125_Gen.root' ,'Events',monojet         ,'ggHRW'+cat+'.root',False,BRGG)
      #xsGG=reweight(label,dm,med,width,gq,gdm,proc,'H125_Gen.root' ,'Events',cutd[cat]       ,'ggHRW'+cat+'.root',False,BRGG)
      if not options.monoJ:
         xsWB=reweight(label,dm,med,width,gq,gdm,proc,'WH115_Gen.root','Events',cutd[cat] + wcut,'WHRW' +cat+'.root',True,BR)
         xsZB=reweight(label,dm,med,width,gq,gdm,proc,'ZH115_Gen.root','Events',cutd[cat] + zcut,'ZHRW' +cat+'.root',True,BR)

   for treefile in files:
      for tree in trees:
         reweightNtuple(treefile,tree,rwfild[tree]+catd[treefile]+'.root')

   for card in cardfiles:
         os.system('cp %s/%s %s ' % (basedir,card,card))
   for tree in trees:
      for tfile in files:
         makeDataCard('%s'%(filed[tfile]),'RWTree'+rwfild[tree]+catd[tfile]+'.root',tree,labeld[tree])

   for tfile in files:
      makeDataCardVBF('%s'%(filed[tfile]),med,proc,BR)
   
   hinv=0
   if options.hinv:
      hinv=10
   scale=runlimit('card_monojet.txt')
   makeNtuple(0+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
   if not options.monoJ:
      scale=runlimit('card_boosted.txt')
      makeNtuple(1+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
      scale=runlimit('card_resolved.txt')
      makeNtuple(2+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
      scale=runlimit('card_v.txt')
      makeNtuple(3+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
      scale=runlimit('card.txt')
      makeNtuple(4+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
   scale=runlimit('card_monojet_simple.txt')
   makeNtuple(5+hinv,scale,label,dm,med,width,proc,xsGG,options.gq,options.gdm,BR)
