Updating annotations
=========================

This document describes how to update the annotations used for searching and validation in the encoded application, ```annotations.json``` .

Annotations used
---------------- 

* [Ensembl Gene ID (Ensembl)]
* [Entrez Gene ID (NCBI)]
* [HUGO Gene Nomenclature Committee HGNC ID (HGNC)]
* [Mouse Genome Informatics (MGI)]

How to update the annotations versions
---------------- 

1. Annotation files to use:
	
	* Human (HGNC file): tsv using ENCODE Portal Gene Object [Encode Portal Gene]
	* Mouse (Mouse file): tsv using MGI [Mouse Genome Informatics (MGI)]

2. Archive the old annotation files used to generate the prior ```annotations.json``` . The archived file should have a *superseded_by* value for the new file that replaces it.

3. Update the path to new tsv files uploaded on portal in [generate_annotations.py]

4. Run generate-annotations on demo machine as encoded user:

	$ cd encoded/srv/encoded/
	$ sudo -su encoded
	$ bin/generate-annotations development.ini --app-name app

5. Transfer ```annotations_local.json``` to local machine:

	$ scp ubuntu@PublicDNS(IPv4):/srv/encoded/annotations_local.json annotations_local.json

6. Rename the ```annotations_local.json``` to one with the date that it was generated:

	$ cp annotations_local.json annotations_YYYY_MM_DD.json

7. Load new annotations file into the encoded-build/annotations directory on S3

	$ aws s3 cp annotations_YYYY_MM_DD.json s3://encoded-build/annotations/

8.  Update the annotations version in the [buildout.cfg]:

	curl -o annotations.json https://s3-us-west-1.amazonaws.com/encoded-build/annotations/annotations_YYYY_MM_DD.json

9.  Update the following information
    
    Site release version: 92 (needs updating the info here)
    annotations.json file: annotations-2019-06-28.json
    [Ensembl release date]: 2020-04-29

[Ensembl Gene ID (Ensembl)]: http://ensembl.org/
[Entrez Gene ID (NCBI)]: http://ncbi.nlm.nih.gov/gene/
[HUGO Gene Nomenclature Committee HGNC ID (HGNC)]: http://genenames.org
[Mouse Genome Informatics (MGI)]: http://informatics.jax.org
[Encode Portal Gene]: http://encodeproject.org/search/?type=Gene
[buildout.cfg]: ../../../buildout.cfg
[generate_annotations.py]: ../../../src/encoded/commands/generate_annotations.py
[Ensembl release date]: http://ensembl.info