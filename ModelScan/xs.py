#! /usr/bin/env python

import ROOT as r
import argparse,commands,os

aparser = argparse.ArgumentParser(description='Process benchmarks.')
#aparser.add_argument('-sample'  ,'--sample'    ,action='store' ,dest='sample' ,default='Spring15_a25ns_DMJetsVector_Mphi-10000_Mchi-50_gSM-1p0_gDM-1p0',  help='sample')
aparser.add_argument('-proc' ,'--proc'  ,action='store' ,dest='proc',default='801',  help='800,801,805,806 => V,A,S,P')
aparser.add_argument('-med'  ,'--med'   ,action='store' ,dest='med' ,default='500',  help='med mass')
aparser.add_argument('-dm'   ,'--dm'    ,action='store' ,dest='dm'  ,default='10',   help='dm mass')
aparser.add_argument('-gq'   ,'--gq'    ,action='store' ,dest='gq'  ,default='1',    help='gq')
aparser.add_argument('-vid'  ,'--vid'   ,action='store' ,dest='vid' ,default=0,      help='boson id (0,23,24)')
aparser.add_argument('-list' ,'--list'  ,action='store_true',dest='list'  ,  help='list everything')
options = aparser.parse_args()

sumweights= 0
sumentries= 0
sumxs     = 0

eos='/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
basedir='eos/cms/store/cmst3/group/monojet/mc/model3/'
basedirmj='eos/cms/store/cmst3/group/monojet/mc/model3_v2/'

def getXS(iMed,iId,basedir='/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_3_3/src/genproductions/bin/JHUGen/'):
    lFile  = r.TFile(basedir+'/patches/WZXS.root')
    label="ZH"
    if int(iId) == 24:
       label="WH"
    lG     = lFile.Get(label)
    lScale = lFile.Get("scaleUp")
    lBR    = lFile.Get("BRbb")
    if iMed > 500:
       lBR    = lFile.Get("BRtt")
    
    scale=int(iMed)+91+15 # 15 is an approximation of the extra energy based on matching xsections at 125                                                                                                   
    if int(iId) == 24:
       scale=int(iMed)+80+15
    #Correct for the BR to fermions assuming Scalar decays to bosons                                                                                                                                       
    lBaseMass=4.2
    if iMed > 500:
       lBaseMass=172.5
    BRCorr = min(lBR.Eval(iMed)*246.*246./lBaseMass/lBaseMass,1.)
    print BRCorr,lG.Eval(iMed),lScale
    return lG.Eval(iMed)*lScale.Eval(scale)*BRCorr

def compute(infile):
    global sumweights,sumxs,sumentries
    #print "root://eoscms//%s" % (infile)
    lFile = r.TFile().Open("root://eoscms//%s" % (infile))
    lTree = lFile.Get("Events")
    lWHist = r.TH1F("W","W",1,-100000,10000000)
    lXHist = r.TH1F("X","X",1,-100000,10000000)
    lTree.Draw("Info.nPU>>W","GenEvtInfo.weight")
    lTree.Draw("Info.nPU>>X","GenEvtInfo.xs")
    #print sumxs,sumweights,sumentries
    sumxs      += lXHist.Integral()
    sumweights += lWHist.Integral()
    sumentries += lTree.GetEntries()

def search(dirname):
    global count
    global basecount
    print 'dir',dirname
    dirSearch = '%s ls %s' %(eos,dirname)
    exists = commands.getoutput(dirSearch)
    for label in exists.splitlines():
        if label.find('log') > 0 or label == 'failed':
            continue
        if label.find('.root') > 0:
            compute(dirname+'/'+label)
            continue
        search('%s/%s' % (dirname,label))


#search( 'eos/cms/store/cmst3/group/monojet/production/05/%s' % options.sample)

def computeXS(med,dm,gq,proc):
    global sumweights,sumxs,sumentries
    gdm='1.0'
    if float(gq) == 1:
        gq = '1.0'
    else:
        gq = '0.25'
    infile='%s/MonoJ_%s_%s_%s_%s_%s.root' % (basedirmj,med,dm,gq,gdm,proc)
    #print "root://eoscms//%s" % (infile)
    print "root://eoscms//%s" % (infile)
    lFile = r.TFile().Open("root://eoscms//%s" % (infile))
    lTree = lFile.Get("Events")
    lWHist = r.TH1F("W","W",1,-100000,10000000)
    lXHist = r.TH1F("X","X",1,-100000,10000000)
    lTree.Draw("v_pt>>W","evtweight*(v_pt > 0)")
    lTree.Draw("v_pt>>X","evtweight*(v_pt > 200)")
    #print sumxs,sumweights,sumentries
    sumweights += lWHist.Integral()
    sumxs      += lXHist.Integral()
    sumentries += lTree.GetEntries()

def computeXSV(med,dm,gq,proc,iId):
    global sumweights,sumxs,sumentries
    infile='%s/MonoV_%s_%s_%s_%s.root' % (basedir,med,dm,gq,proc)
    #print "root://eoscms//%s" % (infile)
    lFile = r.TFile().Open("root://eoscms//%s" % (infile))
    lTree = lFile.Get("Events")
    lWHist = r.TH1F("W","W",1,-100000,10000000)
    lXHist = r.TH1F("X","X",1,-100000,10000000)
    bosonid="(abs(v_id) == "+str(iId)+")"
    weight1="xs"
    if int(proc) < 802:
         weight1=weight1+"2"
    weight1+="*"
    lTree.Draw("v_pt>>W",weight1+"(v_pt > 0)*"+bosonid)
    lTree.Draw("v_pt>>X",weight1+"(v_pt > 200)*"+bosonid)
    #print sumxs,sumweights,sumentries
    xs=1
    if int(proc) > 802:
        xs=getXS(float(med),iId)
    elif int(iId) == 23:
        xs=float(lTree.GetEntries(bosonid))/float(lTree.GetEntries())
    sumweights += lWHist.Integral()*xs
    sumxs      += lXHist.Integral()*xs
    sumentries += lTree.GetEntries(bosonid)

if options.list: 
    command = '%s ls eos/cms/store/cmst3/group/monojet/mc/model3/ | sed "s@_@ @g" | awk \'{print "mMed="$2" mDM="$3}\' | uniq' % eos
    if options.vid > 0:
        command = '%s ls eos/cms/store/cmst3/group/monojet/mc/model3/ | grep MonoV | sed "s@_@ @g" | awk \'{print "mMed="$2" mDM="$3}\' | uniq' % eos
    exists = commands.getoutput(command)
    for line in exists.splitlines():
        print line
    quit()

if int(options.vid) == 0:
    computeXS(options.med,options.dm,options.gq,options.proc)

if int(options.vid) > 0:
    computeXSV(options.med,options.dm,options.gq,options.proc,options.vid)
    
print options.proc,"-",options.vid,"-",options.med,"-",options.dm,"-",options.gq,"XS (Met > 0):",sumweights/sumentries,"XS (Met > 200):",sumxs/sumentries
