## Changelog for experiment.json

### Schema version 25

* Remove biosample_type, biosample_term_id and biosample_term_name.

### Schema version 24

* *internal_tags* removes cre_inputv10 and cre_inputv11, and adds ENCYCLOPEDIAv5, ccre_inputv1, and ccre_inputv2.

### Schema version 23

* Link to BiosampleType object.

### Schema version 22

* Removed *induced pluripotent stem cell line* and *stem cell* from biosample_type enums.

### Schema version 21

* Added required property *experiment_classification* with enums "functional genomics assay" and "functional characterization assay"

### Minor changes since schema version 20

* *possible_controls* property allows specification of any type of Dataset as possible control

### Schema version 20

* Added *organoid* to biosample_type enums.

### Schema version 19

* Make *date_submitted* value a required property for objects in status *submitted*

### Schema version 18

* Replace started status with in progress.

### Schema version 17

* Replace the *status* field value *ready for review* by *submitted*. Make the *status* field editable by DCC personnel only.
* Added *single cell* to biosample_type enums

### Schema version 16

* Replace *immortalized cell line* with *cell line* in biosample_type enum

### Schema version 15

* The biosample_type enum "in vitro sample" has been renamed to "cell-free sample" and requires an accompanying biosample_term_id (of type NTR)

### Schema version 14

* Remove *proposed* from status enum (dataset mixin).

### Schema version 13

* *biosample_type* property is required
* *biosample_term_id* is required for all experiments except experiment with *biosample_type*  "in vitro sample", consistency between the biosample type and ontology term_id is validated by schema dependency


### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."
* *date_submitted* property was added to indicate when submission requirements were met. This value is assigned by the DCC.

### Schema version 11
    
* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias


### Schema version 10

* *assay_term_name* is now a required property
* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the term_name

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

* Array properties *possible_controls*, *dbxrefs*, *aliases*, *references*, and *documents* were updated to allow for only unique elements within them.


### Schema version 5

* *biosample_type* enum value changed from 'primary cell line' to 'primary cell'.
