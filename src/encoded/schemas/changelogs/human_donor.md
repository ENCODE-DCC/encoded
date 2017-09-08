## Changelog for human_donor.json

### Schema version 10

* *fraternal_twin* and *identical_twin* fields were collapsed into *twin* field
* *twin_type* property was added to allow specification of the twin type if it is known, it requires *twin*
* *ethnicity* values are no longer free text but are selected from an enumerated list
* *life_stage* values 'postnatal' and 'fetal' were removed and replaced by 'embryonic' and 'newborn' respectively
* *life_stage* value is required when *age* value is specified
* *children* property is now a calculated property using the parent fields of other objects. It should no longer be submitted
* *url* property was removed

### Schema version 9

* *status* values "proposed" and "preliminary" were removed
* *status* and *dbxrefs* values are restricted to DCC access only
* *mutagen* property is restricted to model organisms only

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCDO..." or "TSTDO..."
