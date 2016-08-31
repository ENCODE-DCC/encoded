==============================
Change log for experiment.json
==============================

Schema version 10
-----------------

* *assay_term_name* is now a required property
* *assay_term_name* is now limited to the following set of possible values:

    "enum": [
        "ChIP-seq",
        "RNA-seq",
        "DNase-seq",
        "eCLIP",
        "shRNA knockdown followed by RNA-seq",
        "RNA Bind-n-Seq",
        "transcription profiling by array assay",
        "DNA methylation profiling by array assay",
        "whole-genome shotgun bisulfite sequencing",
        "RRBS",
        "siRNA knockdown followed by RNA-seq",
        "RAMPAGE",
        "comparative genomic hybridization by array",
        "CAGE",
        "single cell isolation followed by RNA-seq",
        "Repli-seq",
        "microRNA-seq",
        "microRNA counts",
        "MRE-seq",
        "RIP-seq",
        "Repli-chip",
        "MeDIP-seq",
        "ChIA-PET",
        "FAIRE-seq",
        "ATAC-seq",
        "PAS-seq",
        "RIP-chip",
        "RNA-PET",
        "genotyping by high throughput sequencing assay",
        "CRISPR genome editing followed by RNA-seq",
        "protein sequencing by tandem mass spectrometry assay",
        "5C",
        "HiC",
        "TAB-seq",
        "iCLIP",
        "DNA-PET",
        "Switchgear",
        "5' RLM RACE",
        "MNase-seq"
    ]
* *assay_term_id* is now limited to the following set of possible values to match with their corresponding *assay_term_names*:

    "enum": [
        "OBI:0000716",
        "OBI:0001271",
        "OBI:0001853",
        "NTR:0003027",
        "NTR:0000762",
        "OBI:0002044",
        "OBI:0001463",
        "OBI:0001332",
        "OBI:0001863",
        "OBI:0001862",
        "NTR:0000763",
        "OBI:0001864",
        "OBI:0001393",
        "OBI:0001674",
        "NTR:0003082",
        "OBI:0001920",
        "OBI:0001922",
        "NTR:0003660",
        "OBI:0001861",
        "OBI:0001857",
        "OBI:0001915",
        "OBI:0000693",
        "OBI:0001848",
        "OBI:0001859",
        "OBI:0002039",
        "OBI:0002045",
        "OBI:0001918",
        "OBI:0001850",
        "OBI:0001247",
        "NTR:0003814",
        "OBI:0001923",
        "OBI:0001919",
        "OBI:0002042",
        "NTR:0002490",
        "OBI:0002043",
        "OBI:0001849",
        "NTR:0000612",
        "NTR:0001684",
        "OBI:0001924"
    ]


Schema version 9
----------------

* *status* enum was restricted to:
    "enum" : [
        "proposed",
        "started",
        "submitted",
        "ready for review",
        "deleted",
        "released",
        "revoked",
        "archived",
        "replaced"
    ]


Schema version 8
----------------

* Array properties *possible_controls*, *dbxrefs*, *aliases*, *references*, and *documents* were updated to allow for only unique elements within them.


Schema version 5
----------------

* *biosample_type* enum value changed from 'primary cell line' to 'primary cell'.
