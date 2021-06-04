## Changelog for chip_alignment_enrichment_quality_metric.json

### Minor changes since schema version 1

* *NSC* and *RSC* were updated to allow negative values
* *quality_metric_of* was set to have a minimum of 1.
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *CUT&Tag* to *assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *LC/MS label-free quantitative proteomics*, *LC-MS/MS isobaric label quantitative proteomics*, and *Ribo-seq* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*
