## Change log for hic_quality_metric.json

### Minor changes since schema version 2

* Removed the dependencies on *run_type* for *1_alignment*, *pct_1_alignment*, *pct_2_alignment_duplicates*, and *pct_2_alignment_unique*
* Added *proliferation CRISPR screen* to *assay_term_name* enum

### Schema version 2

* Renamed *alignable_normal_and_chimeric_paired*, *chimeric_ambiguous*, *chimeric_paired*, *duplicates*, *normal_paired*, *pct_alignable_duplicates*, *pct_alignable_normal_and_chimeric_paired*, *pct_alignable_unique_reads*, *pct_chimeric_ambiguous*, *pct_chimeric_paired*, *pct_normal_paired*, *pct_sequenced_total_duplicates*, *pct_sequenced_unique_reads*, *pct_single_alignment*, *pct_unmapped_reads*, *single_alignment*, *unique_reads*, *unmapped_reads* to be *2_alignments*, *3_or_more_alignments*, *2_alignments_a1_a2b_a1b2_b1a2*, *total_duplicates*, *2_alignments_a_b*, *pct_2_alignment_duplicates*, *pct_2_alignments*, *pct_2_alignment_unique*, *pct_3_or_more_alignments*, *pct_2_alignments_a1_a2b_a1b2_b1a2*, *pct_2_alignments_a_b*, *pct_sequenced_total_duplicates*, *pct_sequenced_total_unique*, *pct_1_alignment*, *pct_one_or_both_reads_unmapped*, *1_alignment*, *total_unique*, *one_or_both_reads_unmapped* respectively.
* Added *read_type* property and has dependencies.
* Added *2_alignment_duplicates*, *2_alignment_unique*, *no_chimera_found*, *pct_no_chimera_found*, *0_alignments*, *pct_0_alignments*, *pct_1_alignment_unique*, *pct_1_alignment_duplicates*, *pct_sequenced_1_alignment_unique*, *pct_sequenced_1_alignment_duplicates*, *pct_sequenced_2_alignment_unique*, *pct_unique_total_duplicates*, *pct_sequenced_total_unique*, *library_complexity_estimate_1_alignment*, *library_complexity_estimate_2_alignment*, *library_complexity_estimate_1_and_2_alignments*, *pct_sequenced_2_alignment_duplicates*.
