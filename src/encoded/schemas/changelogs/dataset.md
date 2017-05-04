## Changelog for dataset.json

### Schema version 11

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % $ ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 10

* *description*, *notes*, and *submitter_comment* are now not allowed to have any leading or trailing whitespace
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