Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application, ```ontology.json``` .

Ontologies used
---------------- 

* [Uber anatomy ontology (Uberon)]
* [Cell Ontology (CL)]
* [Experimental Factor Ontology (EFO)]

How to update the ontology versions
---------------- 

1. Ontology files to use:
	
	* Uberon and CL: composite-metazoan.owl  from [Uberon download]
	* EFO: EFO_inferred.owl from [EFO src tree]

2. Run generate-ontology, an example is: 

	$ bin/generate-ontology --uberon-url=http://svn.code.sf.net/p/obo/svn/uberon/releases/YYYY-MM-DD/composite-metazoan.owl --efo-url=http://www.ebi.ac.uk/efo/efo_inferred.owl?format=raw

3. Rename the ```ontology.json``` to one with the date that it was generated:

	$ cp ontology.json ontology-YYYY-MM-DD.json

4. Load new ontology file into the encoded-build/ontology directory on S3

	$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/

5.  Update the ontology version in the [buildout.cfg]:

	curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json

6.  Update the following information
    
    Site release version: 1
    ontology.json file: ontology-2020-07-31.json
    [UBERON release date]: 2020-06-05
    [EFO release date]: 2020-07-15

[Uber anatomy ontology (Uberon)]: http://uberon.org/
[Cell Ontology (CL)]: http://cellontology.org/
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[Uberon download]: http://uberon.github.io/downloads.html
[EFO src tree]: https://github.com/EBISPOT/efo/
[buildout.cfg]: ../../../buildout.cfg
[UBERON release date]: http://svn.code.sf.net/p/obo/svn/uberon/releases/
[EFO release date]: https://github.com/EBISPOT/efo/blob/master/ExFactor%20Ontology%20release%20notes.txt
