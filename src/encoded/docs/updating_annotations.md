Updating annotations
=========================

DEPRECATED Now uses Gene objects

This document describes how to update the annotations used for searching and validation in the encoded application, ```annotations.json```.

Annotations used
---------------- 

* [Entrez Gene ID (NCBI)]
* [Refseq (NCBI)]
* [HUGO Gene Nomenclature Committee HGNC ID (HGNC)]
* [Mouse Genome Informatics (MGI)]
* [ENCODE Genes]

How to update the annotations versions
---------------- 

1. The ```annotations.json``` uses official identifiers for the annotated genes. We retrieve location information from our Gene objects ```locations``` property. The ```locations``` property uses RefSeq identifiers in gff assembly files from [NCBI Genomes] to obtain coordinates. The RefSeq IDs used can be found in the ```dbxrefs``` property of the Gene objects.
	
	* Human identifiers: [HUGO Gene Nomenclature Committee HGNC ID (HGNC)]
	* Mouse identifiers: [Mouse Genome Informatics (MGI)]
	* All gene identifiers: [Entrez Gene ID (NCBI)]
	* RefSeq identifiers: [Refseq (NCBI)]


2. Run [generate_annotations] locally to generate a new ```annotations_local.json``` file:
```
$ bin/generate-annotations
```

3. Rename the ```annotations_local.json``` to one with the date that it was generated:
```
$ cp annotations_local.json annotations_YYYY_MM_DD.json
```

4. Load new annotations file into the encoded-build/annotations directory on S3
```
$ aws s3 cp annotations_YYYY_MM_DD.json s3://encoded-build/annotations/
```

5. Update the annotations version in the [Makefile]:
```
curl -o annotations.json https://s3-us-west-1.amazonaws.com/encoded-build/annotations/annotations_YYYY_MM_DD.json
```

6. Update the following information

    Site release version: 109
    annotations.json file: annotations-2020-10-21.json
    [GRCh38 gff assembly release date]: 2019-02-28
    [hg19 gff assembly release date]: 2013-06-28
    [mm10 gff assembly release date]: 2017-09-15
    [mm9 gff assembly release date]: 2010-10-21

[ENCODE Genes]: https://www.encodeproject.org/search/?type=Gene
[NCBI Genomes]: https://ftp.ncbi.nlm.nih.gov/genomes/
[Refseq (NCBI)]: https://www.ncbi.nlm.nih.gov/refseq/
[Entrez Gene ID (NCBI)]: http://ncbi.nlm.nih.gov/gene/
[HUGO Gene Nomenclature Committee HGNC ID (HGNC)]: http://genenames.org
[Mouse Genome Informatics (MGI)]: http://informatics.jax.org
[Makefile]: ../../../Makefile
[generate_annotations]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/commands/generate_annotations.py
[GRCh38 gff assembly release date]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.39/
[hg19 gff assembly release date]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.25/
[mm10 gff assembly release date]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001635.26/
[mm9 gff assembly release date]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001635.18/
