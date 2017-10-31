## Changelog for fly_donor.json

### Schema version 9

* *parent_strains* list property was added and limited to maximum 2 entries of strains of the same organism

### Schema version 8

* *constructs*, *mutated_gene* and *mutagen* properties were removed

### Schema version 7

* *url* property was removed
* *internal_tags* property was removed

### Schema version 6

* *status* values "proposed" and "preliminary" were removed
* *status* and *dbxrefs* values are restricted to DCC access only


### Schema version 5

* *alternate_accessions* now must match accession format, "ENCDO..." or "TSTDO..."

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* *donor_documents* was removed from the schema as it was replaced by *documents*.

### Schema version 2

* Array properties *aliases*, *dbxrefs*, *documents* and *constructs* were updated to allow for only unique elements within them.
