## Changelog for replicate.json

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
   
