## Changelog for library.json

### Schema version 14

* Added dependency that does not allow *nucleic_acid_term_name* and *depleted_in_term_name* to have the same value of *polyadenylated mRNA*.

### Schema version 13

* The *adapter* enum list of *type* options was adjusted to make sequencing adapters specific to each read; now *read1 5' adapter*, *read2 5' adapter*, *read1 3' adapter*, and *read2 3' adapter* are available.

### Schema version 12

* *chemical (HindIII/DpnII restriction)* was removed from *fragmentation_methods* enum.
* *NucleoBond Xtra Midi kit (Machery-Nagel cat#: 740410)* was added to the *extraction_method* enum.

### Minor changes since schema version 11

* The properties *fragmentation_duration_time* and *fragmentation_duration_time_units* were added.
* *chemical (NEBNext Ultra II Directional)* was added to the *fragmentation_methods* enum, and *Animal tissue kit (Norgen Biotek cat#: 25700)* was added to the *extraction_method* enum.
* *adapters* property is modified to allows specification of adapters as strings.
* The properties *average_fragment_size*, *fragment_length_CV*, and *fragment_length_SD* were added.

### Schema version 11

The boolean property *strand_specificity* has been converted to enum; this now allows strandedness to be specified as forward or reverse.

### Schema version 10

The properties *extraction_method*, *lysis_method*, and *library_size_selection_method* were converted to enum, and multiple descriptions or wordings of a specific category were collapsed into single entries. Entries that didn't add substantive information (e.g., "see document" or "n/a") were removed. 
* *extraction_method* now has enum:
```
    "enum": [
        "Ambion mirVana",
        "ATAC-seq (Greenleaf & Chang Lab protocol)",
        "C1 fluidigm",
        "Maxwell 16 LEV simpleRNA Cells Kit (Promega cat#: AS1270)",
        "miRNeasy Mini kit (QIAGEN cat#:217004)",
        "QIAGEN DNeasy Blood & Tissue Kit",
        "Qiagen RNA extraction",
        "RNeasy",
        "RNeasy Lipid Tissue Mini Kit (QIAGEN cat#74804)",
        "RNeasy Plus Mini Kit Qiagen cat#74134 plus additional on column Dnase treatment",
        "Trizol",
        "Zymo Quick-DNA MicroPrep (D3021)"
        ]

    "comment": "Historical extraction methods, not valid for new submissions.",
    "enum": [
        "TruChIP chromatin shearing reagent kit Covaris cat# 520154, sonication Covaris M220, IP (home protocol), DNA isolation with QIAquick PCR Purification Kit cat# 28104.",
        "SDS"
        ]
```
* *lysis_method* now has enum:
```
    "enum": [
        "ATAC buffer",
        "Clontech UltraLow for Illumina sequencing",
        "RIPA",
        "SDS"
        ]

    "comment": "Historical lysis methods, not valid for new submissions.",
    "enum": [
        "QIAGEN DNeasy Blood & Tissue Kit",
        "[NPB (5% BSA (Sigma), 0.2% IGEPAL-CA630 (Sigma), cOmplete (Roche), 1mM DTT in PBS)]",
        "0.01% digitonin",
        "72 degrees for 3 minutes in the presence of Triton"
        ]
```
* *library_size_selection_method* now has enum:
```
    "enum": [
        "agarose gel extraction",
        "AMPure XP bead purification",
        "BluePippin",
        "BluePippin 2-10Kb",
        "dual SPRI",
        "E-Gel",
        "gel",
        "gel followed by Amicon filters",
        "Invitrogen EGel EX 2% agarose (Cat# G402002)",
        "Pippin HT",
        "Sera-mag SpeedBeads",
        "SPRI beads"
        ]

    "comment": "Historical size selection methods, not valid for new submissions.",
    "enum": [
        "Only RNAs greater than 200 nucleotides. The inserts for the library will vary from ~ 100 - 700 base pairs.",
        "Only RNAs greater than 200 nucleotides. The insert for the library will vary from ~ 100 - 700 base pairs.",
        "SPRI beads AMPURE"
        ]
```
Preexisting entries not listed above were mapped to one of the enum as follows:
```
        'ATAC_buffer': 'ATAC buffer',
        'Ambion mirVana <200nt fraction': 'Ambion mirVana',
        'Possibly Trizol': 'Trizol',
        'Qaigen Kit DnEasy Blood and Tissue 69504': 'QIAGEN DNeasy Blood & Tissue Kit',
        'Trizol (LifeTech cat#: 15596-018)': 'Trizol',
        'Trizol (Invitrogen 15596-026)': 'Trizol',
        '[NPB(5%BSA(Sigma),0.2%IGEPAL-CA630(Sigma),cOmplete(Roche),1mMDTTinPBS)]': '[NPB (5% BSA (Sigma), 0.2% IGEPAL-CA630 (Sigma), cOmplete (Roche), 1mM DTT in PBS)]',
        'Agencourt AMPure XP': 'AMPure XP bead purification',
        'AMPUREXPbeads': 'AMPure XP bead purification',
        'SPRI Beads': 'SPRI beads',
        'SPRI_beads': 'SPRI beads',
        'SPRI': 'SPRI beads',
        'eGel': 'E-Gel',
        'eGEL': 'E-Gel',
        'Gel': 'gel',
        'Only RNAs greater than 200 nucleotides. The insert for the library was excised from an agarose gel': 'agarose gel extraction'
```

### Minor changes since schema version 9

* *queried_RNP_size_range* property is added, the property captures ribonucleoprotein size range targeted in the assay the library was constructed for.
* *adapters* property is added. The property is a list that captures information on adapters used during library preparation.
* *mint_mixture_identifier* property is added. The property allows specification of chromatin preps mixture identifier used in a MINT-ChIP experiments.

### Schema version 9

* *fragmentation_method* property was replaced by an array *fragmentation_methods*
* *fragmentation_date* value, if specified, would apply to all the listed fragmentation methods

### Minor changes since schema version 8

* *rna_integrity_number* property is added to capture RIN number.
* *barcode_details* property is added, the property contains barcode details of single cell samples.
* *construction_platform* property is added, the property contains link to platform used to prepare the library.

### Schema version 8

* *alternate_accessions* now must match accession format, "ENCLB..." or "TSTLB..."

### Schema version 7

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 6

* *nucleic_acid_term_id* will no longer be allowed to be submitted, it will be automatically calculated based on the *term_name*
* *depleted_in_term_id* will no longer be allowed to be submitted, it will be automatically calculated based on the *term_name*
* *depleted_in_term_name* will not default to an empty array and will only be present if a value is specified. It can now only contain unique elements.

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
