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

### produce a data summary for a PROV-O dataset
### Currently we use the ProLOD++ app for this: https://www.hpi.uni-potsdam.de/naumann/sites/prolod++/app.html
### For the moment, the profile results are hard-coded. We will work with ProvLOD++ team to revise this

def prolod (g):
    return

def queryGenerator (g):
    
    properties = ["prov:used", "prov:wasGeneratedBy", "prov:wasDerivedFrom", "prov:startedAtTime", "prov:endedAtTime", "prov:wasAssociatedWith", "prov:wasAttributedTo", "prov:wasInformedBy", "prov:actedOnBehalfOf"]
    
    for p in properties:
        sparqlquery = """
            PREFIX prov: <http://www.w3.org/ns/prov#>
            select distinct ?p
            where {?s """ + p + """ ?o; ?p ?o}
            """
        print sparqlquery
    return



def provq(filename):
    
    print "==== Query Generation For: " + filename + "===="
                    
    queryGenerator(filename)

#generateExQueries(filename)
    
    return


def main():
                    
    #endpointpath = ["ta-provenance", "csiro", "obiama"]
    
    endpointpath = ["ta-provenance"]
                    
    endpointhost = "http://www.open-biomed.org.uk/sparql/endpoint-lax/"
    
    for arg in endpointpath:
        provq(arg)

if __name__ == "__main__":
    main()
