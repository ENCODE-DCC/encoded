## Changelog for matched_set.json

### Minor changes since schema version 17

* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *analyses* property
* Added *assay_slims* calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property
* Added *ControlledCellGrowth* to the *internal_tags* enum

### Schema version 17

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 16

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 15
* Added *MouseDevSeries* enum to *internal_tags*
* Removed *month_released* calculated property.

### Schema version 15

* *internal_tags* removes *cre_inputv10* and *cre_inputv11*, and adds *ENCYCLOPEDIAv5*, *ccre_inputv1*, and *ccre_inputv2*.

### Schema version 14

* Replace *started* enum in *status* with *in progress*.

### Schema version 13

* Remove *proposed* from *status* enum (*dataset* mixin).

### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."

### Schema version 11

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 10

* *description*, *notes*, and *submitter_comment* are now not allowed to have any leading or trailing whitespace
* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the *term_name*

### Schema version 9

* *status* enum was restricted to:
    "enum" : [
        "proposed",
        "started",
        "submitted",
        "ready for review",
        "deleted",
        "released",
        "revoked",
        "archived",
        "replaced"
    ]

### Schema version 8

* Array properties *aliases*, *dbxrefs*, *documents*, and *references* were updated to allow for only unique elements within them.
