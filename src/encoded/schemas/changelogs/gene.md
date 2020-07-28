## Changelog for gene.json

### Minor changes since schema version 2

* Added *locations*, which specifies the chromosome and genomic coordinates of the gene using a 1-based, closed coordinate system.

### Schema version 2

* Remove *go_annotations*.

### Minor changes since schema version 1

* *dbxrefs* was set to have a minimum of 1.

### Schema version 1

* The Gene object is isolated from the Target object which will hold metadata from Target and replace some properties of Target. It is initially created by adopting the schema and type of target object. It has seven essential properties:
  - *geneid*: NCBI Entrez GeneID.
  - *ncbi_entrez_status*: the status of corresponding record in NCBI Entrez Gene database. One of *live*, *secondary*, *discontinued*. For details, see https://www.ncbi.nlm.nih.gov/data_specs/schema/NCBI_Entrezgene.mod.xsd
  - *symbol*: gene symbol approved by official nomenclature such as HGNC, MGI, FlyBase, WormBase.
  - *name*: the full gene name provided by NCBI Entrez Gene database. Since all genes in ENCODE portal are approved by official nomenclature, this name will be preferably name approved by the official nomenclature.
  - *synonyms*: alternative symbols/names referring to the gene.
  - *dbxrefs*: external resources related to the gene. As for now, only the following databases are allowed:

      "enum" : [
          "HGNC",
          "MGI",
          "FlyBase",
          "WormBase",
          "ENSEMBL",
          "MIM",
          "UniProtKB",
          "Vega",
          "miRBase",
          "IMGT/GENE-DB",
          "RefSeq"
      ]
  - *go_annotations*: a list of gene ontology annotations of the gene, including all three aspects: Biological Process, Cellular Component, and Molecular Function. Each ontology annotation should include GO ID, ontology term name, annotation evidence code and the aspect of ontology (P: biological process, F: molecular function or C: cellular component).

* Genes on the ENCODE portal are imported from and synced with NCBI Entrez Gene database. Only a subset of genes, which have Entrez GeneID as well as ID and symbol from official nomenclature, are used and maintained here. New genes to be added should comply with this requirement.
