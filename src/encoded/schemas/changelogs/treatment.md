## Changelog for treatment.json

### Minor changes since schema version 11
* *product_id* and *source* properties were added using imports from mixins.json.
* *stimulation* was added to the enum list for the *treatment_type* property in mixins.json.
* *purpose* property was added
* *μg/kg* can now be specified as amount units.

### Schema version 11

* *lab* property was removed

### Schema version 10

* *status* property was restricted to one of  
    "enum" : [
        "released",
        "deleted",
        "in progress"
    ]

### Schema version 9

* The regex for *treatment_term_name* will now accept the namespace "UniProtKB" rather than "UniprotKB".

### Schema version 8

* *status* property was restricted to one of  
    "enum" : [
        "current",
        "deleted",
        "disabled"
    ]

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* *notes* field is no longer allowed to have any leading or trailing whitespace

### Schema version 5
 
* *duration_units* is now required for *duration* and vice versa
* *concentration* and *concentration_units* were renamed to *amount* and *amount_units*
* *amount_units* is now required for *amount* and vice versa
* *antibodies* was renamed to *antibodies_used*
* *protocols* were renamed to *documents*

### Schema version 4

* *antibodies* was added 
* *biosamples_used* was added 
* *aliases* were updated to be an array of unique entries
* *dbxrefs* were updated to be an array of unique entries
* *protocols* were updated to be an array of unique entries
