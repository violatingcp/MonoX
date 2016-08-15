#! /usr/bin/env python

import ROOT as r
import argparse,commands,os

aparser = argparse.ArgumentParser(description='Process benchmarks.')
#aparser.add_argument('-sample'  ,'--sample'    ,action='store' ,dest='sample' ,default='Spring15_a25ns_DMJetsVector_Mphi-10000_Mchi-50_gSM-1p0_gDM-1p0',  help='sample')
aparser.add_argument('-proc' ,'--proc'  ,action='store' ,dest='proc',default='801',  help='800,801,805,806 => V,A,S,P')
aparser.add_argument('-med'  ,'--med'   ,action='store' ,dest='med' ,default='500',  help='med mass')
aparser.add_argument('-dm'   ,'--dm'    ,action='store' ,dest='dm'  ,default='1',    help='dm mass')
aparser.add_argument('-gq'   ,'--gq'    ,action='store' ,dest='gq'  ,default='1',    help='gq')
aparser.add_argument('-list' ,'--list'  ,action='store_true',dest='list'  ,  help='list everything')
options = aparser.parse_args()

sumweights= 0
sumentries= 0
sumxs     = 0

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
basedir='eos/cms/store/cmst3/group/monojet/mc/model3_v2/'

def computeXS(med,dm,gq,proc):
    global sumweights,sumxs,sumentries
    infile='%s/MonoTop_%s_%s_%s_1.0_%s.root' % (basedir,med,dm,gq,proc)
    #print "root://eoscms//%s" % (infile)
    print basedir,infile
    lFile = r.TFile().Open("root://eoscms//%s" % (infile))
    lTree = lFile.Get("Events")
    lWHist = r.TH1F("med_"+med+"_"+gq+"_proc_"+proc,"med_"+med+"_"+gq+"_proc_"+proc,20,0,1200)
    lXHist = r.TH1F("X","X",1,-100000,10000000)
    lZHist = r.TH1F("Z","Z",1,-100000,10000000)
    lTree.Draw("v_pt>>med_"+med+"_"+gq+"_proc_"+proc,"xs2*(top1pt > 0)")
    lTree.Draw("v_pt>>Z","xs2*(top1pt > 0)")
    lTree.Draw("v_pt>>X","xs2*(top1pt > 300)")
    #print sumxs,sumweights,sumentries
    sumweights += lZHist.Integral()
    sumxs      += lXHist.Integral()
    sumentries += lTree.GetEntries()
    lWHist.Scale(1./lTree.GetEntries())
    lWHist.SetDirectory(0)
    lAFile       = r.TFile("med_"+med+"_"+dm+"_"+gq+"_proc"+proc+".root","RECREATE")
    lAFile.cd()
    lWHist.Write()
    
if options.list: 
    command = '%s ls %s | grep dijet | grep zprime5 | sed "s@_@ @g" | awk \'{print "./xsdj.py --med "$2" --dm "$3" --gq "$4" --proc "$5}\' | uniq' % (eos,basedir)
    exists = commands.getoutput(command)
    for line in exists.splitlines():
        print line
    quit()

computeXS(options.med,options.dm,options.gq,options.proc)
    
print options.proc,"-",options.med,"-",options.dm,"-",options.gq,"XS:",sumweights/sumentries,"XS (Pt > 300):",sumxs/sumentries
