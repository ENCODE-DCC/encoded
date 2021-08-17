## Changelog for antibody_lot.json

### Schema version 10
* Modified regex pattern for *lot_id* and *product_id* to disallow blank strings.

### Minor changes since schema version 9

* Added *single cell* to *biosample_type* enums
* Added *used_by_biosample_characterizations* to reversely link to biosample characterizations using the antibody
* Added *control_type*. Either *control_type* + *isotype* or *targets* is required. And they are mutually exclusive. 

### Schema version 9

* *status* is restricted to DCC access only

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCLB..." or "TSTLB..."

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* Free text properties *notes* and *antigen_description* are no longer allowed to have leading or trailing whitespace or allowed to contain just an empty string.

### Schema version 5

* Array properties *purifications*, *targets*, *lot_id_alias*, *dbxrefs*, and *aliases* were updated to allow for only unique elements within them.
