## Changelog for target.json

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* Array properties *aliases*, *dbxref*, and *investigated* were updated to allow for only unique elements within them.

### Schema version 3

* *investigated_as* property was backfilled to assign existing targets the appropriate enums according to what the target was being investigated as within an assay

### Schema version 2

* *status* values were changed to be lowercase