## Changelog for document.json

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

* Free-text fields *notes* and description are no longer allowed to have leading or trailing whitespace or contain just an empty string.

### Schema version 5

* Array properties *aliases*, *urls*, and *references* were updated to allow for only unique elements within them.
