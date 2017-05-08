## Changelog for award.json

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % $ ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* Broke out enum value "ENCODE" in viewing_group to ENCODE3 and ENCODE4

### Schema version 2

* Default values of '' were removed. You can no longer submit a blank url (url='')

* *status* was brought into line with other objects that are shared. Disabled grants with rfa in ['ENCODE2', 'ENCODE2-Mouse']:

        "enum" : [
            "current",
            "deleted",
            "replaced",
            "disabled"
        ]
