## Changelog for library.json

### Minor changes since schema version 8

* *barcode_details* property is added, the property contains barcode details of single cell samples.

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCLB..." or "TSTLB..."

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* nucleic_acid_term_id will no longer be allowed to be submitted, it will be automatically calculated based on the term_name
* depleted_in_term_id will no longer be allowed to be submitted, it will be automatically calculated based on the term_name
* depleted_in_term_name will not default to an empty array and will only be present if a value is specified. It can now only contain unique elements.

### Schema version 5

* Array values *spikeins_used*, *treatments*, *dbxrefs*, *aliases*, and *documents* are now only allowed to have unique elements.

### Schema version 4

* *paired_ended* was removed

* *fragmentation_method* was converted into an enum:

        "enum": [
            "chemical (generic)",
            "chemical (DnaseI)",
            "chemical (HindIII/DpnII restriction)",
            "chemical (Tn5 transposase)",
            "chemical (micrococcal nuclease)",
            "chemical (Illumina TruSeq)",
            "chemical (Nextera tagmentation)",
            "shearing (generic)",
            "shearing (Covaris generic)",
            "shearing (Covaris S2)",
            "sonication (generic)",
            "sonication (Bioruptor generic)",
            "sonication (Bioruptor Plus)",
            "sonication (Bioruptor Twin)",
            "see document",
            "none",
            "n/a"
        ]

### Schema version 3

* *spikeins_used* was added with an audit for RNA libraries missing this field:

        "spikeins_used": {
            "title": "Spike-ins datasets used",
            "description": "The datasets containing the fasta and the concentrations of the library spike-ins.",
            "type": "array",
            "default": [],
            "items" : {
                "title": "A spike-ins dataset.",
                "description": "A specific spike-ins type dataset",
                "comment": "See dataset.json for available identifiers.",
                "type": "string",
                "linkTo": "dataset"
            }
        },

*  *nucleic_acid_starting_quantity_units* enum was added to:

        "enum": [
            "cells",
            "cell-equivalent",
            "µg",
            "ng",
            "pg",
            "mg"
        ]

* *status* enum was brought in line with other accessioned objects::

        "enum": [
            "in progress",
            "deleted",
            "replaced",
            "released",
            "revoked"
        ]
