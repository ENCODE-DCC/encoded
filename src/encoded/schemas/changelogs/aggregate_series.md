## Changelog for aggregate_series.json

### Minor changes since schema version 3

* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property
* Added *analyses* property
* Added *assay_slims* calculated property
* Added *ENCYCLOPEDIAv6* to *internal_tags* enums list
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 1
* Removed *month_released* calculated property.
