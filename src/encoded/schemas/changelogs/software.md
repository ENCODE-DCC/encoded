## Changelog for software.json

### Minor changes since schema version 7
* Added *CUT&RUN* to *purpose* enum
* Added *SPRITE-IP* to *purpose* enum
* Added *CUT&Tag* to *purpose* enum


### Schema version 7

* *purpose* enum *single cell isolation followed by RNA-seq* was changed to *single-cell RNA sequencing assay*

### Schema version 6

* *purpose* enum *single-nuclei ATAC-seq* was changed to *single-nucleus ATAC-seq*

### Schema version 5

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* array properties *aliases*, *software_type*, *purpose* and *used_by* will now only allow for unique elements.

### Schema version 2

* *lab* and *award* properties were added.
