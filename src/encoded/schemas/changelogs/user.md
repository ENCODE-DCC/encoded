## Changelog for user.json

### Schema version 6

* *phone1* removed
* *phone2* removed
* *fax* removed
* *skype* removed
* *google* removed

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* *viewing_group* enum value ENCODE was split into ENCODE3 and ENCODE4. Existing ENCODE users were assigned to ENCODE3.

### Schema version 3

* *status* values were changed to be lowercase
