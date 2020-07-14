## Changelog for publication.json

### Schema version 9
* The *datasets* property is no longer submittable on this object; other dataset objects should specify a publication in their own *references* property and the dataset will appear on the publication.

### Schema version 8
* The *date_published* property is now restricted to a numerical year-month-day date format (e.g., 2020-07-08). The *notes* property is also now available.


### Minor changes since schema version 7
* The *documents* property is now available to provide relevant documents associated with the Publication.


### Schema version 7

* Add *publication_data* to reversely link to PublicationData using the references
* Restrict *datasets* to Experiment, Annotation, FunctionalCharacterizationExperiment and Reference

### Schema version 6

* Changed available enum options for *status* from *in preparation*, *submitted*, *published* and *deleted* to *in progress*, *released* and *deleted*, where *in preparation* and *submitted* now map to *in progress* and *published* now maps to *released*.

### Schema version 5

* Remove *in press*, *in revision*, *planned*, *replaced* from *status*


### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* array properties *identifers*, *datasets*, *categories*, and *published_by* will now only allow for unique elements.

### Schema version 2

* *references* property was renamed to *identifiers*
