## Changelog for genetic_modification.json

### Minor changes since schema version 7

* A minimum of 0 is set for *start* and *end* in *modified_site_by_coordinates*
* The dependency of *method* on *reagents* specification was changed, *reagents* are no longer required to be specified for the relevant types of modification methods.
* Zygosity is now required for modifications of *method* TALEN
* The *introduced_gene* property was added, and can satisfy the *category* dependencies for modifications of *category* insertion.
* *expression* was added to the *purpose* enum, and modifications with this *purpose* require *introduced_sequence* or *introduced_gene*.

### Schema version 7

* *purpose* property "validation" was renamed to "characterization", and "screening" was also added to the list of enums

### Schema version 6

* Genetic modifications are now accessioned objects with accessions starting with "ENCGM"
* *method* and *purpose* are now required properties
* *modification_type* has been renamed to *category*
* *target* has been renamed to *modified_site_by_target_id*
* linkOuts to CRISPR and TALEN objects have been removed, the relevant properties in those objects have been absorbed into this one and techniques are listed as enums within *method*
* *modified_site* has been renamed to *modified_site_by_coordinates*
* *source* and *product id* have been renamed to be an array of subobjects with those equivalent properties (*source* and *identifier*) within a property named *reagents*. Note that these values are meant to capture the reagents used to create the resultant modification.

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

* *modified_site* was renamed from *modification_genome_coordinates*
* if *modified_site* is used, all subproperties (*assembly*, *chromosome*, *start* and *end*) are required
* *description* was renamed from *modification_description*
* *purpose* was renamed from *modification_purpose*
* *zygosity* was renamed from *modification_zygocity*
* *treatments* was renamed from *modification_treatments*

### Schema version 2

* *modification_description* was renamed from *modifiction_description*
