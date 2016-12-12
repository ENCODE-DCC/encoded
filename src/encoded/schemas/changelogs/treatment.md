=========================
 Change log for treatment.json
=========================

Schema version 5
----------------
 
* *duration_units* is now required for *duration* and vice versa
* *concentration* and *concentration_units* were renamed to *amount* and *amount_units*
* *amount_units* is now required for *amount* and vice versa
* *antibodies* was renamed to *antibodies_used*
* *protocols* were renamed to *documents*

Schema version 4
----------------

* *antibodies* was added 
* *biosamples_used* was added 
* *aliases* were updated to be an array of unique entries
* *dbxrefs* were updated to be an array of unique entries
* *protocols* were updated to be an array of unique entries