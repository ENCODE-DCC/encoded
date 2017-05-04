## Changelog for fly_donor.json

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % $ ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* *donor_documents* was removed from the schema as it was replaced by *documents*.

### Schema version 2

* Array properties *aliases*, *dbxrefs*, *documents* and *constructs* were updated to allow for only unique elements within them.
