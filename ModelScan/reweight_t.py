#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array    import array

from MonoX.ModelScan.generate      import loadmonov,loadmonojet,loadmonoggz,loadmonotop,getWidthXS
from MonoX.ModelScan.ntuple        import makeNtuple,ntuplexs
from MonoX.ModelScan.reweightmap   import obtainbasetop
from MonoX.ModelScan.config        import *
from MonoX.ModelScan.limittools    import *

from optparse import OptionParser

def parser():
   rparser = OptionParser()
   rparser.add_option('--dm'      ,action='store',type='float',dest='dm'       ,default=1,              help='Dark Matter Mass')
   rparser.add_option('--med'     ,action='store',type='float',dest='med'      ,default=150,            help='Mediator Mass')
   rparser.add_option('--width'   ,action='store',type='float',dest='width'    ,default=1,              help='Width (in Min width units)')
   rparser.add_option('--proc'    ,action='store',type='float',dest='proc'     ,default=805,            help='Process(800=V,801=A,805=S,806=P)')
   rparser.add_option('--gq'      ,action='store',type='float',dest='gq'       ,default=1.0,            help='coupling to quarks')
   rparser.add_option('--gdm'     ,action='store',type='float',dest='gdm'      ,default=1.0,            help='coupling to dark matter')
   rparser.add_option('--label'   ,action='store',type='string',dest='label'   ,default='model3_v2',    help='eos label')
   rparser.add_option('--monoZ'   ,action='store_true',         dest='monoZ'   ,default=False,          help='Run mono Z generation') # need a few more options for monoV
   rparser.add_option('--monoGGZ' ,action='store_true',         dest='monoGGZ' ,default=False,          help='Run mono GGZ generation') # need a few more options for monoV
   rparser.add_option('--monoTop' ,action='store_true',         dest='monoTop' ,default=False,          help='Run mono Top') # need a few more options for monoV
   (options,args) = rparser.parse_args()
   return options

