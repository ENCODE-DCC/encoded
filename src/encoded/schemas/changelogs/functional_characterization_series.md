## Changelog for functional_characterization_series.json

### Minor changes since schema version 3

* Removed *control_type* from facet_groups; unintentionally added
* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *analyses* property
* Added *assay_slims* calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property
* Added *Deeply Profiled* to the *internal_tags* enum
* Added a calculated boolean property *datapoint* 

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number
