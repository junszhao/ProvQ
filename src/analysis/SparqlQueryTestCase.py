#!/usr/bin/python
# $Id: SparqlQueryTestCase.py 1461 2010-10-02 15:55:16Z graham $
"""
Module to test simple queries against LGPN sample data

$Rev: 1461 $
"""

import os, os.path
import sys

import re
import unittest
import logging
import httplib
import urllib
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

from MiscLib import TestUtils

logger = logging.getLogger('SparqlQueryTestCase')

def bindingType(b):
    """
    Function returns the type of a variable binding.  Commonly 'uri' or 'literal'.
    """
    type = b['type']
    if type == "typed-literal" and b['datatype'] == "http://www.w3.org/2001/XMLSchema#string":
        type = 'literal' 
    return type

def findVarBindings(data, var):
    """
    Returns a list of (type,value) pairs to which the supplied variable is bound in the results
    """
    return [ (bindingType(b[var]),b[var]['value']) 
             for b in data['results']['bindings'] if var in b ]

def findBindingSets(data):
    """
    Returns a list of lists of (var:(type,value)) dictionaries from the supplied results
    """
    return [ dict([ (var,{'type':bindingType(bindset[var]), 'value':bindset[var]['value']} ) for var in bindset ]) 
             for bindset in data['results']['bindings'] ]

