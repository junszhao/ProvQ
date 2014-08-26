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
from operator import truediv



class AssociationMiner (object):
    
    def __init__(self, provdata):
        
        self.filename = provdata
        self.associations = {}
    
    def analyse(self):
        
        print "==== Compute property association for: " + self.filename + "===="
        
        g = Graph()
        g.parse(self.filename, format="nt")
        
        ### find all the unique properties
        properties = g.predicates()
        
        keys = set()
        
        for p in properties:
            if p not in keys:
                keys.add(p)
        
        #print keys
        
        ### compute the association
        
        #associations = {}
        
        for p in keys:
            ### create the index by p to other associative p
            
            #print "seed p: "+p
            
            triples = g.triples((None,p,None))
            #print triples
            
            subjects = set()
            for triple in triples:
                subject = triple[0]
                
                if subject not in subjects:
                    subjects.add(subject)
            
            mapProperties = {}
            indexSubjects = {}
            
            totalsubj = 0
            
            for sub in subjects:
                
                totalsubj += 1
                
                stms = g.triples((sub,None,None))
                
                for stm in stms:
                    
                    predicate = stm[1]
                    
                    if predicate!=p:
                        if predicate not in indexSubjects:
                            indexSubjects[predicate]=set()
                            indexSubjects[predicate].add(sub)
                            mapProperties[predicate] = 1
                        
                        if sub not in indexSubjects[predicate]:
                            indexSubjects[predicate].add(sub)
                            mapProperties[predicate] +=1
        
            highConfProperties = set()
        
            for i in mapProperties:
                mapProperties[i] = truediv(mapProperties[i], totalsubj)
                if (mapProperties[i]>0.9):
                    highConfProperties.add(i)
                    

            self.associations[p] = highConfProperties
            
#            for i in mapProperties:
#                if (truediv(mapProperties[i], totalsubj) > 0.9):
#                    print p + "\t" + i + "\t" + str(mapProperties[i]) + "\t" + str(truediv(mapProperties[i], totalsubj))

        return
