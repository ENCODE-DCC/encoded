## Changelog for duplicates_quality_metric.json

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* array properties *assay_term_id* and *notes* will now only allow for unique elements.