testdata = {u'head': {u'vars': [u's', u'lit']}, 
    u'results': 
        {u'bindings': 
            [ {u'lit': {u'type': u'literal', u'value': u'Naxos'}, 
               u's': {u'type': u'uri', u'value': u'http://arachne.uni-koeln.de/artifact/130220-statue-eines-unfertigen-kouros'}}, 
              {u'lit': {u'type': u'literal', u'value': u'Naxos'}, 
               u's': {u'type': u'uri', u'value': u'http://clas-lgpn2.classics.ox.ac.uk/placeid/LGPN_12790'}}, 
              {u'lit': {u'datatype': u'http://www.w3.org/2001/XMLSchema#string', u'type': u'typed-literal', u'value': u'Naxos'}, 
               u's': {u'type': u'uri', u'value': u'http://arachne.uni-koeln.de/place/187726-naxos'}}, 
              {u'lit': {u'type': u'literal', u'value': u'NAXOS'}, 
               u's': {u'type': u'uri', u'value': u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF'}}, 
              {u'lit': {u'type': u'literal', u'value': u'Naxos, Archaeological Museum: XXXX42018'}, 
               u's': {u'type': u'uri', u'value': u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF'}}, 
              {u'lit': {u'type': u'literal', u'value': u'42018, Naxos, Archaeological Museum, XXXX42018'}, 
               u's': {u'type': u'uri', u'value': u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF'}}, 
              {u'lit': {u'type': u'literal', u'value': u'Production of 42018, Naxos, Archaeological Museum, XXXX42018'}, 
               u's': {u'type': u'uri', u'value': u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF'}}]}}
testsets = [
    {u'lit': (u'literal', u'Naxos'), 
     u's': (u'uri', u'http://arachne.uni-koeln.de/artifact/130220-statue-eines-unfertigen-kouros')}, 
    {u'lit': (u'literal', u'Naxos'), 
     u's': (u'uri', u'http://clas-lgpn2.classics.ox.ac.uk/placeid/LGPN_12790')}, 
    {u'lit': ('literal', u'Naxos'), 
     u's': (u'uri', u'http://arachne.uni-koeln.de/place/187726-naxos')}, 
    {u'lit': (u'literal', u'NAXOS'), 
     u's': (u'uri', u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF')}, 
    {u'lit': (u'literal', u'Naxos, Archaeological Museum: XXXX42018'), 
     u's': (u'uri', u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF')}, 
    {u'lit': (u'literal', u'42018, Naxos, Archaeological Museum, XXXX42018'), 
     u's': (u'uri', u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF')}, 
    {u'lit': (u'literal', u'Production of 42018, Naxos, Archaeological Museum, XXXX42018'), 
     u's': (u'uri', u'http://www.beazley.ox.ac.uk/record/6A1497E1-FC0B-4155-A5FE-9A1EE4C975DF')}]

class SparqlQueryTestCase(unittest.TestCase):
    """
    Test simple query patterns against LGPN data in SPARQL endpoint
    """
    def setUp(self):
        # Default SPARQL endpoint details
        self._endpointhost = ProvenanceTestConfig.ProveannceTestConfig.endpointhost
        self._endpointpath = ProvenanceTestConfig.ProveannceTestConfig.endpointpath
        return

    def tearDown(self):
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def setQueryEndPoint(self, endpointhost=None, endpointpath=None):
        if endpointhost: self._endpointhost = endpointhost
        if endpointpath: self._endpointpath = endpointpath
        logger.debug("setQueryEndPoint: endpointhost %s: " % self._endpointhost)
        logger.debug("setQueryEndPoint: endpointpath %s: " % self._endpointpath)

    def doQueryGET(self, query, 
            endpointhost=None, endpointpath=None, 
            expect_status=200, expect_reason="OK",
            JSON=False):
        self.setQueryEndPoint(endpointhost, endpointpath)
        hc = httplib.HTTPConnection(self._endpointhost)
        encodequery  = urllib.urlencode({"query": query})
        hc.request("GET", self._endpointpath+"?"+encodequery)
        response = hc.getresponse()
        self.assertEqual(response.status, expect_status)
        self.assertEqual(response.reason, expect_reason)
        responsedata = response.read()
        hc.close()
        if JSON: responsedata = json.loads(responsedata)
        return responsedata

    def doQueryPOST(self, query, 
            endpointhost=None, endpointpath=None, 
            expect_status=200, expect_reason="OK",
            JSON=False):
        reqheaders   = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept":       "application/JSON"
            }
        self.setQueryEndPoint(endpointhost, endpointpath)
        hc = httplib.HTTPConnection(self._endpointhost)
        encodequery  = urllib.urlencode({"query": query})
        hc.request("POST", self._endpointpath, encodequery, reqheaders)
        response = hc.getresponse()
        self.assertEqual(response.status, expect_status)
        self.assertEqual(response.reason, expect_reason)
        responsedata = response.read()
        hc.close()
        if JSON: responsedata = json.loads(responsedata)
        return responsedata

    def assertEqualModuloWhitespace(self, data, expect):
        pattern = re.compile("[ \n]+")
        # Use HTTP POST
        data = pattern.sub("", data)
        self.assertEqual(data, expect)
        return

    def assertVarBinding(self, data, var, type, value):
        """
        Asserts that the results for 'var' containing a binding
        """
        self.assertTrue( (type, value) in findVarBindings(data, var),
            """Expected to find %s bound as %s:"%s" in query results"""%(var, type, value))

    def assertBinding(self, data, var, type=None, value=None):
        self.assertTrue(var in data['head']['vars'], "Expected variable %s binding in query results"%(var))        
        bindings = findBindingSets(data)
        found = False
        for b in bindings:
            if var in b:
                match = True
                match &= (type  == None) or (b[var]['type']  == type)
                match &= (value == None) or (b[var]['value'] == value)
                if match:
                    found = True
                    break
        self.assertTrue(found, "Expected to find %s bound with type %s to value %s"%(var, type, value))

    def assertBindingCount(self, data, count):
        bindings = len(data['results']['bindings'])        
        self.assertEqual(bindings, count, "Expected %i result bindings, found %i"%(count, bindings))

    def assertBindingEqual(self, data, count, msg):
        bindings = len(data['results']['bindings'])        
        self.assertEqual(bindings, count, msg)

    def assertBindingSet(self, data, expectbindingset):
        """
        Asserts that a given set of variable bindings occurs in at least one of the 
        result variable bindings from a query.
        """
        found = False
        for resultbinding in findBindingSets(data):
            # For each query result...
            match = True
            for [var, expect] in expectbindingset:
                # For each expected variable binding
                self.assertTrue(var in data['head']['vars'], "Expected variable %s binding in query results"%(var))                    
                # If variable is not bound in result, continue to next result 
                if not var in resultbinding:
                    match = False
                    continue
                # Match details for single variable in binding set
                for facet in expect:
                    match &= facet in resultbinding[var] and resultbinding[var][facet] == expect[facet]
            # Exit if all variables matched in single binding
            if match: return
        # No matching binding found
        self.assertTrue(False, "Expected to find binding set %s"%(expectbindingset))

    def assertBindingSetPos(self, data, pos, expectbindingset):
        """
        Asserts that a given set of variable bindings occurs in at least one of the 
        result variable bindings from a query.
        """
        resultbinding = findBindingSets(data)[pos]
        for [var, expect] in expectbindingset:
            # For each expected variable binding
            self.assertTrue(var in data['head']['vars'], "Expected variable %s binding in query results"%(var))                    
            # If variable is not bound in result, continue to next result 
            self.assertTrue(var in resultbinding, "Expected variable %s binding in query results"%(var))
            # Match details for single variable in binding set
            for facet in expect:
                self.assertTrue(
                    (facet in resultbinding[var] and resultbinding[var][facet] == expect[facet]), 
                    "Result %i expected binding set %s"%(pos,expectbindingset))

    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

# Assemble test suite

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ "testUnits"
            , "testNull"
            , "testTripleExists"
            , "testSimpleJSONDecode"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(SparqlQueryTestCase, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("SparqlQueryTestCase", getTestSuite, sys.argv)

# End.
