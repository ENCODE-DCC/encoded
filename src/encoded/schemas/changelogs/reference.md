## Changelog for reference.json

### Minor changes since schema version 22
* Added *variants* to *reference_type* enums list.

### Schema version 22

* Upgraded *internal_tags* as follows:
    * *ENCYCLOPEDIAv3* is now *ENCYCLOPEDIAv0.3*
    * *ENCYCLOPEDIAv4* is now *ENCYCLOPEDIAv1*
    * *ENCYCLOPEDIAv5* is now *ENCYCLOPEDIAv2*
    * *ENCYCLOPEDIAv6* is now *ENCYCLOPEDIAv3*

### Minor changes since schema version 21
* Added *experimental_input* property.
* Added *Degron* to *internal_tags* enums list.

### Schema version 21
* Renamed the *ATAC-seq*, *DNase-seq*, *transcription factors*, and *GRO-cap* enum of *elements_selection_method* to be *accessible genome regions*, *DNase hypersensitive sites*, *TF binding sites* and *transcription start sites* respectively.
* Renamed both *point mutations* and *single nucleotide polymorphisms* enum of *elements_selection_method* to be *sequence variants*.
* Added *chromatin states*, *histone modifications* and *synthetic elements* to the list of *elements_selection_method*.

### Minor changes since schema version 20
* Added *elements_selection_method* property to capture the selection of elements specified in references that are *reference_type*: *functional elements*
* Added *Deeply Profiled* to the *internal_tags* enum
* Added *crispr_screen_tiling* property to capture the CRISPR screen guide RNA design modalities that are *reference_type*: *functional elements*

### Schema version 20
* Updated the *internal_tags* enum from *RegulomeDB* to *RegulomeDB_1_0*
* Added *RegulomeDB_2_0* and *RegulomeDB_2_1* to the *internal_tags* enum list.

### Minor changes since schema version 19

* *related_pipelines* property was added to link relevant pipelines to their corresponding reference fileset 
* *reference_type* was updated to include the enum *sequence barcodes*
* Added *LRGASP* and *ENCYCLOPEDIAv6* to the *internal_tags* enums list
* Added *doi* property
* Added *analyses* property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *examined_regions* property so that chromosomal regions may be specified as regions of interest

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
