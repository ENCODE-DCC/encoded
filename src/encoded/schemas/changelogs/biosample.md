## Changelog for biosample.json

### Minor changes since schema version 24

* Added *post_differentiation_time* and *post_differentiation_time_units* properties.

### Schema version 24

* Remove biosample_type, biosample_term_id and biosample_term_name.

### Schema version 23

* Link to BiosampleType object.

### Schema version 22

* Removed *induced pluripotent stem cell line* and *stem cell* from biosample_type enums.

### Minor changes since schema version 21

* *passage_number* was set to have a minimum of 0.
* *PMI* was set to have a minimum of 1.
* Added preservation_method to the calculated property of summary.

### Schema version 21

* Added *organoid* to biosample_type enums.

### Minor changes since schema version 20

* Added *single cell* to biosample_type enums
* Added *cell_isolation_method* property for specification of cell isolation method, it could be one of the followings enums: micropippeting, microfluidic cell sorting, dilution, laser capture microdissection or fluorescence activated cell sorting. The property can not be used with biosample_type whole organisms or tissue

### Schema version 20

* Replace *immortalized cell line* with *cell line* in biosample_type enum

### Minor changes since schema version 19

* *PMI* and *PMI_units* were added as new properties, with dependencies enforcing their interdependent use.
* *PMI* and *PMI_units* are additionally restricted to only be used for tissue biosamples.
* *culture_harvest_date* and *culture_start_date* no longer can be used for tissues (a mistake introduced recently and now corrected within the dependencies).
* Sample property *preservation_method* with enums ["cryopreservation", "flash-freezing"] was added.
* Add nih_institutional_certification property for storing biosample institutional certification.

### Schema version 19

* Links to *constructs* and *rnais* via those properties of the same name have been removed.
* *transfection_method* and *transfection_type* have also been removed.
* *genetic_modifications* and *model_organism_donor_modifications* are no longer embedded, only *applied_modifications* (the combination of both those property values) will remain embedded

### Schema version 18

* *biosample_type*, *biosample_term_id* and *biosample_term_name* properties are required, consistency between the type and ontology term_id is validated by schema dependency

### Schema version 17

* *status* value "proposed" was removed


### Schema version 16

* *talens* array was removed, as we are migrating towards the use of genetic_modification with modification_technique specifications
* *treatments* array is required to be non-empty if post_treatment_time_units or post_treatment_time are specified
* *dbxrefs* property was restricted to DCC access only
* *pooled_from* array requires at least two entries to be specified
* *phase* property is restricted to biosamples with biosample_type one of ["primary cell", "immortalized cell line", "in vitro differentiated cells", "stem cell", "induced pluripotent stem cell line"]
* *culture_harvest_date*, *culture_start_date* propeties are restricted to biosamples with biosample_type one of ["primary cell", "immortalized cell line", "in vitro differentiated cells", "stem cell", "induced pluripotent stem cell line", "tissue"] and their format is limited now to only *date* and not one of ["date", "date-time"] as it used to be
* *transfection_method* specification requires specirfication of *transfection_type*
* *post_synchronization_time* specification requires specification of *post_synchronization_time_units* and *fly_synchronization_stage* or *worm_synchronization_stage*
* *status* value "preliminary" was removed
* *date_obtained* format is limited now to only *date* and not one of ["date", "date-time"] as it used to be
* *derived_from* property was renamed to *originated_from*
* *alternate_accessions* now must match accession format, "ENCBS..." or "TSTBS..."

### Schema version 15

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias


### Schema version 14

* *depleted_in_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the term_name
* *subcellular_fraction_term_id* is not longer allowed to be submitted, it will be automatically calculated based on the term_name
* *depleted_in_term_name* array can now only contain unique elements
* *notes*, *description*, *submitter_comment*, *product_id* and *lot_id* are no longer allowed to have any leading or trailing whitespace.

### Schema version 13

* *note* was removed and values were copied over to *submitter_comment*
* *starting_amount* requires *starting_amount_units* and vice versa
* *starting_amount* was previously a mixed type property (string, number), only numbers are allowed now
* *model_organism_age* requires *model_organism_age_units* and vice versa
* *model_organism_age*, *model_organism_age_units*, *model_organism_sex*, *model_organism_mating_status* and *model_organism_health_status* properties all are restricted from use in human biosamples.
* *post_synchronization_time* and *post_synchronization_time_units* are restricted from use in human and mouse biosamples.
* *protocol_documents* was renamed to *documents*

### Schema version 12

* *host* was added 
* *constructs* were updated to be an array of unique entries
* *rnais* were updated to be an array of unique entries
* *talens* were updated to be an array of unique entries
* *treatments* were updated to be an array of unique entries
* *protocol_documents* were updated to be an array of unique entries
* *pooled_from* were updated to be an array of unique entries
* *dbxrefs* were updated to be an array of unique entries
* *aliases* were updated to be an array of unique entries
* *references* were updated to be an array of unique entries

### Schema version 11

* *worm_synchronization_stage* enum was renamed to "L1 larva starved after bleaching" from "starved L1 larva"

### Schema version 8

* *worm_life_stage* enum was renamed to "mixed stage (embryonic))" from "embryonic"

### Schema version 6

* *biosample_type* enum was renamed to "primary cell" from "primary cell line"

### Schema version 3

* *subcellular_fraction* property was split into *subcellular_fraction_term_id* and *subcellular_fraction_term_name*

### Schema version 2

* *starting_amount* property was converted to take number values from string values
