import os
import sys
import getopt
import subprocess

import PyXMCDA

from algGAMMAP import *

from optparse import OptionParser

def main(argv=None):
    
    if argv is None:
        argv = sys.argv
        
    parser = OptionParser()

    parser.add_option("-i", "--in", dest="in_dir")
    parser.add_option("-o", "--out", dest="out_dir")

    (options, args) = parser.parse_args(argv[1:])

    in_dir = options.in_dir
    out_dir = options.out_dir

    # Creating a list for error messages
    errorList = []

    if not os.path.isfile (in_dir+"/alternatives.xml"):
        errorList.append("alternatives.xml is missing")
    if not os.path.isfile (in_dir+"/relation.xml"):
        errorList.append("relation.xml is missing")
    if not os.path.isfile (in_dir+"/parameters.xml"):
        errorList.append("parameters.xml is missing")

    if not errorList:
        # We parse all the mandatory input files
        xmltree_alternatives = PyXMCDA.parseValidate(in_dir+"/alternatives.xml")
        xmltree_relation = PyXMCDA.parseValidate(in_dir+"/relation.xml")
        xmltree_parameters = PyXMCDA.parseValidate(in_dir+"/parameters.xml")
        
        # We check if all madatory input files are valid
        if xmltree_alternatives == None :
            errorList.append("alternatives.xml can't be validated.")
        if xmltree_relation == None :
            errorList.append("relation.xml can't be validated.")
        if xmltree_parameters == None :
            errorList.append("parameters.xml can't be validated.")
            
        if not errorList :

            alternativesId = PyXMCDA.getAlternativesID(xmltree_alternatives)
            alternativesRel = PyXMCDA.getAlternativesComparisons (xmltree_relation, alternativesId)
            relationMin = PyXMCDA.getParameterByName (xmltree_parameters, "min")
            relationMax = PyXMCDA.getParameterByName (xmltree_parameters, "max")
            relationCut = PyXMCDA.getParameterByName (xmltree_parameters, "cut")
            relationBipolar = PyXMCDA.getParameterByName (xmltree_parameters, "bipolar")

            if not alternativesId :
                errorList.append("No active alternatives found.")
            if not alternativesRel :
                errorList.append("Problems between relation and alternatives.")
            if relationMin is None:
                errorList.append("No \'min\' method parameter found")
            if relationMax is None:
                errorList.append("No \'max\' method parameter found")
            if relationCut is None:
                errorList.append("No \'cut\' method parameter found")
            if relationBipolar is None:
                errorList.append("No \'bipolar\' method parameter found")

        if not errorList :
            
            alg = algGAMMAP(alternativesId, alternativesRel, relationMin, relationMax, relationCut, relationBipolar)
            results = alg.Run()
            
            fo = open(out_dir+"/output.xml",'w')
            PyXMCDA.writeHeader(fo)
            fo.write('<alternativesAffectations>\n')
            for o in results:
                fo.write('\t<alternativeAffectation>\n\t\t<alternativeID>'+o+'</alternativeID>\n\t\t\t<categoryID>'+results[o]+'</categoryID>\n\t</alternativeAffectation>\n')
            fo.write('</alternativesAffectations>')
            PyXMCDA.writeFooter(fo)
            fo.close()
            
        # Creating log and error file, messages.xml
        fileMessages = open(out_dir+"/messages.xml", 'w')
        PyXMCDA.writeHeader (fileMessages)

        if not errorList :
            PyXMCDA.writeLogMessages (fileMessages, ["Execution ok"])
        else :
            PyXMCDA.writeErrorMessages (fileMessages, errorList)

        PyXMCDA.writeFooter(fileMessages)
        fileMessages.close()

if __name__ == "__main__":
    sys.exit(main())


            