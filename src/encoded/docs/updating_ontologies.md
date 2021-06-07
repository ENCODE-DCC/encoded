Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application, ```ontology.json``` .

Ontologies used
---------------- 

* [Uber anatomy ontology (Uberon)]
* [Cell Ontology (CL)]
* [Experimental Factor Ontology (EFO)]
* [Ontology for Biomedical Investigations (OBI)]
* [Cell Line Ontology (CLO)]
* [Human Disease Ontology (DOID)]

How to update the ontology versions
---------------- 

1. Ontology files to use:
	
	* Uberon and CL: composite-metazoan.owl  from [Uberon download]
	* EFO: EFO_inferred.owl from [EFO src tree]
	* OBI: obi.owl [OBI download]
	* CLO: clo.owl [CLO download]
	* DOID: doid.owl [DOID download]

2. Run generate-ontology, an example is: 
```
	$ generate-ontology --uberon-url=https://github.com/obophenotype/uberon/releases/download/vYYYY-MM-DD/composite-metazoan.owl --efo-url=http://www.ebi.ac.uk/efo/efo_inferred.owl?format=raw --obi-url=http://purl.obolibrary.org/obo/obi.owl --clo-url=http://purl.obolibrary.org/obo/clo.owl --doid-url=http://purl.obolibrary.org/obo/doid.owl
```
3. Rename the ```ontology.json``` to one with the date that it was generated:
```
	$ cp ontology.json ontology-YYYY-MM-DD.json
```
4. Load new ontology file into the encoded-build/ontology directory on S3
```
	$ aws s3 cp ontology-YYYY-MM-DD.json s3://encoded-build/ontology/
```
5.  Update the ontology version in the [Makefile]:
```
	curl -o ontology.json https://s3-us-west-1.amazonaws.com/encoded-build/ontology/ontology-YYYY-MM-DD.json
```
6.  Update the following information
    
    Site release version: 118
    ontology.json file: ontology-2021-06-02.json
    [UBERON release date]: 2021-02-12
    [OBI release date]: 2021-04-06
    [EFO release date]: 2021-05-17
    [CLO release date]: 2019-02-10
    [DOID release date]: 2021-02-24

[Uber anatomy ontology (Uberon)]: http://uberon.org/
[Cell Ontology (CL)]: http://cellontology.org/
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[Ontology for Biomedical Investigations (OBI)]: http://obi-ontology.org/
[Cell Line Ontology (CLO)]: http://www.clo-ontology.org
[Human Disease Ontology (DOID)]: http://www.disease-ontology.org
[Uberon download]: https://github.com/obophenotype/uberon/releases
[EFO src tree]: https://github.com/EBISPOT/efo/
[OBI download]: http://www.ontobee.org/ontology/OBI
[CLO download]: http://www.ontobee.org/ontology/CLO
[DOID download]: http://www.ontobee.org/ontology/DOID
[Makefile]: ../../../Makefile
[UBERON release date]: https://github.com/obophenotype/uberon/releases
[OBI release date]: http://www.ontobee.org/ontology/OBI 
[EFO release date]: https://github.com/EBISPOT/efo/blob/master/ExFactor%20Ontology%20release%20notes.txt
[CLO release date]: http://www.ontobee.org/ontology/CLO
[DOID release date]: http://www.ontobee.org/ontology/DOID
