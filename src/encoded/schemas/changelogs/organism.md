## Changelog for organism.json

### Schema version 5

* *status* property was restricted to one of  
    "enum" : [
        "released",
        "deleted",
        "in progress"
    ]

### Schema version 4

* *status* property was restricted to one of  
    "enum" : [
        "current",
        "deleted",
        "disabled"
    ]

### Schema version 3

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 2

* *status* values were changed to be lowercase
