## Changelog for worm_donor.json

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* *donor_documents* was removed from the schema as it was replaced by *documents*.

### Schema version 2

* Array properties *aliases*, *dbxrefs*, *documents* and *constructs* were updated to allow for only unique elements within them.