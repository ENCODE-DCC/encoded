## Changelog for rnai.json

### Schema version 5

* *sequence_information* is an array of objects with paired *rnai_sequence* and *rnai_target_sequence* properties so more than one set can be specified at a time, if applicable. Old properties *rnai_sequence* and *rnai_target_sequence* were removed
and the values were migrated into *sequence_information*.

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* array properties *aliases* and documents will only allow for unique elements.