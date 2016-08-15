#! /usr/bin/env python
import commands,sys,os,subprocess,ROOT,numpy
from optparse import OptionParser
from array import array

#Available samples
samples = { 
    'tree_Vector_MonoJ0_300_80X.root'                : [0,800,300,     1],
    'tree_Vector_MonoJ300_1000_80X.root'           : [0,800,500,     1],
    'tree_Vector_MonoJ1000_80X.root'               : [0,800,1000,    1],
    'tree_Vector_MonoJoffshell_80X.root'           : [0,800,1,   10000],

    'tree_Axial_MonoJ0_300_80X.root'                 : [0,801,300,     1],
    'tree_Axial_MonoJ300_1000_80X.root'            : [0,801,500,     1],
    'tree_Axial_MonoJ1000_80X.root'                : [0,801,1000,    1],
    'tree_Axial_MonoJoffshell_80X.root'            : [0,801,1,   10000],

    'tree_Scalar_MonoJ0_300_80X.root'               : [0,805,300,     1],
    'tree_Scalar_MonoJ300_1000_80X.root'           : [0,805,500,     1],
    'tree_Scalar_MonoJ1000_80X.root'               : [0,805,1000,    1],
    'tree_Scalar_MonoJ300_1000_80X.root'           : [0,805,1,   10000],

    'tree_Pseudoscalar_MonoJ0_300_80X.root'          : [0,806,300,     1],
    'tree_Pseudoscalar_MonoJ300_1000_80X.root'     : [0,806,500,     1],
    'tree_Pseudoscalar_MonoJ1000_80X.root'         : [0,806,1000,    1],
    'tree_Pseudoscalar_MonoJoffshell_80X.root'     : [0,806,1,   10000],

    'tree_Vector_MonoZ300.root'                : [23,800,300,     1],
    'tree_Vector_MonoZ300_1000.root'           : [23,800,500,     1],
    'tree_Vector_MonoZ1000.root'               : [23,800,1000,    1],
    'tree_Vector_MonoZoffshell.root'           : [23,800,1,   10000],

    'tree_Axial_MonoZ300.root'                 : [23,801,300,     1],
    'tree_Axial_MonoZ300_1000.root'            : [23,801,700,     1],
    'tree_Axial_MonoZ1000.root'                : [23,801,1500,    1],
    'tree_Axial_MonoZoffshell.root'            : [23,801,1,   10000],

    'tree_Scalar_MonoZ300.root'                : [23,805,300,     1],
    'tree_Scalar_MonoZ300_1000.root'           : [23,805,700,     1],
    #'tree_Scalar_MonoJ1000.root'               : [23,805,1000,    1],
    'tree_Scalar_MonoZoffshell.root'           : [23,805,1,   10000],

    'tree_Pseudoscalar_MonoZ300.root'          : [23,806,300,     1],
    'tree_Pseudoscalar_MonoZ300_1000.root'     : [23,806,700,     1],
    'tree_Pseudoscalar_MonoZ1000.root'         : [23,806,1500,    1],
    'tree_Pseudoscalar_MonoZoffshell.root'     : [23,806,1,   10000],

    'tree_Vector_MonoW300.root'                : [24,800,300,     1],
    'tree_Vector_MonoW300_1000.root'           : [24,800,700,     1],
    'tree_Vector_MonoW1000.root'               : [24,800,1500,    1],
    'tree_Vector_MonoWoffshell.root'           : [24,800,1,   10000],

    'tree_Axial_MonoW300.root'                 : [24,801,300,     1],
    'tree_Axial_MonoW300_1000.root'            : [24,801,700,     1],
    'tree_Axial_MonoW1000.root'                : [24,801,1500,    1],
    'tree_Axial_MonoWoffshell.root'            : [24,801,1,   10000],

    'tree_Scalar_MonoW300.root'                : [24,805,300,     1],
    'tree_Scalar_MonoW300_1000.root'           : [24,805,700,     1],
    'tree_Scalar_MonoW1000.root'               : [24,805,1500,    1],
    'tree_Scalar_MonoWoffshell.root'           : [24,805,1,   10000],

    'tree_Pseudoscalar_MonoW300.root'          : [24,806,300,     1],
    'tree_Pseudoscalar_MonoW300_1000.root'     : [24,806,700,     1],
    'tree_Pseudoscalar_MonoW1000.root'         : [24,806,1500,    1],
    'tree_Pseudoscalar_MonoWoffshell.root'     : [24,806,1,   10000],

    'tree_HiggsInv_VBF150.root'                : [ 1,805,150,     1],
    'tree_HiggsInv_VBF150_200.root'            : [ 1,805,200,     1],
    'tree_HiggsInv_VBF200_300.root'            : [ 1,805,300,     1],
    'tree_HiggsInv_VBF300_400.root'            : [ 1,805,400,     1],
    'tree_HiggsInv_VBF400_500.root'            : [ 1,805,500,     1],
    'tree_HiggsInv_VBF500.root'                : [ 1,805,550,     1]

#    'tree_Axial_MonoJ.root'                    : [0,801,10000, 50],
#    'tree_Scalar_MonoJ.root'                   : [0,805,10000, 50],
#    'tree_Pseudoscalar_MonoJ.root'             : [0,806,10000, 50],
#    'tree_Vector_MonoW.root'                   : [24,800,10000, 50],
#    'tree_Axial_MonoW.root'                    : [24,801,10000, 50],
#    'tree_Scalar_MonoW.root'                   : [24,805,10000, 50],
#    'tree_Pseudoscalar_MonoW.root'             : [24,806,10000, 50],
#    'tree_Vector_MonoZ.root'                   : [23,800,10000, 50],
#    'tree_Axial_MonoZ.root'                    : [23,801,10000, 50],
#    'tree_Scalar_MonoZ.root'                   : [23,805,10000, 50],
#    'tree_Pseudoscalar_MonoZ.root'             : [23,806,10000, 50],
}

