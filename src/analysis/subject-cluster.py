"""property-associatin.py: compute property associations by the number of unique subjects that associate them
    
    Usage: property-association.py
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
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF
import pprint


def createModel(filename):
    
    print "==== Compute property association for: " + filename + "===="
    
    g = Graph()
    g.parse(filename, format="nt")

    return g


def createSubjPredicateMatrix(g):
    
    querystring = "select distinct ?s ?p where {?s ?p ?o}"
    
    results = g.query(querystring)
    
    subjects = set()
    
    associations = {}
    
    for row in results:
        subject = row['s']
        property = row['p']
        if subject not in associations:
            associations[subject]=set()
            associations[subject].add(property)
        else:
            properties = associations[subject]
            if property not in properties:
                associations[subject].add(property)

#    print "we found " + str(len(associations)) + " subjects"

#    for key in associations.keys():
#        print "we found " + str(len(associations[key])) + " properties for subject " + key

#
#
#    for s in subjects:
#        ### create the index by subject to properties
#        
#        querystring = "select distinct ?p where {<"+s+"> ?p ?o}"
#        
#        results = g.query(querystring)
#        
#        properties = set()
#        
#        for row in results:
#            property = row['p']
#            if property not in properties:
#                properties.add(property)
#
#        print "we found " + str(len(properties)) + " properties for subject " + s
#    
#        associations[s]= properties


    return associations

def hashSubjects(associations,threshold):
    subjectDic = {}
    
    keys = associations.keys()
    
    for i in range(0,len(keys)):
        s1 = keys[i]
        sub1 = frozenset(associations[s1])
        
        for j in range(1,len(keys)-1):
            s2 = keys[j]
            sub2 = frozenset(associations[s2])
            
            if len(sub1)>=threshold and len(sub2)>=threshold:
                common = sub1.intersection(sub2)
                
                if len(common)>=threshold:
                    
                    dickey = hash(common)
                    
                    if dickey not in subjectDic:

                        subjectDic[dickey]=set()
                        subjectDic[dickey].add(s1)
                        subjectDic[dickey].add(s2)
                    else:
                        subjects = subjectDic[dickey]
                        if s1 not in subjects:
                            subjectDic[dickey].add(s1)
                        if s2 not in subjects:
                            subjectDic[dickey].add(s2)

    return subjectDic

def translate(subjectDic,g):

    keys = subjectDic.keys()
    
    translatedSubs = {}

    for i in range(0,len(keys)):
        print i
        key = keys[i]
        subjects = subjectDic[key]
        types = set()
        for s in subjects:
            results = g.objects(s,RDF.type)
            for type in results:
                if type not in types:
                    types.add(type)
        print "for hash " + str(key) + ", we have: "
        print types
        translatedSubs[key]=types

    return translatedSubs

def analyse(filename, threshold):

    g = createModel(filename)
    
    ### find all the unique subjects
    associations = createSubjPredicateMatrix(g)
    
    subjectDic = hashSubjects(associations,threshold)

    translate(subjectDic,g)

    return

def main():
    
    #filename = '/Users/zhaoj/workspace/ProvQ/data/ta-201402.nt'
#    filename = '/Users/zhaoj/workspace/ProvQ/data/workflowrun.provo.nt'
    filename = '/Users/zhaoj/workspace/ProvQ/data/workflowrun.all.nt'

    analyse(filename,3)

if __name__ == "__main__":
    main()