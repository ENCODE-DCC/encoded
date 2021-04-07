## Changelog for award.json

### Schema version 9

* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *milestones.assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively

### Minor changes since schema version 8
* Added *CUT&RUN* to *milestones.assay_term_name* enum
* Added *SPRITE-IP* to *milestones.assay_term_name* enum
* Added *CUT&Tag* to *milestones.assay_term_name* enum
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *milestones.assay_term_name* enum

### Schema version 8

* *assay_term_name* enum *single cell isolation followed by RNA-seq* was changed to *single-cell RNA sequencing assay*

### Schema version 7

* *assay_term_name* enum *single-nuclei ATAC-seq* was changed to *single-nucleus ATAC-seq*

### Schema version 6
* *title* is now a required property

### Minor changes since schema version 5
* *component* was added to enable denoting functional characterization awards

### Schema version 5

* *status* property was restricted to one of  
    "enum" : [
        "current",
        "deleted",
        "disabled"
    ]

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* Broke out enum value *ENCODE* in *viewing_group* to *ENCODE3* and *ENCODE4*

### Schema version 2

* Default values of '' were removed. You can no longer submit a blank url (url='')

* *status* was brought into line with other objects that are shared. Disabled grants with rfa in ['ENCODE2', 'ENCODE2-Mouse']:

        "enum" : [
            "current",
            "deleted",
            "replaced",
            "disabled"
        ]
