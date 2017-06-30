## Changelog for antibody_lot.json

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCLB..." or "TSTLB..."

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* Free text properties *notes* and *antigen_description* are no longer allowed to have leading or trailing whitespace or allowed to contain just an empty string.

### Schema version 5

* Array properties *purifications*, *targets*, *lot_id_alias*, *dbxrefs*, and *aliases* were updated to allow for only unique elements within them.
