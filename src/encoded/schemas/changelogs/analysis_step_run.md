## Change log for analysis_step_run.json

### Schema version 3

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ ! $ ^ & | ~ ; ` and consecutive whitespaces will no longer be allowed in the alias

### Schema version 2

* *analysis_step_version* is now a required property.
