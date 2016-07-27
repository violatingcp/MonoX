#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array    import array

from MonoX.ModelScan.generate      import loadmonov,loadmonojet,loadmonoggz,getWidthXS
from MonoX.ModelScan.ntuple        import makeNtuple,ntuplexs
from MonoX.ModelScan.reweightmap   import obtainbasez
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

def end():
   #if __name__ == '__main__':
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

def makeHist(filename,var,baseweight,treename,label,normalize='',iMonoVBin=False):
   x = array( 'd' )
   y=mzrbins
   if iMonoVBin==1:
      y=mzrbins
   if iMonoVBin==2:
      y=mzgbins
   if iMonoVBin==3:
      y=mzgbins
   if iMonoVBin==-1:
      y=[-100,10000]
   for i0  in range(0,len(y)):
      x.append(y[i0])
   print var,label,baseweight
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
   h1=makeHist(filename,var,mzrcut+"*newWeight",treename,treename+'_mononz','',0)
   h1.SetBinContent(h1.GetNbinsX(),h1.GetBinContent(h1.GetNbinsX())+h1.GetBinContent(h1.GetNbinsX()+1))
   lFile.cd()
   h1.Write()
   lFile.Close()

def reweight(label,DM,Med,Width,gq,gdm,process,basentuple,basename,basecut,basecutReco,iOutputName,monoV,monoGGZ,iVId=0,iBR=1):
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
   else :
      loadmonojet(DM,Med,Width,process,gq,gdm,'model3_v2')

   #label='MonoJ_%s_%s_%s_%s_mcfm.root'    % (str(int(Med)),str(int(DM)),str(gq),str(int(process)))
   label='MonoJ_%s_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(gq),str(gdm),str(int(process)))
   if monoV and not monoGGZ:
      label='MonoJ_%s_%s_%s_%s.root'    % (str(int(Med)),str(int(DM)),str(gq),str(int(process)))
   weight1="evtweight*1000*"+basecut+"*"
   weight2=basecutReco
   var1="v_pt"
   var2="genP4.Pt()"
   Norm1='(v_pt > 0)'
   Norm2=''
   useMonoVBin=2
   if basecut.find('fjm') > 0: 
      useMonoVBin=3
   if iVId > 0:
      var1="v_pt"
      var2="genP4.Pt()"
      if monoGGZ:
         label=label.replace("MonoJ","MonoGGZ")
      else:
         label=label.replace("MonoJ","MonoV")
      
      weight1="xs"
      if process < 802 or monoGGZ:
         weight1=weight1+"2"
         if process < 802:#Correcting for Majorana
            weight1=weight1+"*2" 
         #if process < 802 and Med < 3500:
            #weight1=weight1+"*7.0/4.9"#Correction for rounding in top width
         #   weight1=weight1+"*1.5"#Correction for rounding in top width
      if process > 802 and not monoGGZ:
         weight1=weight1+"*"+str(getXS(Med,iVId))
      if abs(iVId) == 23:
         weight2=weight2+"*(genPdgId==23)"
      weight1=weight1+"*1000*"+basecut.replace("23","23")+"*"
      Norm1='(abs(v_id) == '+str(iVId)+')'
   h1=makeHist(label     ,var1,weight1+Norm1,'Events','model',Norm1,useMonoVBin)
   h2=makeHist(basentuple,var2,weight2+Norm2,basename,'base' ,Norm2,useMonoVBin)           
   print h1.Integral()
   if int(iVId) == 23 and process < 802:
      h1.Scale(1./fixNorm(label,"Events",Norm1))
   #h1.Scale(h2.Integral()/h1.Integral())
   h1.Divide(h2)
   os.system('mv %s old' % label)
   print "Yields",h1.Integral(),h2.Integral()
   lOFile = ROOT.TFile(iOutputName,'RECREATE')
   h1.Write()
   lOFile.Close()
   return xs

