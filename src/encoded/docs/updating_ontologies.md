Updating ontologies
=========================

This document describes how to update the ontology versions used for searching and validation in the encoded application.

Ontologies used
---------------- 

| Ontology |  File used | Version in use |
|:--|:--|:--|
| [Uber-anatomy ontology (UBERON)] | `uberon.owl` from [OLS-UBERON] | 2021-11-28 |
| [Cell Ontology (CL)] | `cl.ow` from [OLS-CL] | 2021-12-07 |
| [Experimental Factor Ontology (EFO)] | `efo.owl` from [OLS-EFO] | 3.36.0 |
| [Mondo Disease Ontology (MONDO)] | `mondo.owl` from [OLS-MONDO] | 2021-12-01 |
| [Human Ancestry Ontology (HANCESTRO)] | `hancestro.owl` from [OLS-HANCESTRO] | 2.5 |
| [Human Developmental Stage Ontology (HsapDv)] | `hsapdv.owl` from [OLS-HsapDv] | 2020-03-10 |
| [Mouse Developmental Stage Ontology (MmusDv)] | `mmusdv.owl` from [OLS-MmusDv] | 2020-03-10 |

**Current ontology.json:** `ontology-2021-12-08.json`

How to update the ontology versions
---------------- 

1. Run generate-ontology

	`$ bin/generate-ontology`

2. Rename the `ontology.json` to one with the date that it was generated

	`$ cp ontology.json ontology-YYYY-MM-DD.json`

3. Load new ontology file into the latticed-build/ontology directory on S3

	`$ aws s3 cp ontology-YYYY-MM-DD.json s3://latticed-build/ontology/`

4.  Update the ontology.json file in [buildout.cfg]

	`curl -o ontology.json https://latticed-build.s3-us-west-2.amazonaws.com/ontology/ontology-YYYY-MM-DD.json`

5.  Update the **Version in use** and **Current ontology.json:** above


[Uber-anatomy ontology (UBERON)]: http://uberon.org
[OLS-UBERON]: https://www.ebi.ac.uk/ols/ontologies/uberon
[Cell Ontology (CL)]: https://github.com/obophenotype/cell-ontology
[OLS-CL]: https://www.ebi.ac.uk/ols/ontologies/cl
[Experimental Factor Ontology (EFO)]: http://www.ebi.ac.uk/efo
[OLS-EFO]: https://www.ebi.ac.uk/ols/ontologies/efo
[Mondo Disease Ontology (MONDO)]: http://obofoundry.org/ontology/mondo.html
[OLS-MONDO]: https://www.ebi.ac.uk/ols/ontologies/mondo
[Human Ancestry Ontology (HANCESTRO)]: https://github.com/EBISPOT/ancestro
[OLS-HANCESTRO]: https://www.ebi.ac.uk/ols/ontologies/hancestro
[Human Developmental Stage Ontology (HsapDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/HsapDv
[OLS-HsapDv]: https://www.ebi.ac.uk/ols/ontologies/hsapdv
[Mouse Developmental Stage Ontology (MmusDv)]: https://github.com/obophenotype/developmental-stage-ontologies/wiki/MmusDv
[OLS-MmusDv]: https://www.ebi.ac.uk/ols/ontologies/mmusdv
[buildout.cfg]: ../../../buildout.cfg
