## Changelog for functional_characterization_experiment.json

### Minor changes since schema version 7

* Added  *ENCYCLOPEDIAv6* to *internal_tags* enums list

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
