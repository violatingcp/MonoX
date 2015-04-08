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
parser.add_option('--hinv'    ,action='store_true',         dest='hinv'    ,default=False,          help='Higgs Invisible') # need a few more options for monoV
parser.add_option('--monoJ'   ,action='store_true',         dest='monoJ'   ,default=False,          help='Just Monojet') # need a few more options for monoV
parser.add_option('--override',action='store_true',         dest='override',default=False,          help='Use Specified Ntuples') 
parser.add_option('--mj'      ,action='store',              dest='mj'      ,default='ggH125_signal',help='Monojet Base') 
parser.add_option('--zh'      ,action='store',              dest='zh'      ,default='ZH125_signal', help='ZH Base') 
parser.add_option('--wh'      ,action='store',              dest='wh'      ,default='WH125_signal', help='WH Base') 

(options,args) = parser.parse_args()

def fixNorm(filename,treename,cut):
   lFile = ROOT.TFile(filename)
   lTree = lFile.Get(treename)
   scale=float(lTree.GetEntriesFast())/float(lTree.GetEntries(cut))
   return scale

def makeHist(filename,var,baseweight,treename,label,normalize=False):
   x = array( 'd' )
   y=[100.0,200.0,210.0,220.0,230.0,240.0,250.0 , 260.0 , 270.0 , 280.0 , 290.0 , 300.0 , 310.0 , 320.0 , 330.0,340,360,380,420,710,1200,1500]
   for i0  in range(0,len(y)):
      x.append(y[i0])
   if len(filename) != 0:
      lFile = ROOT.TFile(filename)
      lTree = lFile.Get(treename)
      lHist = ROOT.TH1F(label,label,len(x)-1,x)
      lTree.Draw(var+'>>'+label,baseweight)
      lHist.SetDirectory(0)
   else:
      lHist = ROOT.TH1F(label,label,len(x)-1,x)
      return lHist
   if normalize:
      lHist.Scale(1./lTree.GetEntriesFast())
   return lHist