samplesz = { 
    'tree_Vector_MonoZLL100.root'                : [23,800,100,     1],
    'tree_Vector_MonoZLL100_300.root'            : [23,800,250,     1],
    'tree_Vector_MonoZLL300_1000.root'           : [23,800,500,     1],
    'tree_Vector_MonoZLL1000.root'               : [23,800,1000,    1],
    'tree_Vector_MonoZLLoffshell.root'           : [23,800,1,   10000],
    'tree_Axial_MonoZLL100.root'                 : [23,801,100,     1],
    'tree_Axial_MonoZLL100_300.root'             : [23,801,250,     1],
    'tree_Axial_MonoZLL300_1000.root'            : [23,801,500,     1],
    'tree_Axial_MonoZLL1000.root'                : [23,801,1000,    1],
    'tree_Axial_MonoZLLoffshell.root'            : [23,801,1,   10000],
}
samplestop = { 
'monotop-nr-v3-100-100_med-100_dm-100.root'                  : [6,800,100,   100],
'monotop-nr-v3-100-10_med-100_dm-10.root'                    : [6,800,100,   10],
'monotop-nr-v3-100-200_med-100_dm-200.root'                  : [6,800,100,   200],
'monotop-nr-v3-100-500_med-100_dm-500.root'                  : [6,800,100,   500],
'monotop-nr-v3-100-50_med-100_dm-50.root'                    : [6,800,100,   50],
'monotop-nr-v3-1100-100_med-1100_dm-100.root'                : [6,800,1100,   100],
'monotop-nr-v3-1100-10_med-1100_dm-10.root'                  : [6,800,1100,   10],
'monotop-nr-v3-1100-200_med-1100_dm-200.root'                : [6,800,1100,   200],
'monotop-nr-v3-1100-500_med-1100_dm-500.root'                : [6,800,1100,   500],
'monotop-nr-v3-1100-50_med-1100_dm-50.root'                  : [6,800,1100,   50],
'monotop-nr-v3-1300-1000_med-1300_dm-1000.root'              : [6,800,1300,   1000],
'monotop-nr-v3-1300-100_med-1300_dm-100.root'                : [6,800,1300,   100],
'monotop-nr-v3-1300-10_med-1300_dm-10.root'                  : [6,800,1300,   10],
'monotop-nr-v3-1300-200_med-1300_dm-200.root'                : [6,800,1300,   200],
'monotop-nr-v3-1300-500_med-1300_dm-500.root'                : [6,800,1300,   500],
'monotop-nr-v3-1300-50_med-1300_dm-50.root'                  : [6,800,1300,   50],
'monotop-nr-v3-150-100_med-150_dm-100.root'                  : [6,800,150,   100],
'monotop-nr-v3-150-10_med-150_dm-10.root'                    : [6,800,150,   10],
'monotop-nr-v3-150-200_med-150_dm-200.root'                  : [6,800,150,   200],
'monotop-nr-v3-150-500_med-150_dm-500.root'                  : [6,800,150,   500],
'monotop-nr-v3-150-50_med-150_dm-50.root'                    : [6,800,150,   50],
'monotop-nr-v3-1500-1000_med-1500_dm-1000.root'              : [6,800,1500,   1000],
'monotop-nr-v3-1500-100_med-1500_dm-100.root'                : [6,800,1500,   100],
'monotop-nr-v3-1500-10_med-1500_dm-10.root'                  : [6,800,1500,   10],
'monotop-nr-v3-1500-200_med-1500_dm-200.root'                : [6,800,1500,   200],
'monotop-nr-v3-1500-500_med-1500_dm-500.root'                : [6,800,1500,   500],
'monotop-nr-v3-1500-50_med-1500_dm-50.root'                  : [6,800,1500,   50],
'monotop-nr-v3-1700-1000_med-1700_dm-1000.root'              : [6,800,1700,   1000],
'monotop-nr-v3-1700-100_med-1700_dm-100.root'                : [6,800,1700,   100],
'monotop-nr-v3-1700-10_med-1700_dm-10.root'                  : [6,800,1700,   10],
'monotop-nr-v3-1700-200_med-1700_dm-200.root'                : [6,800,1700,   200],
'monotop-nr-v3-1700-500_med-1700_dm-500.root'                : [6,800,1700,   500],
'monotop-nr-v3-1700-50_med-1700_dm-50.root'                  : [6,800,1700,   50],
'monotop-nr-v3-1900-1000_med-1900_dm-1000.root'              : [6,800,1900,   1000],
'monotop-nr-v3-1900-100_med-1900_dm-100.root'                : [6,800,1900,   100],
'monotop-nr-v3-1900-10_med-1900_dm-10.root'                  : [6,800,1900,   10],
'monotop-nr-v3-1900-200_med-1900_dm-200.root'                : [6,800,1900,   200],
'monotop-nr-v3-1900-500_med-1900_dm-500.root'                : [6,800,1900,   500],
'monotop-nr-v3-1900-50_med-1900_dm-50.root'                  : [6,800,1900,   50],
'monotop-nr-v3-200-100_med-200_dm-100.root'                  : [6,800,200,   100],
'monotop-nr-v3-200-10_med-200_dm-10.root'                    : [6,800,200,   10],
'monotop-nr-v3-200-200_med-200_dm-200.root'                  : [6,800,200,   200],
'monotop-nr-v3-200-500_med-200_dm-500.root'                  : [6,800,200,   500],
'monotop-nr-v3-200-50_med-200_dm-50.root'                    : [6,800,200,   50],
'monotop-nr-v3-2100-1000_med-2100_dm-1000.root'              : [6,800,2100,   1000],
'monotop-nr-v3-2100-100_med-2100_dm-100.root'                : [6,800,2100,   100],
'monotop-nr-v3-2100-10_med-2100_dm-10.root'                  : [6,800,2100,   10],
'monotop-nr-v3-2100-200_med-2100_dm-200.root'                : [6,800,2100,   200],
'monotop-nr-v3-2100-500_med-2100_dm-500.root'                : [6,800,2100,   500],
'monotop-nr-v3-2100-50_med-2100_dm-50.root'                  : [6,800,2100,   50],
'monotop-nr-v3-300-100_med-300_dm-100.root'                  : [6,800,300,   100],
'monotop-nr-v3-300-10_med-300_dm-10.root'                    : [6,800,300,   10],
'monotop-nr-v3-300-200_med-300_dm-200.root'                  : [6,800,300,   200],
'monotop-nr-v3-300-500_med-300_dm-500.root'                  : [6,800,300,   500],
'monotop-nr-v3-300-50_med-300_dm-50.root'                    : [6,800,300,   50],
'monotop-nr-v3-50-100_med-50_dm-100.root'                    : [6,800,50,   100],
'monotop-nr-v3-50-10_med-50_dm-10.root'                      : [6,800,50,   10],
'monotop-nr-v3-50-200_med-50_dm-200.root'                    : [6,800,50,   200],
'monotop-nr-v3-50-500_med-50_dm-500.root'                    : [6,800,50,   500],
'monotop-nr-v3-50-50_med-50_dm-50.root'                      : [6,800,50,   50],
'monotop-nr-v3-500-100_med-500_dm-100.root'                  : [6,800,500,   100],
'monotop-nr-v3-500-10_med-500_dm-10.root'                    : [6,800,500,   10],
'monotop-nr-v3-500-200_med-500_dm-200.root'                  : [6,800,500,   200],
'monotop-nr-v3-500-500_med-500_dm-500.root'                  : [6,800,500,   500],
'monotop-nr-v3-500-50_med-500_dm-50.root'                    : [6,800,500,   50],
'monotop-nr-v3-700-100_med-700_dm-100.root'                  : [6,800,700,   100],
'monotop-nr-v3-700-10_med-700_dm-10.root'                    : [6,800,700,   10],
'monotop-nr-v3-700-200_med-700_dm-200.root'                  : [6,800,700,   200],
'monotop-nr-v3-700-500_med-700_dm-500.root'                  : [6,800,700,   500],
'monotop-nr-v3-700-50_med-700_dm-50.root'                    : [6,800,700,   50],
'monotop-nr-v3-900-100_med-900_dm-100.root'                  : [6,800,900,   100],
'monotop-nr-v3-900-10_med-900_dm-10.root'                    : [6,800,900,   10],
'monotop-nr-v3-900-200_med-900_dm-200.root'                  : [6,800,900,   200],
'monotop-nr-v3-900-500_med-900_dm-500.root'                  : [6,800,900,   500],
'monotop-nr-v3-900-50_med-900_dm-50.root'                    : [6,800,900,   50],
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
        if entry[3] < entry[2]*0.501 and not iOffShell:
            oSamples[sample]=entry    
    return oSamples

#Nearest using Price is right rules (still debating this)
def nearest(iSamples,iEntry,iVal):
    #!!!Note assumes things are sorted by mediator mass
    tSamples = iSamples.keys() 
    baseVal=-1
    #Find nearest Val wit PIR Rules
    for sample in tSamples:
        entry = iSamples[sample]
        if abs(entry[iEntry]-iVal) < abs(baseVal-iVal) or (baseVal-iVal < 0 and entry[iEntry]-iVal > 0) : #2nd bit is POR rules
            baseVal=entry[iEntry]
    return filtered(iSamples,iEntry,baseVal)

def convert(iName):
    return 'tree'
    lName=iName.replace("Vector"      ,"V")
    lName=lName.replace("Axial"       ,"A")
    lName=lName.replace("Scalar"      ,"S")
    lName=lName.replace("Pseudoscalar","P")
    lName=lName.replace("Mchi-","")
    lName=lName.replace("Mphi-","")
    lName=lName.replace("_0.root_0","")
    return lName+"_signal"

#Find the tree that is kinematic closest before reweighting
def obtainbase(iId,dm,med,proc,hinv):
    #Step 1 Map Get all process with the right decay
    dDecay = filtered(samples,0,iId)
    #Step 2 filter by process
    dProcess = filtered(dDecay,1,proc)
    #Merge Pseudoscalar with Scalar
    if len(dProcess) == 0 and proc == 806:
        dProcess = filtered(dDecay,1,805)
    #Merge Vector/Axial and all flavors with Vector
    if len(dProcess) == 0 and (proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821):
        dProcess = filtered(dDecay,1,800)
    #Just take whatever the hell we have for Mono-V
    if len(dProcess) == 0 and iId > 1:
        print "Mono-V Process missing"
        dProcess = filtered(dDecay,1,800)
    if len(dProcess) == 0:
        print "Process not found!!!!",proc,iId
        output=['H125_Gen.root','ggH125_signal']
        return output

    isExact = True
    #Step 3 filter by offshell or on shell
    dMass = offshell(dProcess,(dm > 0.5*med))
    if len(dMass) == 0: 
        isExact = False
    if dm < 10*med and len(dMass) == 0: #Default to onshell if ti fails
        dMass = offshell(dProcess,not (dm > 0.5*med))
    
    #Step 4 find the nearest Mediator
    dMed = filtered(dMass,2,med)
    if len(dMed) == 0: 
        isExact = False
        dMed = nearest(dMass,2,med)
    
    #Step 5 find the nearest DM candidate
    final = nearest(dMed,3,dm)
    if len(final) > 1 : 
        print "Ambiguous options",final

    print "final",final
    output=[final.keys()[0],convert(final.keys()[0])]
    #if isExact and hinv:
    #    output[0]=''
    return output


def obtainbasez(iId,dm,med,proc,hinv):
    #Step 1 Map Get all process with the right decay
    dDecay = filtered(samplesz,0,iId)
    #Step 2 filter by process
    dProcess = filtered(dDecay,1,proc)
    #Merge Pseudoscalar with Scalar
    if len(dProcess) == 0 and (proc == 806 or proc == 805):
        dProcess = filtered(dDecay,1,801)
    #Merge Vector/Axial and all flavors with Vector
    if len(dProcess) == 0 and (proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821):
        dProcess = filtered(dDecay,1,800)
    #Just take whatever the hell we have for Mono-V
    if len(dProcess) == 0 and iId > 1:
        print "Mono-V Process missing"
        dProcess = filtered(dDecay,1,800)
    if len(dProcess) == 0:
        print "Process not found!!!!",proc,iId
        output=['H125_Gen.root','ggH125_signal']
        return output

    isExact = True
    #Step 3 filter by offshell or on shell
    dMass = offshell(dProcess,(dm > 0.5*med))
    if len(dMass) == 0: 
        isExact = False
    if dm < 10*med and len(dMass) == 0: #Default to onshell if ti fails
        dMass = offshell(dProcess,not (dm > 0.5*med))
    
    #Step 4 find the nearest Mediator
    dMed = filtered(dMass,2,med)
    if len(dMed) == 0: 
        isExact = False
        dMed = nearest(dMass,2,med)
    
    #Step 5 find the nearest DM candidate
    final = nearest(dMed,3,dm)
    if len(final) > 1 : 
        print "Ambiguous options",final

    print "final",final
    output=[final.keys()[0],'events']
    #if isExact and hinv:
    #    output[0]=''
    return output

def obtainbasetop(iId,dm,med,proc,hinv):
    #Step 1 Map Get all process with the right decay
    dDecay = filtered(samplestop,0,iId)
    #Step 2 filter by process
    dProcess = filtered(dDecay,1,proc)
    #Merge Pseudoscalar with Scalar
    if len(dProcess) == 0 and (proc == 806 or proc == 805):
        dProcess = filtered(dDecay,1,801)
    #Merge Vector/Axial and all flavors with Vector
    if len(dProcess) == 0 and (proc == 801 or proc == 810 or proc == 811 or proc == 820 or proc == 821):
        dProcess = filtered(dDecay,1,800)
    #Just take whatever the hell we have for Mono-V
    if len(dProcess) == 0 and iId > 1:
        print "Mono-V Process missing"
        dProcess = filtered(dDecay,1,800)
    if len(dProcess) == 0:
        print "Process not found!!!!",proc,iId
        output=['H125_Gen.root','ggH125_signal']
        return output

    isExact = True
    #Step 3 filter by offshell or on shell
    dMass = offshell(dProcess,(dm > 0.5*med))
    if len(dMass) == 0: 
        isExact = False
    if dm < 10*med and len(dMass) == 0: #Default to onshell if ti fails
        dMass = offshell(dProcess,not (dm > 0.5*med))
    
    #Step 4 find the nearest Mediator
    dMed = filtered(dMass,2,med)
    if len(dMed) == 0: 
        isExact = False
        dMed = nearest(dMass,2,med)
    
    #Step 5 find the nearest DM candidate
    final = nearest(dMed,3,dm)
    if len(final) > 1 : 
        print "Ambiguous options",final

    print "final",final
    #output=[final.keys()[0],'Overwrite']
    output=[final.keys()[0],'events']
    #if isExact and hinv:
    #    output[0]=''
    return output

#parser = OptionParser()
#parser.add_option('--dm'   ,action='store',type='int',dest='dm'    ,default=10,  help='Dark Matter Mass')
#parser.add_option('--med'  ,action='store',type='int',dest='med'   ,default=2000,help='Mediator Mass')
#parser.add_option('--proc' ,action='store',type='int',dest='proc'  ,default=806, help='Process(800=V,801=A,805=S,806=P)')
#(options,args) = parser.parse_args()

#if __name__ == "__main__":
#   dm  =options.dm
#   med =options.med
#   proc=options.proc

#   for i0 in range(0,4):   
#       basetree,trees=obtainbase(i0,dm,med,proc)
#       print "Base:",basetree,"Run Tree",trees
