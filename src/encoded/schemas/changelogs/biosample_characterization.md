## Changelog for biosample_characterization.json

### Minor changes since schema version 11 

* *review* has been added to the schema to allow other lab to review the characterization.
* *antibody* is added to the schema to indicate the antibody used in the characterization.

### Schema version 11

* *comment* has been replaced with *submitter_comment*

### Schema version 10

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]