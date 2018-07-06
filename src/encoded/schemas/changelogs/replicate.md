## Changelog for replicate.json

### Schema version 10

* *biological_replicate_number*, *technical_replicate_number*, and *rbns_protein_concentration* were set to have a minimum of 0.

### Schema version 9

* Remove standard_status mixin.
* Remove *proposed* and *preliminary* from local status enum.

### Schema version 8

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* array property *aliases* is now only allowed to contain unique elements

### Schema version 5

* *platform* was removed and migrated to file
* *read_length* was removed and migrated to file
* *read_length_units* was removed
* *paired_ended* was removed and migrated to file.run_type

### Schema version 4

* *flowcell_details* was removed and migrated to file.  For replicates without files, this information was stored in *notes*

### Schema version 3

* *status* was brought in line with the standard status for unaccessioned objects::

	    "enum" : [
	        "in progress",
	        "deleted",
	        "replaced",
	        "released"
	    ]
   
