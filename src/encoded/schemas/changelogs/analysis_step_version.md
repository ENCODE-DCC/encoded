## Changelog for analysis_step_version.json

### Minor changes since schema version 4

* *minor_version* was set to have a minimum of 0.

### Schema version 4

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]
* *version* property has been renamed to *minor_version* and allowed to start from 0
* *name* has been added as a calculated name made up of the analysis step label, major and minor version numbers.


### Schema version 3

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 2

* *software_versions* is now a required property.
