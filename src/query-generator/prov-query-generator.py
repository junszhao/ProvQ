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
from rdflib import URIRef, Graph
import cluster as cluster

try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json


def profiling (filename):
    analysis = cluster.AssociationMiner(filename)
        
    analysis.analyse()
    
    associations = analysis.associations

    return associations


def queryGenerator (associations):
    
    properties = ["http://www.w3.org/ns/prov#used", "http://www.w3.org/ns/prov#wasGeneratedBy", "http://www.w3.org/ns/prov#wasDerivedFrom", "http://www.w3.org/ns/prov#startedAtTime", "http://www.w3.org/ns/prov#endedAtTime", "http://www.w3.org/ns/prov#wasAssociatedWith", "http://www.w3.org/ns/prov#wasAttributedTo", "http://www.w3.org/ns/prov#wasInformedBy", "http://www.w3.org/ns/prov#actedOnBehalfOf"]
    
    print "==== Query Generation For Starting Point Terms===="
    
    queries = []
    
    for p in properties:
        
        seedQuery = "No queries for the property: " + p
        
        p = URIRef(p)
        
        if (p in associations):
            
            seedQuery = "select distinct ?s where {?s <" + p + "> ?o.\n "
        
            associatedProperties = associations[p]
    
            count = 0
        
            for key in associatedProperties:
                count = count + 1
                
                if (count < len(associatedProperties)):
                    seedQuery = seedQuery + "optional {?s\t<"+key + "> ?o" + str(count) + ".}\n "
                else:
                    seedQuery = seedQuery + "optional {?s\t<"+key + "> ?o" + str(count) + ".} }"
            queries.append(seedQuery)
        
        print seedQuery
        
        

    return queries


def queryGeneratorQualified (associations):
    
    properties = ["http://www.w3.org/ns/prov#entity", "http://www.w3.org/ns/prov#agent", "http://www.w3.org/ns/prov#activity", "http://www.w3.org/ns/prov#hadRole", "http://www.w3.org/ns/prov#hadPlan"]
    
    print "==== Query Generation For Qualified Terms===="
    
    queries = []

    for p in properties:
        
        seedQuery = "No queries for the property: " + p
        
        p = URIRef(p)
        
        if (p in associations):
            
            seedQuery = "select distinct ?s where {?s1 ?p ?s . ?s <" + p + "> ?o.\n "
            
            associatedProperties = associations[p]
            
            count = 0
            
            for key in associatedProperties:
                count = count + 1
                
                if (count < len(associatedProperties)):
                    seedQuery = seedQuery + "optional {?s <"+key + "> ?o" + str(count) + ".}\n "
                else:
                    seedQuery = seedQuery + "optional {?s <"+key + "> ?o" + str(count) + ".} } "
            queries.append(seedQuery)
    
        print seedQuery
        
        

    return queries

def testcoverage(queries,filename):
    g = Graph()
    g.parse(filename, format="nt")   
    querystring = "select distinct ?s where {?s ?p ?o}" 
    allSubj = g.query(querystring)
    unique = set()
    total = 0
    
    for row in allSubj:
        s = row['s']
        if s not in unique:
            total = total +1
    
    print total
    
    subjects = set()
    
    for q in queries:
        print "Query: " + q
        results = g.query(q)       
        for row in results:
            subject = row['s']
            if subject not in subjects:
                subjects.add(subject)                
    
    coverage = len(subjects)/float(total)
    print len(subjects)
    print coverage
    
    return

def testStms(queries,filename):
    g = Graph()
    g.parse(filename, format="nt")    
    allSubj = g.triples()
    unique = set()
    total = 0
    
    for s in allSubj:
        if s not in unique:
            total = total +1
    
    print total
    
    stms = set()
    
    for q in queries:
        print "Query: " + q
        results = g.query(q)       
        for row in results:
            stm = row[0]
            if stm not in stms:
                stms.add(stm)                
    
    coverage = len(stms)/float(total)
    print len(stms)
    print coverage
    
    return

def provq(filename):
    
    print "==== Query Generation For: " + filename + "===="
    
    associations = profiling(filename)
                    
    queries1 = queryGenerator(associations)

    queries2 = queryGeneratorQualified(associations)
    
    queries = queries1 + queries2
    
    testcoverage(queries,filename)
    #testStms(queries,filename)

    return


def main(argv):
    
    provq(argv)

if __name__ == "__main__":
    main(sys.argv[1])
