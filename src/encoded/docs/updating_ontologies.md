Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use | Version reference |
|:--|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `composite-vertebrate.owl` from [UBERON releases] | 2021-02-12 | [UBERON release] |
| [Cell Ontology (CL)] | `cl.ow` from [CL] | 2021-04-22 | [CL release] |
| [Experimental Factor Ontology (EFO)] | `efo-base.owl` from [EFO releases] | 2021-04-20 (3.29.1) | [EFO releases] |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | 2021-04-07 | [MONDO release date] |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [OLS] | 2021-01-04 (2.5) | [HANCESTRO releases] |

**Current ontology.json:** `ontology-2021-06-11.json`

How to update the ontology versions
---------------- 

1. Run generate-ontology  
*note: first look up the latest [UBERON release] and [EFO release] and include the versions each url*

	`$ bin/generate-ontology --uberon-url=https://github.com/obophenotype/uberon/releases/download/vYYYY-MM-DD/composite-vertebrate.owl --efo-url=https://github.com/EBISPOT/efo/releases/download/vX.XX.X/efo-base.owl --mondo-url=http://purl.obolibrary.org/obo/mondo.owl --hancestro-url=http://purl.obolibrary.org/obo/hancestro/hancestro.owl --cl-url=http://purl.obolibrary.org/obo/cl.owl`

2. Rename the `ontology.json` to one with the date that it was generated
	`$ cp ontology.json ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3
	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/`

4.  Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5.  Update the **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://uberon.org/
[UBERON download]: https://github.com/obophenotype/uberon/releases/
[UBERON release]: https://github.com/obophenotype/uberon/releases/
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[CL download]: http://obofoundry.org/ontology/cl.html
[CL release]: https://github.com/obophenotype/cell-ontology/releases
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
