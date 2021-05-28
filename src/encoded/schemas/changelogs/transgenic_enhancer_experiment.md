## Changelog for transgenic_enhancer_experiment.json

### Minor changes since schema version 1

* Added *unidentified tissue* to the enum list for *tissue_with_enhancer_activity*.
* Added *element_location*, which specifies the chromosome and genomic coordinates of the element being tested.
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *CUT&Tag* to *assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *analyses* property
* Added *RushAD* to the *internal_tags* enum
