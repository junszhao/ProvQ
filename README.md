ProQ
==============
This is the source code for a profile-based approach of generating PROV queries for a PROV dataset. 

An early result of this work has been published in Prov Analytics, see http://provenanceweek.org/2014/analytics/papers/2-1.pdf.

This is still work ongoing, see list of open issues (https://github.com/junszhao/ProvQ/issues). Current the query generation function can only process PROV-O data in N-Triple format.

Prerequisites

1. python 2.7 and above
2. rdflib

To run the query generation code:

1. Go to the folder of src/query-generator/

2. python prov-query-generator.py [prov data file name]


