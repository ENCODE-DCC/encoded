Change log for library.json
===========================


Schema version 4
----------------

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

Schema version 3
----------------

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