def getXS(iMed,iId,basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_3_3/src/genproductions/bin/JHUGen/'):
    lFile  = ROOT.TFile(basedir+'/patches/WZXS.root')
    label="ZH"
    if int(iId) == 24:
       label="WH"
    lG     = lFile.Get(label)
    lScale = lFile.Get("scaleUp")
    lBR    = lFile.Get("BRbb")
    if iMed > 500:
       lBR    = lFile.Get("BRtt")
    print lBR,iMed,label,iId
    scale=int(iMed)+91+15 # 15 is an approximation of the extra energy based on matching xsections at 125
    if int(iId) == 24:
       scale=int(iMed)+80+15
    #Correct for the BR to fermions assuming Scalar decays to bosons                                                                                                                                       
    lBaseMass=4.2
    if iMed > 500:
       lBaseMass=172.5
    BRCorr = min(lBR.Eval(iMed)*246.*246./lBaseMass/lBaseMass,1.)
    return lG.Eval(iMed)*lScale.Eval(scale)*BRCorr

def getXS2(iFile,iTree):
   lFile = ROOT.TFile.Open(iFile)
   lTree = lFile.Get(iTree)
   lTree.GetEntry(0)
   return lTree.xs2

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def fixNorm(filename,treename,cut):
   lFile = ROOT.TFile(filename)
   lTree = lFile.Get(treename)
   scale=float(lTree.GetEntriesFast())/float(lTree.GetEntries(cut))
   return scale

def makeHist(filename,var,baseweight,treename,label,normalize='',iMonoVBin=2):
   x = array( 'd' )
   y=mtrbins
   if iMonoVBin==1:
      y=mtrbins
   if iMonoVBin==2:
      y=mtgbins
   if iMonoVBin==3:
      y=mtgbins
   if iMonoVBin==-1:
      y=[-100,10000]
   for i0  in range(0,len(y)):
      x.append(y[i0])
   if len(filename) != 0:
      lFile = ROOT.TFile.Open(filename)
      lTree = lFile.Get(treename)
      lHist = ROOT.TH1F(label,label,len(x)-1,x)
      lTree.Draw(var+'>>'+label,baseweight)
      lHist.SetDirectory(0)
   else:
      lHist = ROOT.TH1F(label,label,len(x)-1,x)
      return lHist
   if normalize != '':
      print "NORM : ",normalize,baseweight
      lHist.Scale(1./lTree.GetEntries(normalize))
   return lHist

def makeFile(filename,treename,var='metP4.Pt()'): #pfMetPt
   outfilename=treename+".root"
   lFile = ROOT.TFile(outfilename,"RECREATE")
   h1=makeHist(filename,var,mzrcut,treename,treename+'_monojet','',0)
   lFile.cd()
   h1.Write()
   lFile.Close()

def reweight(label,DM,Med,Width,gq,gdm,process,basentuple,basename,basecut,basecutReco,iOutputName,monoV,monoGGZ,monoTop,iVId=0,iBR=1):
   xs = [1,1]
   scale = 1
   h1=makeHist('','',basecut,'Events','model')
   h2=makeHist('','',basecut,'Events','base')
   for i0 in range(0,h1.GetNbinsX()+1):
      h1.SetBinContent(i0,1)
      h2.SetBinContent(i0,1)
   #MonoJet
   if basentuple == '':
      return
   if monoV and not monoGGZ :
      loadmonov(DM,Med,Width,process,gq,gdm)
   elif monoGGZ :
      loadmonoggz(DM,Med,Width,process,gq,gdm,'model3_v2')
   elif monoTop :
      loadmonotop(DM,Med,Width,process,gq,gdm,'model3_v2')
   else :
      loadmonojet(DM,Med,Width,process,gq,gdm,'model3_v2')
   label='MonoJ_%s_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(gq),str(gdm),str(int(process)))
   if monoV and not monoGGZ:
      label='MonoJ_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(gq),str(int(process)))
   weight1="evtweight*1000*"+basecut+"*"
   weight2=basecutReco
   var1="v_pt"
   var2="genP4.Pt()"
   Norm1='(v_pt > 0)'
   useMonoVBin=2
   if basecut.find('fjm') > 0: 
      useMonoVBin=3
   if iVId > 0:
      var1="v_pt"
      var2="genVBosonPt"
      if monoGGZ:
         label=label.replace("MonoJ","MonoGGZ")
      elif monoV:
         label=label.replace("MonoJ","MonoV")
      else:
         label=label.replace("MonoJ","MonoTop")
      weight1="xs"
      if process < 802 or monoGGZ:
         weight1=weight1+"2"
      if process > 802 and not monoGGZ:
         weight1=weight1+"*"+str(getXS(Med,iVId))
      weight1=weight1+"*1000*"+basecut.replace("23","23")+"*"
      Norm1='(abs(v_id) == '+str(iVId)+')'
   if monoTop:
      var1="top1pt"
      var2="genTopPt"
      Norm1='(top1pt > 0)'
      Norm2=''
      xs[0]=getXS2(label,'Events')
      useMonoVBin=2
   h1=makeHist(label     ,var1,weight1+Norm1,'Events','model',Norm1,useMonoVBin)
   h2=makeHist(basentuple,var2,weight2+Norm2,basename,'base' ,Norm2,useMonoVBin)           
   if int(iVId) == 23 and process < 802:
      h1.Scale(1./fixNorm(label,"Events",Norm1))
   os.system('mv %s old' % label)
   print "Integral:",h1.Integral(),h2.Integral()
   h1.Divide(h2)
   lOFile = ROOT.TFile(iOutputName,'RECREATE')
   h1.Write()
   lOFile.Close()
   return xs

def reweightNtuple(iFile,iTreeName,iHistName,iOTreeName,iClass,iMonoV,iXS,iHiggsPt=False,histlabel='model'):
   lHFile = ROOT.TFile('%s' % (iHistName))
   h1     = lHFile.Get(histlabel)
   #If Tree is empty put in a dummy branch and scale it down to nothing 
   baseweight=1
   #Now reweight the ntuple
   lFile  = ROOT.TFile('%s' % iFile)
   lTree  = lFile.Get(iTreeName)
   lOFile = ROOT.TFile('tmpRWTree%s' % (iHistName),'RECREATE')
   lOTree = lTree.CloneTree(0)
   lOTree.SetTitle(iOTreeName)
   lOTree.SetName(iOTreeName)
   w1 = numpy.zeros(1, dtype=float)
   w2 = numpy.zeros(1, dtype=float)
   lOTree.Branch("weight",w1,"w2/D")
   lOTree.Branch("xs"    ,w2,"w2/D")
   for i0 in range(lTree.GetEntriesFast()):
      lTree.GetEntry(i0)
      genpt=-1
      genpt = lTree.genTopPt
      w1[0] = h1.GetBinContent(h1.FindBin(genpt))*baseweight
      w2[0] = iXS
      lOTree.Fill()
   lOTree.Write()
   lOFile.Close()
   return iTreeName

def treeName(proc,med,dm,gq,gdm,iId):
   Name='V'
   if proc == 801:
      Name='A'
   if proc == 805:
      Name='S'
   if proc == 806:
      Name='P'
   if iId == 24:
      Name="MonoW_"+Name
   if iId == 23:
      Name="MonoZ_"+Name
   if iId == 1:
      Name="VBF_"+Name
   Name="%s_%s_%s_%s_%s_signal" % (Name,int(med),int(dm),str(gq),str(gdm))
   return Name
      
if __name__ == "__main__":
   options = parser()
   label=options.label
   dm=options.dm
   med=options.med
   width=options.width
   gq=options.gq
   gdm=options.gdm
   proc=options.proc
   BRGG=1
   baseid=0
   cuts=[monot]
   cutsReco=[monotReco]
   monoTop = True
   baseid=6
   monoV =  False
   #Determine the sample to use reweighting by scanning
   basetree,trees=obtainbasetop(baseid,dm,med,proc,False)
   basetreegen=basetree
   os.system('cmsStage %s/%s .' % (eostopbasedir,basetree))
   os.system('echo cmsStage %s/%s .' % (eostopbasedir,basetree))
   treesgen=trees
   #List them
   print "Ntuples : ",basetree,"-- using",trees,label,trees,gq
   os.system('mkdir old')
   os.system('rm *ggHRWmonojet.root')
   for i0 in range(0,len(cuts)):
      xsGG=reweight(label,dm,med,width,gq,gdm,proc,basetreegen,treesgen,cuts[i0],cutsReco[i0],'ggHRWmonojet.root',monoV,options.monoGGZ,monoTop,baseid,BRGG)
      idcut=''
      #Build ntuples with modified weights => if blank re-assign
      reweightNtuple(basetree,trees,'ggHRWmonojet.root',treeName(proc,med,dm,gq,gdm,baseid),idcut,monoV,xsGG[0])
      if i0 > 0:
         os.system('hadd tmp2TreeggHRWmonojet.root RWTreeggHRWmonojet.root tmpRWTreeggHRWmonojet.root')
         os.system('cp RWTreeggHRWmonojet.root tmpXRWTreeggHRWmonojet.root')
         os.system('mv tmp2TreeggHRWmonojet.root tmpRWTreeggHRWmonojet.root')
      os.system('mv tmpRWTreeggHRWmonojet.root RWTreeggHRWmonojet.root')

   name='MonoTop_%s_%s_%s_%s_%s.root' % (int(med),int(dm),str(gq),str(gdm),int(proc))
   #name=name.replace('1.0','1')
   os.system('mv RWTreeggHRWmonojet.root %s' % name)

