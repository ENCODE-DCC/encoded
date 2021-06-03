## Changelog for mixins.json

### Minor changes since schema version 1

* *size*, *width*, and *height* in *attachment* were set to have a minimum of 0.
* Added *CUT&RUN* to *assay.assay_term_name* enum
* Added *SPRITE-IP* to *assay.assay_term_name* enum
* Added *CUT&Tag* to *assay.assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay.assay_term_name* enum
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay.assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *LC/MS label-free quantitative proteomics* and *LC-MS/MS isobaric label quantitative proteomics* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*
