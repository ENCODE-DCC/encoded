## Change log for antibody_characterization.json

### Schema version 11

* *comment* has been replaced with *submitter_comment*

### Schema version 10
    
* *biosample_type* and *biosample_term_id* consistency added to the list of schema dependencies

### Schema version 9

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 8

* *comment*, *notes*, *submitter_comment*, and *caption* are no longer allowed to have leading or trailing whitespace

### Schema version 7

* Array properties *aliases*, *references* and *documents* were updated to allow for only unique elements within them.
