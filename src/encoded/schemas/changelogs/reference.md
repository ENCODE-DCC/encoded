## Changelog for reference.json

### Minor changes since schema version 19

* *related_pipelines* property was added to link relevant pipelines to their corresponding reference fileset 
* *reference_type* was updated to include the enum *sequence barcodes*
* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *analyses* property
* Added *RushAD* to the *internal_tags* enum

### Schema version 19

* Adjusted the default schema to not specify *examined_loci* property automatically.

### Minor changes since schema version 18

* *Examined_loci* property may now be specified in references that are *reference_type*: *functional elements*.
* *Donor* property may now be specified in references that are *reference_type*: *genome*

### Schema version 18

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 17

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 16

* *functional elements* is added to the enums list of *reference_type* property
* Added *MouseDevSeries* enum to *internal_tags*
* *reference_type* was updated to include the enum *sequence adapters*
* Removed *month_released* calculated property.

### Schema version 16

* *internal_tags* removes cre_inputv10 and cre_inputv11, and adds ENCYCLOPEDIAv5, ccre_inputv1, and ccre_inputv2.

### Schema version 15

* Replace *started* enum in *status* with *in progress*.

### Schema version 14

* Replace the *status* field value *ready for review* by *submitted*. Make the *status* field editable by DCC personnel only.

### Schema version 13

* Remove *proposed* from *status* enum (*dataset* mixin).

### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."
