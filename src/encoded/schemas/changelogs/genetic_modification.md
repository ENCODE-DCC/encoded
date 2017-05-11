## Changelog for genetic_modification.json

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* *modified_site* was renamed from *modification_genome_coordinates*
* if *modified_site* is used, all subproperties (*assembly*, *chromosome*, *start* and *end*) are required
* *description* was renamed from *modification_description*
* *purpose* was renamed from *modification_purpose*
* *zygosity* was renamed from *modification_zygocity*
* *treatments* was renamed from *modification_treatments*

### Schema version 2

* *modification_description* was renamed from *modifiction_description*
