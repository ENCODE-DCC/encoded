## Changelog for sc_atac_alignment_quality_metric.json

### Schema version 3
* Updated the attachment *mito_stats* mime type to allow both TXT and TSV
* Added *genomic perturbation followed by RT-qPCR* to *assay_term_name* enum.
* Added *seqFISH* to *assay_term_name* enum.
* Added descriptions to all properties.
* Removed *usable_fragments* property

### Schema version 2

* Renamed *pct_properly_paired_reads*, *pct_mapped_reads*, *pct_singletons* to be *frac_properly_paired_reads*, *frac_mapped_reads*, *frac_singletons* respectively.