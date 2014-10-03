"""prov-analysis.py: Some basic prov-o benchmarking

Usage: prov-analysis.py
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
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF

def createModel(filename):
    
    print "==== create query model for: " + filename + "===="
    
    g = Graph()
    g.parse(filename, format="nt")
    
    return g


def countInstances (g):

    sparqlquery = """
        select ?o (count (distinct ?o) as ?cnt)
        where {?s rdf:type ?o .
        }
        group by ?o
        """
    results = g.query(sparqlquery)

    if len(results)>0:
        for result in results:
            classname = result['o']
            count = result['cnt']
        
            print "==== Find " + count + " class " + classname

    return

def countProvoInstances (g):
    
    sparqlquery = """
        select ?o (count (distinct ?o) as ?cnt)
        where {?s rdf:type ?o .
        filter (REGEX(STR(?o), "^http://www.w3.org/ns/prov#"))
        }
        group by ?o
        """
    results = g.query(sparqlquery)
    
    if len(results)>1:
        for result in results:
            count = 0
            classname = result['o']
            count = result['cnt']
            
            print "==== Find " + str(count) + " PROV-O class " + classname
    
    return



def countProvoStms (g):
    sparqlquery = """
        select ?p (count(*) as ?cnt)
        where {?s ?p ?o .
        filter (REGEX(STR(?p), "^http://www.w3.org/ns/prov#"))
        }
        group by ?p
        """
    
    results = g.query(sparqlquery)
    
    
    if len(results)>0:
        count = 0
        for result in results:
            property = result['p']
            count = result['cnt']
            
            print "==== Find " + str(count) + " statements for PROV-O property " + property
    
    return
    








def countProvoProperties (g):
    sparqlquery = """
        select distinct ?p
        where {?s ?p ?o .
        filter (REGEX(STR(?p), "^http://www.w3.org/ns/prov#"))
        }
        """
    
    results = g.query(sparqlquery)
    
    properties = set()
    
    count = 0
    if len(results)>0:
        
        for result in results:
            p = result['p']
            if p not in properties:
                properties.add(p)
                count = count +1
    print "==== Find " + str(count)  + " PROV-O properties "
    return




def analyse(filename):
    
    
    print "==== Analyse " + filename + "===="
    
    g = createModel(filename)
    

    countInstances(g)
    
    countProvoInstances(g)
                    
    countProvoProperties(g)

    countProvoStms(g)

    return


def main(argv):
    
    #filename = '/Users/zhaoj/workspace/ProvQ/data/ta-201402.nt'
    #    filename = '/Users/zhaoj/workspace/ProvQ/data/workflowrun.provo.nt'
    #    filename = '/Users/zhaoj/workspace/ProvQ/data/workflowrun.all.nt'
    
    analyse(argv)


if __name__ == "__main__":
    main(sys.argv[1])