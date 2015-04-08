#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy,math
from MonoX.ModelScan.generate import getWidthXS
from optparse import OptionParser
import ROOT as r

def pseudoscalar(iMed,iMass,iCoupl,iGamma):
   lVal    = 0.5 *  1./r.TMath.Pi()  * 3
   lDenom  = (iMed*iMed-4.*iMass*iMass)*(iMed*iMed-4.*iMass*iMass)
   lDenom += iMed*iMed*iGamma*iGamma;
   lVal /= lDenom;
   lVal *= iMass *iMass;
   lVal *= iCoupl*iCoupl;
   lVal *= r.TMath.Sqrt(1.-(4.2*4.2)/iMass/iMass);
   #Adding Yukawa Copulings
   lVal *= (4.2/246.)*(4.2/246.);
   lVal *= (iMass/246.)*(iMass/246.);
   return lVal;

def scalar(iMed,iMass,iCoupl):
   lVal  = 3.83
   lMass = iMed/100.
   lMu   = (0.938*iMass)/(0.938+iMass)
   lVal *= 1./r.TMath.Power((lMass),4.)
   lVal *= iCoupl*iCoupl;
   lVal *= lMu*lMu;
   lVal *= (iMass/246.)*(iMass/246.);
   return lVal;

def vector(iMed,iMass,iCoupl):
   lVal  = 1.1*100.
   lMass = iMed/1000.
   lMu   = (0.938*iMass)/(0.938+iMass)
   lVal  *= 1./r.TMath.Power((lMass),4.)
   lVal  *= iCoupl*iCoupl/16.
   lVal  *= lMu*lMu
   return lVal

def axial(iMed,iMass,iCoupl):
   lVal  = 4.6*0.47/0.43
   lMass = iMed/1000.
   lMu   = (0.938*iMass)/(0.938+iMass) 
   lVal  *= 1./r.TMath.Power((lMass),4.)
   lVal  *= iCoupl*iCoupl/16.
   lVal  *= lMu*lMu
   return lVal

def ntuplexs(filename,treename):
   lFile = ROOT.TFile(filename)
   lTree = lFile.Get(treename)
   lTree.GetEntry(0)
   return lTree.mcweight

