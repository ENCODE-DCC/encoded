## Changelog for experiment_series.json

### Schema version 4

* Upgraded *internal_tags* as follows:
    * *ENCYCLOPEDIAv3* is now *ENCYCLOPEDIAv0.3*
    * *ENCYCLOPEDIAv4* is now *ENCYCLOPEDIAv1*
    * *ENCYCLOPEDIAv5* is now *ENCYCLOPEDIAv2*
    * *ENCYCLOPEDIAv6* is now *ENCYCLOPEDIAv3*

### Minor changes since schema version 3

* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *analyses* property
* Added *assay_slims* calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *Deeply Profiled* to the *internal_tags* enum
* Removed *control_type* calculated property
* Added *Degron* to *internal_tags* enums list.

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 1

* *related_datasets* was set to have a minimum of 1.
* Added *biosample_summary*
