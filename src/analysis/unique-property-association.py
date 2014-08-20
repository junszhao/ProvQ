"""property-associatin.py: compute unique property associations
    
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

def analyse(filename):

    g = createModel(filename)
    
    ### find all the unique properties
    properties = getUniquePredicates(g)
    
    ### compute the association
    
    associations = {}
    
    for seed_p in properties:
        ### create the index by p to other associative p
        
        #print "seed_p: " + seed_p
    
        pairs = g.subject_objects(seed_p)
    
        countMap = {}

        for sub_obj in pairs:
            
            for s,p,o in g.triples((sub_obj[0],None,sub_obj[1])):
                ### a property that is used with the same (sub,obj) as seed_p
                if p!=seed_p:
    
                    if p in countMap:
                        countMap[p]+=1
    
                    else:
                        countMap[p] = 1
    
        associations[seed_p] = countMap

        for i in countMap:
            print seed_p + "\t" + i + "\t" + str(countMap[i])

    return

def main():
    
    filename = '/Users/zhaoj/workspace/ProvQ/data/ta-201402.nt'

    analyse(filename)

if __name__ == "__main__":
    main()