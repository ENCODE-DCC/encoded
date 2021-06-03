## Changelog for hotspot_quality_metric.json

### Minor changes since schema version 9
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *CUT&Tag* to *assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *LC/MS label-free quantitative proteomics* and *LC-MS/MS isobaric label quantitative proteomics* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*

### Schema version 9
* Standardized property names to remove spaces and capital letters.
* Added the following new properties: *five_percent_allcalls_count*, *five_percent_hotspots_count*, *five_percent_narrowpeaks_count*, and *tenth_of_one_percent_narrowpeaks_count*.

### Minor changes since schema version 8

* *quality_metric_of* was set to have a minimum of 1.

### Schema version 8

* *assay_term_name* enum *single-nuclei ATAC-seq* was changed to *single-nucleus ATAC-seq*

### Schema version 7

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 6

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias
* *generated_by* field has been added as a required field, to distinguish between Hotspot1 and Hotspot2 scores.
* *SPOT2 score* field has been renamed from *SPOT score* to show it was calculated by Hotspot2.
* *SPOT1 score* field has been added for scores as calculated by Hotspot1.
* *total tags* and *hotspot tags* fields have been added to characterize Hotspot1 methods"

### Schema version 5

* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the *term_name*
* *notes* field is no longer allowed to have leading or trailing whitespace or contain just an empty string.
