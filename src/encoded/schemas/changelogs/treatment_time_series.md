## Changelog for treatment_time_series.json

### Minor changes since schema version 18
* Updated schema description.
* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property
* Added *analyses* property

### Schema version 18

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 17

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 16
* Added *MouseDevSeries* enum to *internal_tags*
* Removed *month_released* calculated property.

### Schema version 16

* *internal_tags* removes *cre_inputv10* and *cre_inputv11*, and adds *ENCYCLOPEDIAv5*, *ccre_inputv1*, and *ccre_inputv2*.

### Schema version 15

* Replace *started* enum in *status* with *in progress*.

### Schema version 14

* Replace the *status* field value *ready for review* by *submitted*. Make the *status* field editable by DCC personnel only.

### Schema version 13

* Remove *proposed* from *status* enum (*dataset* mixin).

### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."
