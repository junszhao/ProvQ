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
import pprint


def createModel(filename):
    
    print "==== Compute property association for: " + filename + "===="
    
    g = Graph()
    g.parse(filename, format="nt")

    return g

def getUniquePredicates(g):

    ### find all the properties
    properties = g.predicates()
    keys = set()

    for p in properties:
        if p not in keys:
            keys.add(p)

    #print keys

    return keys

def getUniqueSubjects(triples):
    
    subjects = set()
    for triple in triples:
        subject = triple[0]
        
        if subject not in subjects:
            subjects.add(subject)

    return subjects


def mapTriples(triples):
    
    tripleMap = set()
    
    for triple in triples:
        tripleMap.add(triple)

    return tripleMap

def analyse(filename):

    g = createModel(filename)
    
    ### find all the unique properties
    properties = getUniquePredicates(g)
    
    ### compute the association
    
    associations = {}
    
    for p in properties:
        ### create the index by p to other associative p
        
        print "seed p: "+p
        
        triples = g.triples((None,p,None))
        #print triples
        
        subjects = getUniqueSubjects(triples)
        
        mapProperties = {}
        indexSubjects = {}
        

        for sub in subjects:
            
            stms = g.triples((sub,None,None))
            
            for stm in stms:
            
                subj = stm[0]
                
                predicate = stm[1]
                
                if predicate!=p:
                    if predicate not in indexSubjects:
                        indexSubjects[predicate]=set()
                        indexSubjects[predicate].add(sub)
                        mapProperties[predicate] = 1
                    
                    if sub not in indexSubjects[predicate]:
                        indexSubjects[predicate].add(sub)
                        mapProperties[predicate] +=1

        associations[p] = mapProperties

        for i in mapProperties:
            print p + "\t" + i + "\t" + str(mapProperties[i])

    return

def main():
    
    filename = '/Users/zhaoj/workspace/ProvQ/data/ta-201402.nt'
    #filename = '/Users/zhaoj/workspace/ProvQ/data/test-ta-prov.nt'

    analyse(filename)

if __name__ == "__main__":
    main()