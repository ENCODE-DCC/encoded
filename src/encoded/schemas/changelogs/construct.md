## Changelog for construct.json

### Deprecated object, removed in v66/67

### Schema version 6

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]
    
### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* *notes*, *description*, *submitter_comment* are no longer allowed to have any leading or trailing whitespace.

### Schema version 3

* Array properties *aliases* and *documents* were updated to allow for only unique elements within them.
