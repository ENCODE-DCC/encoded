## Changelog for hotspot_quality_metric.json

### Schema version 7

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 6

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias
* *generated_by* field has been added as a required field, to distinguish between Hotspot1 and Hotspot2 scores.
* *SPOT2 score* field has been renamed from *SPOT score* to show it was calculated by Hotspot2.
* *SPOT1 score* field has been added for scores as calculated by Hotspot1.
* *total tags* and *hotspot tags* fields have been added to characterize Hotspot1 methods"

### Schema version 5

* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the term_name
* *notes* field is no longer allowed to have leading or trailing whitespace or contain just an empty string.