def reweight(label,DM,Med,Width,gq,gdm,process,basentuple,basename,basecut,iOutputName,monoV=False,iBR=1):
   xs = [1,1]
   scale = 1
   #Make Dummy weights
   if basentuple == '':
      h1=makeHist('','',basecut,'Events','model')
      h2=makeHist('','',basecut,'Events','base')
      for i0 in range(0,h1.GetNbinsX()+1):
         h1.SetBinContent(i0,1)
         h2.SetBinContent(i0,1)
   #MonoJet
   if not monoV and basentuple != '':
      loadmonojet(DM,Med,Width,process,gq,gdm)
      scale=ntuplexs(('MonoJ_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'Events')
      h1=makeHist(('MonoJ_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'dm_pt',basecut,'Events','model',True)
      h2=makeHist('%s/reweight/%s' % (basedir, basentuple) ,'dm_pt',basecut,basename,'base',True)           
      h1.Scale(iBR/1000.)
   elif basentuple != '':
      #MonoV
      loadmonov(DM,Med,Width,process,gq,gdm)
      xs=1
      #Add yukawa coupling by computing BR to inv vs B-quark
      label='MonoV_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))
      if process == 806 or process == 805 or process == 835 or process == 836:
         tmpProc = process
         #If corrected for Yukawa correct back
         if tmpProc > 830:
            tmpProc = tmpProc-30
            label=label.replace('83','80')
         #use the right VH samples
         label = label.replace('MonoV','MonoJHUV1')
         #Get the cross section and correct by BR
         xs=ntuplexs(('MonoJHUV1_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(tmpProc)))),'Events')
         if xs < 0:
            xs=-1.0e-10
         xs*=iBR
         #if basecut.find('23') > 0:
         #   xs=xs#*1.43 # Correct for BR? => Double check that x-section for base is inclusive
         #else:
         #   xs=xs#*1.48
      if process == 800 or process == 801 or process == 810 or process == 811 or process == 820 or process == 821:
         xs=xs*4  #Correction factor for Axial vector being majorana => fixed in new ntuples
         if basentuple.find("DM1") < 0:
            if basecut.find('23') > 0:
               xs=xs*1.43 # Correct for color factor and BR
            else:
               xs=xs*1.48
      h1=makeHist(label,'dm_pt',basecut,'Events','model',True)
      h2=makeHist('%s/reweight/%s' % (basedir, basentuple),'dm_pt',basecut,basename,'base',True)           
      h1.Scale(xs)
      print "Scaling :",xs
   h1.Divide(h2)
   lOFile = ROOT.TFile(iOutputName,'RECREATE')
   h1.Write()
   lOFile.Close()
   return xs

def reweightNtuple(iFile,iTreeName,iHistName,iHiggsPt=False,histlabel='model'):
   lHFile = ROOT.TFile('%s' % (iHistName))
   h1     = lHFile.Get(histlabel)
   #Add Higgs Pt Weight
   if iHiggsPt:
      lPtFile = ROOT.TFile('%s/reweight/PtW.root' % (basedir))
      hPt    = lPtFile.Get('Ratio1')

   #If Tree is empty put in a dummy branch and scale it down to nothing 
   baseweight=1
   if len(iTreeName) < 2:
      if iTreeName == '1':
         iTreeName = 'WH125_signal'
      if iTreeName == '2':
         iTreeName = 'ZH125_signal'
      if iTreeName.find('signal') < 0:
         iTreeName = 'ggH125_signal'
      baseweight=1e-10
   
   #Now reweight the ntuple
   lFile  = ROOT.TFile('%s/%s' % (basedir, iFile) )
   lTree  = lFile.Get(iTreeName+"Met")
   lOFile = ROOT.TFile('RWTree%s' % (iHistName),'UPDATE')
   lOTree = lTree.CloneTree(0)
   w2 = numpy.zeros(1, dtype=float)
   lOTree.Branch("w2",w2,"w2/D")
   for i0 in range(lTree.GetEntriesFast()):
      lTree.GetEntry(i0)
      jet1pt = lTree.dmpt
      w2[0] = 1
      w2[0]=h1.GetBinContent(h1.FindBin(jet1pt))*baseweight
      if iHiggsPt:
         if jet1pt < 480:
            w2[0]*=1./hPt.GetBinContent(hPt.FindBin(jet1pt))
         #   w2[0]*=1./hPt.GetFunction("pol2").Eval(jet1pt)
         else : 
            w2[0]*=1./hPt.GetBinContent(hPt.FindBin(480))
      lOTree.Fill()
   lOTree.Write()
   lOFile.Close()
   return iTreeName

def addHiggsPtWeightUnc(card,treefile,treename,label):
   lHFile = ROOT.TFile('%s/reweight/higgsPtWeights.root' % (basedir))
   hPt     = lHFile.Get('weights_muR125_muF125')
   hPtUp   = lHFile.Get('weights_muR250_muF250')
   hPtDown = lHFile.Get('weights_muR62.5_muF62.5')
   hPtUp  .Divide(hPt)
   hPtDown.Divide(hPt)
   lTFile  = ROOT.TFile(treefile)
   lTree   = lTFile.Get(treename+"Met")
   lOFile  = ROOT.TFile('%s' % card,'UPDATE')
   higgs   = lOFile.Get(label)
   labelsys=label.replace("signal","signalSYS")
   hOPtUp   = higgs.Clone(labelsys+"_hptUp")
   hOPtDown = higgs.Clone(labelsys+"_hptDown")
   for i0 in range(0,hPt.GetNbinsX()+1) : 
      hOPtUp  .SetBinContent(i0,0)   
      hOPtDown.SetBinContent(i0,0)   
   for i0 in range(0,lTree.GetEntriesFast()):
      lTree.GetEntry(i0)
      weightUp   = hPtUp  .GetBinContent(hPtUp  .FindBin(lTree.dmpt))
      weightDown = hPtDown.GetBinContent(hPtDown.FindBin(lTree.dmpt))
      hOPtUp  .Fill(lTree.mvamet,lTree.w2*weightUp)
      hOPtDown.Fill(lTree.mvamet,lTree.w2*weightDown)
   hOPtUp.Scale(higgs.Integral()/hOPtUp.Integral())
   hOPtDown.Scale(higgs.Integral()/hOPtDown.Integral())
   lOFile.cd()
   hOPtUp.Write()
   hOPtDown.Write()

def fix(iHist):
   if iHist.Integral() > 0: 
      return
   for i0 in range(0,iHist.GetNbinsX()+1) : 
      iHist.SetBinContent(i0,0)   
   iHist.Fill(501,1e-10)

def makeDataCard(card,newntuple='BaseOut.root',treename='GGH0',label='GGH'):
   print "Reweighting:",card,label,"Ntuple :",newntuple,treename
   lFile  = ROOT.TFile('%s/%s' % (basedir,card))
   lH1    = lFile.Get(label)
   labelsys=label.replace('signal','signalSYS')
   lH0    = lFile.Get(labelsys+'_MetUp')
   lH2    = lFile.Get(labelsys+'_MetDown')
   lH1.SetDirectory(0)
   if lH0 : 
      lH0.SetDirectory(0)
      lH2.SetDirectory(0)
   #Load ntuple
   lTFile = ROOT.TFile(newntuple)
   lTree  = lTFile.Get(treename+'Met')
   #Write Hists
   lOFile  = ROOT.TFile('%s' % card,'UPDATE')
   lOH1   = lH1.Clone()
   if lH0 :
      lOH0   = lH0.Clone()
      lOH2   = lH2.Clone()
   for i0 in range(1,lH1.GetNbinsX()+1) : 
      lOH1.SetBinContent(i0,0)
      if lH0 :
         lOH0.SetBinContent(i0,0)
         lOH2.SetBinContent(i0,0)
   lTree.Draw('mvamet>>'+lOH1.GetName(),'w2*weight')
   fix(lOH1);
   print "Card :",card,label,"Yield",lOH1.Integral()
   lOH1.Write()
   if lH0 :
      lTree.Draw('mvametUp>>'  +lOH0.GetName(),'w2*weight')
      lTree.Draw('mvametDown>>'+lOH2.GetName(),'w2*weight')
      fix(lOH0);
      fix(lOH2);
      lOH0.Write()
      lOH2.Write()
   lOFile.Close()

def makeDataCardVBF(card,med,proc,iBR,label='signal_vbf',xs='reweight/VBFXS.root'):
   lFile  = ROOT.TFile('%s/%s' % (basedir,xs))
   lXS    = lFile.Get('xs')
   lXS125 = lXS.Eval(125)
   lXSMed = lXS.Eval(med)
   lScale = lXSMed/lXS125*iBR
   if proc != 805 and proc != 806 and proc != 835 and proc != 836:
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

def fullresults(iBase,override,label,dm,med,width,proc,g,gdm,BR,post):
   xst=[1,1]
   scale=runlimit('card_monojet'+post ,basedir)
   xst=makeNtuple(0+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
   scale=runlimit('card_boosted'+post ,basedir)
   makeNtuple(1+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
   scale=runlimit('card_resolved'+post,basedir)
   makeNtuple(2+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
   scale=runlimit('card_v'+post       ,basedir)
   makeNtuple(3+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
   scale=runlimit('card'+post         ,basedir)
   makeNtuple(4+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
   if iBase < 100 : 
      scale=runlimit('card_monojet_simple.txt',basedir)
      makeNtuple(5+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
      #scale=runlimit('card_noEWK.txt',basedir)
      #makeNtuple(6+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)
      #scale=runlimit('card_Unc.txt',basedir)
      #makeNtuple(7+iBase,override,scale,label,dm,med,width,proc,xst,gq,gdm,BR)

def computeBR(dm,med,width,gq,gdm,proc,hinv,override):
   BR=1
   #compute BR assuming DM yukawa coupling
   if (proc == 805 or proc == 806 or proc == 835 or proc == 836) and not hinv and not override:
      DMyuk=getWidthXS(dm,med,width,proc,gq,gdm,False)
      bmass=5.2
      if med > 400:
         bmass = 172.3
      SMBR=0.577
      lRWFile = ROOT.TFile('%s/reweight/ScalarCorr.root' % basedir)
      lFBR = lRWFile.Get("BRbb")
      if bmass > 150:
         lFBR = lRWFile.Get("BRtt")
      SMBR = lFBR.Eval(med)
      lRWFile.Close()
      MByuk=getWidthXS(bmass,med,width,proc,gq,gdm,False)
      BR=float(DMyuk[0])/float(MByuk[0])*SMBR
      print "Branching ratio : ",SMBR,"mass",bmass,BR,DMyuk[0],MByuk[0]
   return BR

if __name__ == "__main__":
   label=options.label
   dm=options.dm
   med=options.med
   width=options.width
   gq=options.gq
   gdm=options.gdm
   proc=options.proc
   zcut="*(abs(v_id)==23)"
   wcut="*(abs(v_id)==24)"
   BR=computeBR(dm,med,width,gq,gdm,proc,options.hinv,options.override)
   BRGG=1
   if options.hinv:
      BRGG=50.76 

   #Build the config
   category =['monojet'                 ,'boosted'             ,'resolved']
   cut      =[monojet                   ,boosted               ,resolved]
   files    =['monojet-combo.root'      ,'boosted-combo.root'  ,'resolved-combo.root']
   cardfiles=['card_monojet.root'       ,'card_boosted.root'   ,'card_resolved.root']
   ##Reweighting
   rwfil=    ['ggHRW'    ,'WHRW'  ,'ZHRW']
   trees=    ['ggH125_signalMet' ,'WH125_signalMet'   , 'ZH125_signalMet']
   #Signal Base reweighting
   labels=   ['signal_ggH'    ,'signal_wh'      , 'signal_zh']
   basetree= ['H125_Gen.root' ,'WH115_Gen.root' , 'ZH115_Gen.root']

   #Determine the sample to use reweighting by scanning
   for i0 in range(0,4):
      id0 = i0 - (i0 > 1)
      if i0 != 1:
         basetree[id0],trees[id0]=obtainbase(i0,dm,med,proc,options.hinv)

   #If Option Override just reweight with the specified ntuples
   if options.override:
      for i0 in range(0,3):
         basetree[i0] = ''
      trees[0] = options.mj
      trees[1] = options.wh
      trees[2] = options.zh
   #List them
   for i0 in range(0,3):
      print "Ntuples : ",basetree[i0],"-- using",trees[i0]
   
   #Build dictionaries
   catd    = dict(zip(files,category))
   rwfild  = dict(zip(trees,rwfil))
   filed   = dict(zip(files,cardfiles))
   cutd    = dict(zip(category,cut))
   
   #Loop through the categories and build the weight hitograms as listed in rwfile
   for cat in category: 
      xsGG=reweight(label,dm,med,width,gq,gdm,proc,basetree[0],'Events',monojet         ,'ggHRW'+cat+'.root',False,BRGG)
      xsWB=reweight(label,dm,med,width,gq,gdm,proc,basetree[1],'Events',cutd[cat] + wcut,'WHRW' +cat+'.root',True,BR)
      xsZB=reweight(label,dm,med,width,gq,gdm,proc,basetree[2],'Events',cutd[cat] + zcut,'ZHRW' +cat+'.root',True,BR)

   #Build ntuples with modified weights => if blank re-assign
   outtrees=[trees[0],trees[1],trees[2]]
   for treefile in files:
      for tree in trees:
         outtrees[trees.index(tree)]=reweightNtuple('base/'+treefile,tree,rwfild[tree]+catd[treefile]+'.root',options.hinv)

   #Get the Cards
   for card in cardfiles:
         os.system('cp %s/%s %s ' % (basedir,card,card))

   #Construct the signal files
   labeld  = dict(zip(outtrees,labels))
   rwfild2 = dict(zip(outtrees,rwfil))

   #Base
   for tree in outtrees:
      for tfile in files:
         makeDataCard('%s'%(filed[tfile]),'RWTree'+rwfild2[tree]+catd[tfile]+'.root',tree,labeld[tree])
         if options.hinv and tree.find('ggH') > -1:
            addHiggsPtWeightUnc('%s'%(filed[tfile]),'RWTree'+rwfild2[tree]+catd[tfile]+'.root',tree,labeld[tree])
   #VBF
   for tfile in files:
      makeDataCardVBF('%s'%(filed[tfile]),med,proc,BR)

   #Clean up
   for rwfile in rwfil: 
      for cat in category:
         os.system('rm '+rwfile+cat+'.root')
         os.system('rm RWTree'+rwfile+cat+'.root')

   hinv=0
   if options.hinv:
      hinv=10
   post='.txt'
   if options.hinv:
      post='_higgs.txt'

   #Base results
   fullresults(hinv,options.override,label,dm,med,width,proc,options.gq,options.gdm,BR,post)      
   os.system('mkdir Cards')
   os.system('mv *.txt Cards')
   os.system('mkdir root')
   os.system('mv *.root root')
   os.system('rm runlimit.sh')
