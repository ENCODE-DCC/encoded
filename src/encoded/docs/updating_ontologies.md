Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use | Version reference |
|:--|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `uberon/ext.owl` from [UBERON download] | 2020-06-05 | [UBERON release date] |
| [Cell Ontology (CL)] | incl. w/ UBERON | incl. w/ UBERON | incl. w/ UBERON |
| [Experimental Factor Ontology (EFO)] | `efo-base.owl` from [EFO releases] | 2020-07-15 (3.20.0) | [EFO releases] |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | 2020-06-30 | [MONDO release date] |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [OLS] | 2019-07-22 (2.3) | [HANCESTRO releases] |

**Current ontology.json:** `ontology-2020-08-04.json`  
**Updated with site version:** 1

How to update the ontology versions
---------------- 

1. Run generate-ontology  
*note: first look up the latest [EFO release] and include the version in the `efo-url`*
```
	$ bin/generate-ontology --uberon-url=http://purl.obolibrary.org/obo/uberon/ext.owl --efo-url=https://github.com/EBISPOT/efo/releases/download/vX.XX.X/efo-base.owl --mondo-url=http://purl.obolibrary.org/obo/mondo.owl --hancestro-url=http://purl.obolibrary.org/obo/hancestro/hancestro.owl
```

2. Rename the `ontology.json` to one with the date that it was generated
```
	$ cp ontology.json ontology-YYYY-MM-DD.json
```
3. Load new ontology file into the encoded-build/ontology directory on S3
```
	$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/
```
4.  Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5.  Update the **Version in use** and ontology.json/site versions above


[Uber-anatomy ontology (UBERON)]: http://uberon.org/
[UBERON download]: http://uberon.github.io/downloads.html
[UBERON release date]: http://svn.code.sf.net/p/obo/svn/uberon/releases/
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[EFO releases]: https://github.com/EBISPOT/efo/releases
[EFO release]: https://github.com/EBISPOT/efo/releases
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[MONDO]: http://obofoundry.org/ontology/mondo.html
[MONDO release date]: https://github.com/monarch-initiative/mondo/releases
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[OLS]: https://www.ebi.ac.uk/ols/ontologies/hancestro
[HANCESTRO releases]: https://github.com/EBISPOT/ancestro/releases
[buildout.cfg]: ../../../buildout.cfg