def makeNtuple(iId,override,scale,label,DM,Med,Width,process,xst=[1,1],gq=1,gdm=1,BR=1):
   #Declare file
   lFile  = r.TFile('%s_%s_%s_%s_%s_%s.rootX '%(label,str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)),iId),'RECREATE')
   lTree  = r.TTree("limit","limit");
   #Coordinates
   fId    = numpy.zeros(1, dtype=int)
   fProc  = numpy.zeros(1, dtype=int)
   fMass  = numpy.zeros(1, dtype=float)
   fMed   = numpy.zeros(1, dtype=float)
   fWidth = numpy.zeros(1, dtype=float)
   fGQ    = numpy.zeros(1, dtype=float)
   fGDM   = numpy.zeros(1, dtype=float)
   fXS    = numpy.zeros(1, dtype=float)
   fXSY   = numpy.zeros(1, dtype=float)
   fBR    = numpy.zeros(1, dtype=float)
   fXSN   = numpy.zeros(1, dtype=float)
   #Results
   fObs   = numpy.zeros(1, dtype=float)
   fExp   = numpy.zeros(1, dtype=float)
   f1PSigma = numpy.zeros(1, dtype=float)
   f1MSigma = numpy.zeros(1, dtype=float)
   f2PSigma = numpy.zeros(1, dtype=float)
   f2MSigma = numpy.zeros(1, dtype=float)
   #Build Tree
   lTree.Branch("id"   ,fId     ,"fId/I")
   lTree.Branch("proc" ,fProc   ,"fProc/I")
   lTree.Branch("m"    ,fMass   ,"fMass/D")
   lTree.Branch("med"  ,fMed    ,"fMed/D")
   lTree.Branch("w"    ,fWidth  ,"fWidth/D")
   lTree.Branch("gq"   ,fGQ     ,"fGQ/D")
   lTree.Branch("gdm"  ,fGDM    ,"fGDM/D")
   lTree.Branch("xs"   ,fXS     ,"fXS/D")
   lTree.Branch("xsY"  ,fXSY    ,"fXSY/D")
   lTree.Branch("br"   ,fBR     ,"fBR/D")
   lTree.Branch("xsN"  ,fXSN    ,"fXSN/D")
   #Results
   lTree.Branch("obs"  ,fObs    ,"fObs/D")
   lTree.Branch("exp"  ,fExp    ,"fExp/D")
   lTree.Branch("P1sigma",f1PSigma  ,"f1PSigma/D")
   lTree.Branch("P2sigma",f2PSigma  ,"f2PSigma/D")
   lTree.Branch("M1sigma",f1MSigma  ,"f1MSigma/D")
   lTree.Branch("M2sigma",f2MSigma  ,"f2MSigma/D")

   xs=1
   if not override:
      xs=ntuplexs(('MonoJ_%s_%s_%s_%s.root' % (str(int(Med)),str(int(DM)),str(int(Width)),str(int(process)))),'Events')
   #xst=[1,1]
   print xst
   if process == 806 or process == 805 and not override and xst[0] == 1:
      xst=getWidthXS(DM,Med,Width,int(process),gq,gdm,True)
   print xst
   fId[0]    = iId
   fProc[0]  = process
   fMass[0]  = DM
   fMed[0]   = Med
   fWidth[0] = Width*float(xst[1])
   fGQ[0]    = gq
   fGDM[0]   = gdm
   fXS[0]    = float(xst[0])
   fXSY[0]   = xs
   fBR[0]    = BR
   lCoupl = gq*gdm
   if process == 835 or process == 836:
      lCoupl = gq*gdm*242./DM
   if process == 800:
      fXSN[0] = vector      (Med,DM,lCoupl)
   if process == 801:
      fXSN[0] = axial       (Med,DM,lCoupl)
   if process == 805:
      fXSN[0] = scalar      (Med,DM,lCoupl)
   if process == 806:
      fXSN[0] = pseudoscalar(Med,DM,lCoupl,fWidth[0])
   if process == 810:
      fXSN[0] = vector      (Med,DM,lCoupl)*0.44
   if process == 811:
      fXSN[0] = axial       (Med,DM,lCoupl)*5.30
   if process == 820:
      fXSN[0] = vector      (Med,DM,lCoupl)*1./9.
   if process == 821:
      fXSN[0] = axial       (Med,DM,lCoupl)*12.79
   if process == 835:
      fXSN[0] = scalar      (Med,DM,lCoupl)
   if process == 836:
      fXSN[0] = pseudoscalar(Med,DM,lCoupl,fWidth[0])

   lTFile = ROOT.TFile('higgsCombineTest.Asymptotic.mH120.root')
   lLTree  = lTFile.Get('limit')
   lLTree.GetEntry(0)
   f2MSigma[0]=lLTree.limit*scale
   lLTree.GetEntry(1)
   f1MSigma[0]=lLTree.limit*scale
   lLTree.GetEntry(2)
   fExp[0]=lLTree.limit*scale
   lLTree.GetEntry(3)
   f1PSigma[0]=lLTree.limit*scale
   lLTree.GetEntry(4)
   f2PSigma[0]=lLTree.limit*scale
   lFile.cd()
   lTree.Fill()
   lTree.Write()
   lFile.Close();
   return xst
#parser = OptionParser()
#parser.add_option('--dm'   ,action='store',type='int',dest='dm'    ,default=10,  help='Dark Matter Mass')
#parser.add_option('--med'  ,action='store',type='int',dest='med'   ,default=2000,help='Mediator Mass')
#parser.add_option('--proc' ,action='store',type='int',dest='proc'  ,default=806, help='Process(800=V,801=A,805=S,806=P)')
#(options,args) = parser.parse_args()

#if __name__ == "__main__":
#   makeNtuple(0,1,'MonoJ',options.dm,options.med,1,options.proc,gq=1,gdm=1,BR=1)

