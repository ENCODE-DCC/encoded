## Changelog for experiment.json

### Schema version 13

* *biosample_type* is a required field
* *biosample_term_id* is required for experiments with *biosample_type* != "in vitro sample"  * *biosample_type* and *biosample_term_id* consistency added to the list of schema dependencies

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