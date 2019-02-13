## Changelog for genetic_modification_characterization.json

### Minor changes since schema version 4 

* *size*, *width*, and *height* in *attachment* were set to have a minimum of 0.
* *review* has been added to the schema to allow other lab to review the characterization.

### Schema version 4

* *comment* has been replaced with *submitter_comment*

### Schema version 3

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]
