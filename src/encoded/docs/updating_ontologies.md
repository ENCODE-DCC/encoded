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
	
	* Uberon and CL: composite-metazoan.owl from [Uberon download]
	* EFO: EFO_inferred.owl from [EFO src tree]
	* OBI: obi.owl [OBI download]
	* CLO: clo.owl [CLO download]
	* DOID: doid.owl [DOID download]

2. Run generate-ontology, an example is: 
```
$ generate-ontology --uberon-url=https://github.com/obophenotype/uberon/releases/download/vYYYY-MM-DD/composite-metazoan.owl --efo-url=https://github.com/EBISPOT/efo/releases/download/v#.##.#/efo.owl --obi-url=http://purl.obolibrary.org/obo/obi.owl --clo-url=http://purl.obolibrary.org/obo/clo.owl --doid-url=http://purl.obolibrary.org/obo/doid.owl --cl-url=https://github.com/obophenotype/cell-ontology/raw/master/cl-full.owl
```
3. Rename the ```ontology.json``` to one with the date that it was generated:
```
$ cp ontology.json ontology-YYYY-MM-DD.json
```
4. Load new ontology file into the encoded-build/ontology directory on S3
```
$ aws s3 cp ontology-YYYY-MM-DD.json s3://encoded-build/ontology/
```
Locate the file on S3 and change the permissions so that "Read" permission is granted to "Everybody (public access)."

5.  Update the ontology version in the [Makefile]:
```
curl -o ontology.json https://s3-us-west-1.amazonaws.com/encoded-build/ontology/ontology-YYYY-MM-DD.json
```
6.  Update the following information
    
    Site release version: 129
    ontology.json file: ontology-2022-11-01.json
    [UBERON release date]: 2022-09-30
    [CL release date]: 2022-09-15
    [OBI release date]: 2022-07-11
    [EFO release date]: 2022-10-17
    [CLO release date]: 2022-03-20
    [DOID release date]: 2022-11-01

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
[CL release date]: https://github.com/obophenotype/cell-ontology/releases
[OBI release date]: https://github.com/obi-ontology/obi/releases
[EFO release date]: https://github.com/EBISPOT/efo/blob/master/ExFactor%20Ontology%20release%20notes.txt
[CLO release date]: http://www.ontobee.org/ontology/CLO
[DOID release date]: http://www.ontobee.org/ontology/DOID
