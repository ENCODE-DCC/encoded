Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application, ```ontology.json``` .

Ontologies used
---------------- 

* [Uber anatomy ontology (Uberon)]
* [Cell Ontology (CL)]
* [Experimental Factor Ontology (EFO)]
* [Ontology for Biomedical Investigations (OBI)]

How to update the ontology versions
---------------- 

1. Ontology files to use:
	
	* Uberon and CL: composite-metazoan.owl  from [Uberon download]
	* EFO: EFO_inferred.owl from [EFO src tree]
	* OBI: obi.owl [OBI releases], identify the most recent release at time of generating ```ontology.json```

2. Run generate-ontology, an example is: 

	$ bin/generate-ontology --uberon-url=http://ontologies.berkeleybop.org/uberon/composite-metazoan.owl --efo-url=http://sourceforge.net/p/efo/code/HEAD/tree/trunk/src/efoinowl/InferredEFOOWLview/EFO_inferred.owl?format=raw --obi-url=http://svn.code.sf.net/p/obi/code/releases/<<<<USE THE MOST RECENT DATE HERE>>>>/obi.owl

3. Rename the ```ontology.json``` to one with the date that it was generated:

	$ cp ontology.json ontology-YYYY-MM-DD.json

4. Load new ontology file into the encoded-build/ontology directory on S3

	$ aws s3 cp ontology-YYYY-MM-DD.json s3://encoded-build/ontology

5.  Update the ontology version in the [buildout.cfg]:

	curl -o ontology.json https://s3-us-west-1.amazonaws.com/encoded-build/ontology ontology-YYYY-MM-DD.json

6.  Update the following information
    
    Site release version: 59   
    ontology.json file: ontology-2017-07-17.json   
    [UBERON release date]: 2017-05-21   
    [OBI release date]: 2016-10-11   
    [EFO release date]: 2017-06-14

[Uber anatomy ontology (Uberon)]: http://uberon.org/
[Cell Ontology (CL)]: http://cellontology.org/
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[Ontology for Biomedical Investigations (OBI)]: http://obi-ontology.org/
[Uberon download]: http://uberon.github.io/downloads.html
[EFO src tree]: https://sourceforge.net/p/efo/code/HEAD/tree/trunk/src/efoinowl/InferredEFOOWLview/
[OBI releases]: http://svn.code.sf.net/p/obi/code/releases/
[buildout.cfg]: ../../../buildout.cfg
[UBERON release date]: http://uberon.github.io/
[OBI release date]: http://svn.code.sf.net/p/obi/code/releases/ 
[EFO release date]: https://sourceforge.net/p/efo/code/HEAD/tree/trunk/src/efoinowl/InferredEFOOWLview/