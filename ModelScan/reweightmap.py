#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from array import array

#Available samples
samples = { 
    'ggH125_signal'           :[0,805,125,    1],  # Ntuple  : [Final State,Proc,med,DM]
    'VBFH125_signal'          :[1,805,125,    1],
    'WH125_signal'            :[2,805,125,    1],   
    'ZH125_signal'            :[3,805,125,    1],
    'ggH200_signal'           :[0,805,200,    1],
    'VBFH200_signal'          :[1,805,200,    1],
    'WH200_signal'            :[2,805,200,    1],
    'ZH200_signal'            :[3,805,200,    1],
    'ggH300_signal'           :[0,805,300,    1],
    'VBFH300_signal'          :[1,805,300,    1],
    'WH300_signal'            :[2,805,300,    1],
    'ZH300_signal'            :[3,805,300,    1],
    'ggH400_signal'           :[0,805,400,    1],
    'VBFH400_signal'          :[1,805,400,    1],
    'WH400_signal'            :[2,805,400,    1],
    'ZH400_signal'            :[3,805,400,    1],
    'WDM1_D1_xip1_signal'     :[2,800,  1,    1],
    'ZDM1_D1_xip1_signal'     :[3,800,  1,    1],
    'WDM1000_D1_xip1_signal'  :[2,800,1000,1000],
    'ZDM1000_D1_xip1_signal'  :[3,800,1000,1000],
    'MJDM0p1_C1_signal'       :[0,800,1000, 0.1],
    'MJDM1_C1_signal'         :[0,800,1000,   1],
    'MJDM10_C1_signal'        :[0,800,1000,  10],
    'MJDM200_C1_signal'       :[0,800,1000, 200],
    'MJDM400_C1_signal'       :[0,800,1000, 400],
    'MJDM700_C1_signal'       :[0,800,1000, 700],
    'MJDM0p1_C3_signal'       :[0,800,1000, 0.1],
    'MJDM1_C3_signal'         :[0,800,1000,   1],
    'MJDM100_C3_signal'       :[0,800,1000, 100],
    'MJDM200_C3_signal'       :[0,800,1000, 200],
    'MJDM300_C3_signal'       :[0,800,1000, 300],
    'MJDM400_C3_signal'       :[0,800,1000, 400],
    'MJDM700_C3_signal'       :[0,800,1000, 700],
    'MJDM1_C5_signal'         :[0,800,1000,   1],
    'MJDM100_C5_signal'       :[0,800,1000, 100],
    'MJDM400_C5_signal'       :[0,800,1000, 400],
    'MJDM700_C5_signal'       :[0,800,1000, 700],
    'MJDM10_PS125_signal'     :[0,806,125,   10],
    'MJDM10_S125_signal'      :[0,805,125,   10]
}
def filtered(iSamples,iEntry,iVal):
    oSamples = {}
    tSamples = iSamples.keys()
    for sample in tSamples:
        entry = iSamples[sample]
        if entry[iEntry] == iVal:
            oSamples[sample]=entry    
    return oSamples

def offshell(iSamples,iOffShell):
    oSamples = {}
    tSamples = iSamples.keys()
    for sample in tSamples:
        entry = iSamples[sample]
        if entry[3] > entry[2]*0.5 and iOffShell:
            oSamples[sample]=entry    
        if entry[3] < entry[2]*0.5 and not iOffShell:
            oSamples[sample]=entry    
    return oSamples

#Nearest using Price is right rules (still debating this)
def nearest(iSamples,iEntry,iVal):
    #!!!Note assumes things are sorted by mediator mass
    baseVal=-1
    #Find nearest Val wit PIR Rules
    for sample in tSamples:
        entry = iSamples[sample]
        if abs(entry[iVal]-iVal) < abs(baseVal-iVal) or (baseVal-iVal < 0 and entry[iVal]-iVal > 0) : #2nd bit is POR rules
            baseVal=entry[iVal]
    return filtered(iSamples,iEntry,baseVal)

#Find the tree that is kinematic closest before reweighting
def obtainbase(iId,dm,med,width,gq,gdm,proc,hinv):
    #Step 1 Map Get all process with the right decay
    dDecay = filtered(samples,0,iId)
    print "Found:",len(dDecay),dDecay

    #Step 2 filter by process
    dProcess = filtered(dDecay,1,proc)
    #Merge Pseudoscalar with Scalar
    if len(dProcess) == 0 and proc == 806:
        process = filtered(dDecay,1,805)
    #Merge Vector/Axial and all flavors with Vector
    if len(dProcess) == 0 and (proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821):
        process = filtered(dDecay,1,800)
    if len(dProcess) == 0:
        print "Process not found!!!!",proc,iId
        output={'H125_Gen.root','ggH125_signal'}
        return output
    
    isExact = True
    #Step 3 filter by offshell or on shell
    if dm > med:
        dMass = offshell(dProcess,True)
    if len(dMass) == 0: 
        isExact = False
    if dm < med or len(dMass) == 0: #Default to onshell if ti fails
        dMass = offshell(dProcess,False)
    
    #Step 4 find the nearest Mediator
    dMed = filtered(dMass,2,med)
    if len(dMed) == 0: 
        isExact = False
    dMed = nearest(dMass,2,med)

    #Step 5 find the nearest DM candidate
    final = nearest(dMed,3,mass)
    if len(final) > 1 : 
        print "Ambiguous options",final
    output={final.keys()[0]+'.root',final.keys()[0]}
    if isExact:
        output[0]=''
    return output
