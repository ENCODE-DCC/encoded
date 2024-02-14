## Changelog for aggregate_series.json

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
* Added *assay_slims* calculated property
* Added *ENCYCLOPEDIAv6* to *internal_tags* enums list
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property
* Added *Deeply Profiled* to the *internal_tags* enum
* *related_datasets* now includes FunctionalCharacterizationExperiment.json and TransgenicEnhancerExperiment.json
* Removed *control_type* calculated property
* Added *Degron* to *internal_tags* enums list
* Added *related_series* property

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 1
* Removed *month_released* calculated property.
