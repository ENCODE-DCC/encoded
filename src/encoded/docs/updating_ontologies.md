Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application, ```ontology.json``` .

Ontologies used
---------------- 

* [Uber-anatomy ontology (UBERON)]
* [Cell Ontology (CL)]
* [Experimental Factor Ontology (EFO)]
* [Mondo Disease Ontology (MONDO)]

How to update the ontology versions
---------------- 

1. Ontology files to use:
	
	* UBERON and CL: `uberon/ext.owl` from [UBERON download]
	* EFO: `efo-base.owl` from [EFO releases]
	* MONDO: `mondo.owl` from [Mondo Disease Ontology (MONDO)]

2. Run generate-ontology, an example is: 
```
	$ bin/generate-ontology --uberon-url=http://purl.obolibrary.org/obo/uberon/ext.owl --efo-url=https://github.com/EBISPOT/efo/releases/download/vX.XX.X/efo-base.owl --mondo-url=http://purl.obolibrary.org/obo/mondo.owl
```
3. Rename the ```ontology.json``` to one with the date that it was generated:
```
	$ cp ontology.json ontology-YYYY-MM-DD.json
```
4. Load new ontology file into the encoded-build/ontology directory on S3
```
	$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/
```
5.  Update the ontology version in the [buildout.cfg]:
```
	$ curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json
```
6.  Update the following information, which notes the versions currently in use by the Lattice database
    
    | Site release version | 1 |
    | ontology.json file | ontology-2020-08-03.json |
    | [UBERON release date] | 2020-06-05 |
    | [EFO release date] | 2020-07-15 (3.20.0) |
    | [MONDO release date] | 2020-06-30 |

[Uber-anatomy ontology (UBERON)]: http://uberon.org/
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[UBERON download]: http://uberon.github.io/downloads.html
[EFO releases]: https://github.com/EBISPOT/efo/releases
[buildout.cfg]: ../../../buildout.cfg
[UBERON release date]: http://svn.code.sf.net/p/obo/svn/uberon/releases/
[EFO release date]: https://github.com/EBISPOT/efo/releases
[MONDO release date]: https://github.com/monarch-initiative/mondo/releases
