## Changelog for single_cell_rna_series.json

### Schema version 4

* Upgraded *internal_tags* as follows:
    * *ENCYCLOPEDIAv3* is now *ENCYCLOPEDIAv0.3*
    * *ENCYCLOPEDIAv4* is now *ENCYCLOPEDIAv1*
    * *ENCYCLOPEDIAv5* is now *ENCYCLOPEDIAv2*
    * *ENCYCLOPEDIAv6* is now *ENCYCLOPEDIAv3*

### Minor changes since schema version 3

* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property
* Added *analyses* property
* *related_datasets* now includes SingleCellUnit.json
* Added *assay_slims* calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property
* Added *Deeply Profiled* to the *internal_tags* enum
* *related_datasets* now includes FunctionalCharacterizationExperiment.json
* Removed *control_type* calculated property
* Added *Degron* to *internal_tags* enums list.

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number
