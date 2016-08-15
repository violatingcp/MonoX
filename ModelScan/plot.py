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
   print var,label,baseweight,y
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
   h1=makeHist(filename,var,mzrcut+"*mcWeight",treename,treename+'_mononz','',0)
   h1.SetBinContent(h1.GetNbinsX(),h1.GetBinContent(h1.GetNbinsX())+h1.GetBinContent(h1.GetNbinsX()+1))
   lFile.cd()
   h1.Write()
   lFile.Close()

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

   name='MonoZLL_%s_%s_%s_%s_%s_v.root' % (int(med),int(dm),str(int(gq)),str(int(gdm)),int(proc))
   makeFile(name,'events')
