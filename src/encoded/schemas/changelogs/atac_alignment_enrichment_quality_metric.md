## Change log for atac_alignment_enrichment_quality_metric.json

### Minor changes since schema version 2

* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively

### Schema version 2

* *fri_blacklist* was changed to *fri_exclusion_list*

### Minor changes since schema version 1

* *NSC* and *RSC* were updated to allow negative values
* *quality_metric_of* was set to have a minimum of 1.
* Move *fri_dhs*, *fri_blacklist*, *fri_prom* and *fri_enh* from atac_peak_enrichment_quality_metric to atac_alignment_enrichment_quality_metric
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *CUT&Tag* to *assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