def reweightNtuple(iFile,iTreeName,iHistName,iOTreeName,iClass,iMonoV,iHiggsPt=False,histlabel='model'):
   print iFile,iTreeName,iHistName,iOTreeName,iMonoV
   lHFile = ROOT.TFile('%s' % (iHistName))
   h1     = lHFile.Get(histlabel)
   #If Tree is empty put in a dummy branch and scale it down to nothing 
   baseweight=1
   #Now reweight the ntuple
   lFile  = ROOT.TFile('%s' % iFile)
   lTree  = lFile.Get(iTreeName)
   lTree.SetBranchStatus("*",0)
   lTree.SetBranchStatus("genPdgId",1)
   lTree.SetBranchStatus("genP4",1)
   lTree.SetBranchStatus("metP4",1)
   lTree.SetBranchStatus("totalWeight",1)
   lTree.SetBranchStatus("mcWeight",1)

   lOFile = ROOT.TFile('tmpRWTree%s' % (iHistName),'RECREATE')
   #lFTree = lTree.CopyTree(iClass)
   #lFTree = lTree.CopyTree('')
   lOTree = lTree.CloneTree(0)
   lOTree.SetTitle(iOTreeName)
   lOTree.SetName(iOTreeName)
   w1 = numpy.zeros(1, dtype=float)
   w2 = numpy.zeros(1, dtype=float)
   lOTree.Branch("newWeight",w2,"w2/D")
   #lOTree.SetBranchAddress("mcWeight",w1)
   for i0 in range(0,lTree.GetEntriesFast()):
      if i0 % 10000 == 0:
         print i0,"total",lTree.GetEntriesFast()
      lTree.GetEntry(i0)
      genpt=-1
      for i1 in range(0,lTree.genP4.GetEntries()):
         if lTree.genPdgId[i1] == 23:
            genpt = lTree.genP4[i1].Pt()
            
      if genpt > 400:
         genpt = 395
      if genpt < 5:
         genpt = 5
      #w1[0] = 1
      #w2[0] = lTree.mcWeight
      w2[0] = h1.GetBinContent(h1.FindBin(genpt))*baseweight
      #w1[0] = w1[0] * w2[0]
      #print i0,genpt,w2[0]
      lOTree.Fill()
   lOTree.Write()
   lOFile.Close()
   return iTreeName

def treeName(proc,med,dm,gq,gdm,iId,monoGGZ):
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
   if iId == 23 and monoGGZ:
      Name="MonoGGZ_"+Name
   if iId == 1:
      Name="VBF_"+Name
   Name="%s_%s_%s_%s_%s_signal" % (Name,int(med),int(dm),str(gq),str(gdm))
   return Name

def reweight_z(options):
   label=options.label
   dm=options.dm
   med=options.med
   width=options.width
   gq=options.gq
   gdm=options.gdm
   proc=options.proc
   BRGG=1
   baseid=0
   cuts=[monoz]
   cutsReco=[monozReco]
   monoV = True
   baseid=23
   cut=boosted+"*(abs(v_id) == 23)"
   monoV =  True

   if options.monoGGZ:
      baseid=23
      cut=boosted+"*(abs(v_id) == 23)"
      monoV =  True
   
   #Determine the sample to use reweighting by scanning
   basetree,trees=obtainbasez(baseid,dm,med,proc,False)
   basetreegen=basetree
   os.system('cmsStage %s/%s .' % (eosbasedir,basetree))
   treesgen=trees
   #List them
   print "Ntuples : ",basetree,"-- using",trees,label,trees,gq
   os.system('mkdir old')
   os.system('rm *ggHRWmonojet.root')
   for i0 in range(0,len(cuts)):
      xsGG=reweight(label,dm,med,width,gq,gdm,proc,basetreegen,treesgen,cuts[i0],cutsReco[i0],'ggHRWmonojet.root',monoV,options.monoGGZ,baseid,BRGG)
      idcut=''
      #Build ntuples with modified weights => if blank re-assign
      reweightNtuple(basetree,trees,'ggHRWmonojet.root',treeName(proc,med,dm,gq,gdm,baseid,options.monoGGZ),idcut,monoV)
      if i0 > 0:
         os.system('hadd tmp2TreeggHRWmonojet.root RWTreeggHRWmonojet.root tmpRWTreeggHRWmonojet.root')
         os.system('cp RWTreeggHRWmonojet.root tmpXRWTreeggHRWmonojet.root')
         os.system('mv tmp2TreeggHRWmonojet.root tmpRWTreeggHRWmonojet.root')
      os.system('mv tmpRWTreeggHRWmonojet.root RWTreeggHRWmonojet.root')

   name='MonoZLL_%s_%s_%s_%s_%s.root' % (int(med),int(dm),str(gq),str(gdm),int(proc))
   if options.monoGGZ:
      name=name.replace('MonoZLL','MonoGGZLL')
   name=name.replace('1.0','1')
   makeFile('RWTreeggHRWmonojet.root',treeName(proc,med,dm,gq,gdm,baseid,options.monoGGZ))
   os.system('mv RWTreeggHRWmonojet.root %s' % name)
      
if __name__ == "__main__":
   options = parser()
   reweight_z(options)
   
