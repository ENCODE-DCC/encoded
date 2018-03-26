## Changelog for experiment.json

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
