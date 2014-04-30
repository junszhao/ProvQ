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




def countProvoClasses (g):
    sparqlquery = """
        select (count (distinct ?o) as ?cnt)
        where {?s a ?o .
        filter (REGEX(STR(?o), "^http://www.w3.org/ns/prov#"))
        }
        """
    data = sparql("/sparql/endpoint-lax/"+g, sparqlquery)
    
    for binding in data["results"]["bindings"]:
    
        print binding["cnt"]["value"]
    return








def countProvoInstances (g):
    sparqlquery = """
        select ?o (count(distinct ?s) as ?cnt)
        where {?s a ?o .
        filter (REGEX(STR(?o), "^http://www.w3.org/ns/prov#"))
        }
        group by ?o

        """
    data = sparql("/sparql/endpoint-lax/"+g, sparqlquery)
    

    
    for binding in data["results"]["bindings"]:
        
        
        if len(binding)>1:
            print binding["o"]["value"] + "\t" + binding["cnt"]["value"]
        else:
            print "No PROV-O instances found"
    return








def countProvoStms (g):
    sparqlquery = """
        select ?p (count(*) as ?cnt)
        where {?s ?p ?o .
        filter (REGEX(STR(?p), "^http://www.w3.org/ns/prov#"))
        }
        group by ?p
        """
    data = sparql("/sparql/endpoint-lax/"+g, sparqlquery)
    
    for binding in data["results"]["bindings"]:
        
        print binding["p"]["value"] + "\t" + binding["cnt"]["value"]
    return








def countProvoProperties (g):
    sparqlquery = """
        select (count(distinct ?p) as ?cnt)
        where {?s ?p ?o .
        filter (REGEX(STR(?p), "^http://www.w3.org/ns/prov#"))
        }
        """
    data = sparql("/sparql/endpoint-lax/"+g, sparqlquery)
    
    for binding in data["results"]["bindings"]:
        
        print binding["cnt"]["value"]
    return




def propertyAssociations (g):



def analyse(filename):
    
                    #countInstances()
                    #countTriples()
                    
    print "==== Analyse " + filename + "===="
                    
    countProvoClasses(filename)

    countProvoInstances(filename)
                    
    countProvoProperties(filename)

    countProvoStms(filename)
                    
    return


def main():
                    
    endpointpath = ["ta-provenance", "csiro", "obiama"]
                    
    endpointhost = "http://www.open-biomed.org.uk/sparql/endpoint-lax/"
    
    for arg in endpointpath:
        analyse(arg)

if __name__ == "__main__":
    main()
