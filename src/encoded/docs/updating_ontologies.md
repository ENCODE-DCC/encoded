Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use | Version reference |
|:--|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `composite-vertebrate.owl` from [UBERON releases] | 2021-02-12 | [UBERON releases] |
| [Cell Ontology (CL)] | `cl.ow` from [CL] | 2021-06-21 | [CL releases] |
| [Experimental Factor Ontology (EFO)] | `efo-base.owl` from [EFO releases] | 2021-06-15 (3.31.0) | [EFO releases] |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [MONDO] | 2021-06-01 | [MONDO release] |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [HANCESTRO] | 2021-01-04 (2.5) | [HANCESTRO releases] |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [HsapDv] | 2020-03-10 | [OLS HsapDv] (confirm versionIRI in .owl) |
| [Mouse Developmental Stage Ontology (MmusDv)] | `mmusdv.owl` from [MmusDv] | 2020-03-10 | [OLS MmusDv] (confirm versionIRI in .owl) |

**Current ontology.json:** `ontology-2021-06-25.json`

How to update the ontology versions
---------------- 

1. Run generate-ontology  
*note: first look up the latest [UBERON release] and [EFO release] and include the versions each url*

	`$ bin/generate-ontology --uberon-version YYYY-MM-DD --efo-version X.XX.X`

2. Rename the `ontology.json` to one with the date that it was generated

	`$ cp ontology.json ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/`

4.  Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5.  Update the **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://uberon.org/
[UBERON releases]: https://github.com/obophenotype/uberon/releases/
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[CL]: http://obofoundry.org/ontology/cl.html
[CL releases]: https://github.com/obophenotype/cell-ontology/releases
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[EFO releases]: https://github.com/EBISPOT/efo/releases
[EFO release]: https://github.com/EBISPOT/efo/releases
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[MONDO]: http://obofoundry.org/ontology/mondo.html
[MONDO release]: https://github.com/monarch-initiative/mondo/releases
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[HANCESTRO]: https://github.com/EBISPOT/ancestro
[HANCESTRO releases]: https://github.com/EBISPOT/ancestro/releases
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[HsapDv]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[OLS HsapDv]: https://www.ebi.ac.uk/ols/ontologies/hsapdv
[Mouse Developmental Stage Ontology (MmusDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv
[MmusDv]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv
[OLS MmusDv]: https://www.ebi.ac.uk/ols/ontologies/mmusdv
[buildout.cfg]: ../../../buildout.cfg
