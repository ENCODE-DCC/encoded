## Changelog for gene_type_quantification_quality_metric.json

### Minor changes since schema version 2
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *CUT&Tag* to *assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *LC/MS label-free quantitative proteomics* and *LC-MS/MS isobaric label quantitative proteomics* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*

### Schema version 2

* The following properties were removed from the schema and will be reported in an attachment:
  - 3prime_overlapping_ncrna
  - IG_C_gene
  - IG_C_pseudogene
  - IG_D_gene
  - IG_J_gene
  - IG_J_pseudogene
  - IG_V_gene
  - IG_V_pseudogene
  - Mt_tRNA
  - TEC
  - TR_C_gene
  - TR_D_gene
  - TR_J_gene
  - TR_J_pseudogene
  - TR_V_gene
  - TR_V_pseudogene
  - bidirectional_promoter_lncrna
  - lincRNA
  - macro_lncRNA
  - misc_RNA
  - polymorphic_pseudogene
  - processed_pseudogene
  - pseudogene
  - tRNAscan
  - transcribed_processed_pseudogene
  - transcribed_unitary_pseudogene
  - transcribed_unprocessed_pseudogene
  - transcript_id_not_found
  - translated_unprocessed_pseudogene
  - unitary_pseudogene
  - unprocessed_pseudogene
  - vaultRNA

### Minor changes since schema version 1

* *quality_metric_of* was set to have a minimum of 1.
