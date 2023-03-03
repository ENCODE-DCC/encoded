## Changelog for functional_characterization_experiment.json

### Schema version 13

* Upgraded *internal_tags* as follows:
    * *ENCYCLOPEDIAv3* is now *ENCYCLOPEDIAv0.3*
    * *ENCYCLOPEDIAv4* is now *ENCYCLOPEDIAv1*
    * *ENCYCLOPEDIAv5* is now *ENCYCLOPEDIAv2*
    * *ENCYCLOPEDIAv6* is now *ENCYCLOPEDIAv3*

### Minor changes since schema version 12
* Added *genomic perturbation followed by RT-qPCR* enum to *assay_term_name*
* Added *biosamples* calculated property
* Added *Degron* to *internal_tags* enums list.

### Schema version 12
* The assay_term_names are now more specific for CRISPR screens based on the readout. All of these assays will slim to CRISPR screen in the field assay_slims
** proliferation CRISPR screen
** FlowFISH CRISPR screen
** FACS CRISPR screen

### Schema version 11
* An *expression_measurement_method* selection is now required for all *examined_loci* entries
* The *CRISPRi-FlowFISH* enum in *expression_measurement_method* has been removed, *PrimeFlow* is to be used instead

### Minor changes since schema version 10
* Added *Deeply Profiled* to the *internal_tags* enum
* Added *bio_replicate_count* and *tech_replicate_count* for the respective counts of the embedded replicates as a calculated property
* Added *biological_replicates* with a formatted text version of biological replicates as a calculated property
* Added a calculated boolean property *datapoint* 

### Schema version 10
* The pooled clone sequencing assay term name requires specification of the control_type

### Schema version 9
* *elements_mapping* property was replaced by an array *elements_mappings*

### Minor changes since schema version 8
* Added *simple_biosample_summary* truncated version of biosample_summary as calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *fluorescence activated cell sorting* and *CRISPRi-FlowFISH* enum to *expression_measurement_method* property of *examined_loci*.

### Schema version 8
* The *HCR-FlowFish* enum in *expression_measurement_method* has been adjusted to *HCR-FlowFISH*

### Minor changes since schema version 7

* Added *ENCYCLOPEDIAv6* to *internal_tags* enums list

### Schema version 7

* Changed the *analysis_objects* property to be *analyses*
* Added *expression_measurement_method* to the *examined_loci* property

### Minor changes since schema version 6

* Restricted submission of *target* property to admins only.
* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property
* Added *analysis_objects* property
* Added *perturbation followed by scRNA-seq* and *perturbation followed by snATAC-seq* to *assay_term_name* enum

### Schema version 6

* *plasmids_library_type* value *other* was removed.

### Schema version 5

* Made *biosample_ontology* a required property.

### Minor changes since schema version 4

* Added *examined_loci* property.

### Schema version 4

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 3

* Added *elements_cloning* property.
* Added *plasmids_library_type* property that is required to specify the purpose of pooled clone sequencing experiments.

### Schema version 2

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 1

* Allowed *elements_references* to link to Annotation objects in addition to Reference objects.
* Added *control_type*
* Removed *month_released* calculated property.
* Added *target_expression_percentile* property.
* Added *related_series* property.
