"""prov-query-generator.py: A tailor PROV-O query generator for PROV-O datasets

Usage: prov-query-generator.py
"""

import os, os.path
import sys
import re
import unittest
import logging
import httplib
import urllib
import time
import StringIO
import codecs
import csv


try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

def sparql(path, query):
    params = urllib.urlencode({"query": query})
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "application/sparql-results+json"}
    conn = httplib.HTTPConnection("www.open-biomed.org.uk")
    conn.request('POST', path, params, headers)
    res = conn.getresponse()
    if (res.status != 200):
        print res.status
        print res.reason
        print res.read()
        conn.close()
        return None
    else:
        resultSet = json.load(res)
        conn.close()
        return resultSet



### produce a data summary for a PROV-O dataset
### Currently we use the ProLOD++ app for this: https://www.hpi.uni-potsdam.de/naumann/sites/prolod++/app.html
### For the moment, the profile results are hard-coded. We will work with ProvLOD++ team to revise this

def prolod (g):
    
    profilename = '/Users/zhaoj/workspace/ProvQ/data/taverna-profile.csv'
    
    reader = csv.reader(open(profilename, "rU"), delimiter=',')

    #skip the first row
    reader.next()
    
    associations = {}
    
    for row in reader:
        condition = row[0]
        consequence = row[1]
        confidence = row[3]
        
        if (confidence > 0.9):
        
            if (associations.has_key(condition)):
                associatedProperties = associations.get(condition)
                if (associatedProperties.count(consequence)==0):
                    associatedProperties.append(consequence)
            else:
                associations[condition]= [consequence]

    #print associations

    return associations

def queryGenerator (g):
    
    properties = ["prov:used", "prov:wasGeneratedBy", "prov:wasDerivedFrom", "prov:startedAtTime", "prov:endedAtTime", "prov:wasAssociatedWith", "prov:wasAttributedTo", "prov:wasInformedBy", "prov:actedOnBehalfOf"]
    
    print "==== Query Generation For Starting Point Terms===="

    
    associations = prolod(g)
    
    for p in properties:
        
        seedQuery = "No queries for the property: " + p
        
        if (associations.has_key(p)):
            
            seedQuery = "select distinct * where {?s " + p + " ?o; "
        
            associatedProperties = associations.get(p)
            
            count = 0
        
            for item in range(len(associatedProperties)-1):
                
                count = count + 1
            
                seedQuery = seedQuery + associatedProperties[item] + " ?o" + str(count) + "; "
            
            count = count + 1
    
            seedQuery = seedQuery + associatedProperties[len(associatedProperties)-1] + " ?o" + str(count) + ".} "

        print seedQuery
    
    return


def queryGeneratorQualified (g):
    
    properties = ["prov:entity", "prov:agent", "prov:activity", "prov:hadRole", "prov:hadPlan"]
    
    print "==== Query Generation For Qualified Terms===="

    associations = prolod(g)
    
    for p in properties:
        
        seedQuery = "No queries for the property: " + p
        
        if (associations.has_key(p)):
            
            seedQuery = "select distinct * where {?s ?p [" + p + " ?o; "
            
            associatedProperties = associations.get(p)
            
            count = 0
            
            for item in range(len(associatedProperties)-1):
                
                count = count + 1
                
                seedQuery = seedQuery + associatedProperties[item] + " ?o" + str(count) + "; "
            
            count = count + 1
            
            seedQuery = seedQuery + associatedProperties[len(associatedProperties)-1] + " ?o" + str(count) + "] } "
        
        print seedQuery
    
    return



def provq(filename):
    
    print "==== Query Generation For: " + filename + "===="
                    
    queryGenerator(filename)

    queryGeneratorQualified(filename)
    
    return


def main():
                    
    #endpointpath = ["ta-provenance", "csiro", "obiama"]
    
    endpointpath = ["ta-provenance"]
                    
    endpointhost = "http://www.open-biomed.org.uk/sparql/endpoint-lax/"
    
    for arg in endpointpath:
        provq(arg)

if __name__ == "__main__":
    main()
