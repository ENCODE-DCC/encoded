## Changelog for human_donor.json

### Schema version 10

* *fraternal_twin* and *identical_twin* fields were replaced by *twin* field
* *twin_type* property was added to allow specification of the twin type if it is known
* *ethnicity* values are no longer free text, and now have to be selected from enum list
* *life_stage* values 'postnatal' and 'fetal' were removed
* *children* property is calculated property and should not be submitted anymore

### Schema version 9

* *status* values "proposed" and "preliminary" were removed
* *status* and *dbxrefs* values are restricted to DCC access only
* *mutagen* property is restricted to model organisms only

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCDO..." or "TSTDO..."