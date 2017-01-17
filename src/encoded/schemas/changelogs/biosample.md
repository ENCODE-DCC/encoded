=========================
Change log for biosample.json
=========================

Schema version 14
-----------------

* *depleted_in_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the term_name
* *subcellular_fraction_term_id* is not longer allowed to be submitted, it will be automatically calculated based on the term_name
* *depleted_in_term_name* array can now only contain unique elements
* *notes*, *description*, *submitter_comment*, *product_id* and *lot_id* are no longer allowed to have any leading or trailing whitespace.

Schema version 13
-----------------

* *note* was removed and values were copied over to *submitter_comment*
* *starting_amount* requires *starting_amount_units* and vice versa
* *starting_amount* was previously a mixed type property (string, number), only numbers are allowed now
* *model_organism_age* requires *model_organism_age_units* and vice versa
* *model_organism_age*, *model_organism_age_units*, *model_organism_sex*, *model_organism_mating_status* and *model_organism_health_status* properties all are restricted from use in human biosamples.
* *post_synchronization_time* and *post_synchronization_time_units* are restricted from use in human and mouse biosamples.
* *protocol_documents* was renamed to *documents*

Schema version 12
----------------

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
