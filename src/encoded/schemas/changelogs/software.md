## Changelog for software.json

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* array properties *aliases*, *software_type*, *purpose* and *used_by* will now only allow for unique elements.

### Schema version 2

* *lab* and *award* properties were added.