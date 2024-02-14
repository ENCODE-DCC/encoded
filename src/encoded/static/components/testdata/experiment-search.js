module.exports = {
    single_type: {
        '@context': '/terms/',
        '@graph': [
            {
                '@id': '/experiments/ENCSR808QCJ/',
                '@type': [
                    'Experiment',
                    'Dataset',
                    'Item',
                ],
                accession: 'ENCSR808QCJ',
                assay_term_name: 'ATAC-seq',
                assay_title: 'ATAC-seq',
                award: { project: 'ENCODE' },
                biosample_ontology: { term_name: 'GM12878' },
                biosample_summary: 'GM12878',
                files: [
                    { '@id': '/files/ENCFF164JWT/' },
                    { '@id': '/files/ENCFF032OJW/' },
                    { '@id': '/files/ENCFF182CHA/' },
                ],
                lab: { title: 'Michael Snyder, Stanford' },
                replicates: [
                    {
                        library: {
                            biosample: {
                                age_units: 'year',
                                life_stage: 'adult',
                                accession: 'ENCBS630AAA',
                                organism: { scientific_name: 'Homo sapiens' },
                                age: '53',
                            },
                        },
                        biological_replicate_number: 1,
                        technical_replicate_number: 1,
                        '@id': '/replicates/0311d1e6-a141-4be4-a165-6abc6d320f05/',
                    },
                ],
                status: 'released',
            },
            {
                '@id': '/experiments/ENCSR751YPU/',
                '@type': [
                    'Experiment',
                    'Dataset',
                    'Item',
                ],
                accession: 'ENCSR751YPU',
                assay_term_name: 'DNase-seq',
                assay_title: 'DNase-seq',
                award: { project: 'Roadmap' },
                biosample_ontology: { term_name: 'midbrain' },
                biosample_summary: 'midbrain male adult (34 years)',
                files: [
                    { '@id': '/files/ENCFF477MLC/' },
                    { '@id': '/files/ENCFF000LBC/' },
                    { '@id': '/files/ENCFF000LBB/' },
                    { '@id': '/files/ENCFF000LBA/' },
                    { '@id': '/files/ENCFF000LAZ/' },
                    { '@id': '/files/ENCFF010LAO/' },
                ],
                lab: { title: 'John Stamatoyannopoulos, UW' },
                replicates: [
                    {
                        library: {
                            biosample: {
                                age_units: 'year',
                                life_stage: 'adult',
                                accession: 'ENCBS804RUL',
                                organism: { scientific_name: 'Homo sapiens' },
                                age: '34',
                            },
                        },
                        biological_replicate_number: 1,
                        technical_replicate_number: 1,
                        '@id': '/replicates/952fc6c6-f155-47e8-ab0f-d44d48880d11/',
                    },
                ],
                status: 'released',
            },
        ],
        '@id': '/search/?type=Experiment&status=released&assay_slims=DNA+accessibility',
        '@type': ['Search'],
        clear_filters: '/search/?type=Experiment',
        facets: [
            {
                terms: [
                    {
                        doc_count: 2,
                        key: 'Dataset',
                    },
                    {
                        doc_count: 2,
                        key: 'Experiment',
                    },
                ],
                type: 'terms',
                field: 'type',
                total: 2,
                title: 'Data Type',
                appended: false,
            },
            {
                terms: [
                    {
                        doc_count: 18,
                        key: 'DNA binding',
                    },
                    {
                        doc_count: 12,
                        key: 'Transcription',
                    },
                ],
                type: 'terms',
                field: 'assay_slims',
                total: 46,
                title: 'Assay type',
                appended: false,
            },
            {
                terms: [
                    {
                        doc_count: 2,
                        key: 'fastq',
                    },
                    {
                        doc_count: 1,
                        key: 'bam',
                    },
                    {
                        doc_count: 1,
                        key: 'bed narrowPeak',
                    },
                    {
                        doc_count: 1,
                        key: 'csfasta',
                    },
                    {
                        doc_count: 1,
                        key: 'csqual',
                    },
                ],
                type: 'terms',
                field: 'files.file_type',
                total: 2,
                title: 'Available file types',
                appended: false,
            },
            {
                terms: [
                    {
                        doc_count: 1,
                        key: 'GRCh38',
                    },
                ],
                type: 'terms',
                field: 'assembly',
                total: 2,
                title: 'Genome assembly',
                appended: false,
            },
        ],
        filters: [
            {
                field: 'status',
                remove: '/search/?type=Experiment&assay_slims=DNA+accessibility',
                term: 'released',
            },
            {
                field: 'assay_slims',
                remove: '/search/?type=Experiment&status=released',
                term: 'DNA accessibility',
            },
            {
                field: 'type',
                remove: '/search/?status=released&assay_slims=DNA+accessibility',
                term: 'Experiment',
            },
        ],
        notification: 'Success',
        sort: {
            date_created: {
                order: 'desc',
                unmapped_type: 'keyword',
            },
            label: {
                order: 'desc',
                unmapped_type: 'keyword',
            },
            uuid: {
                order: 'desc',
                unmapped_type: 'keyword',
            },
        },
        title: 'Search',
        total: 2,
    },

    multiple_types:
    {
        "@context": "/terms/",
        "@graph": [
            {
                "@id": "/functional-characterization-series/ENCSR000FCS/",
                "@type": [
                    "FunctionalCharacterizationSeries",
                    "Series",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR000FCS",
                "assay_term_name": [
                    "MPRA"
                ],
                "assay_title": [
                    "MPRA"
                ],
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/labs/thomas-gingeras/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {thomas-gingeras|/labs/thomas-gingeras/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/functional-characterization-series/ENCSR000FCS/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released functional characterization series {ENCSR000FCS|/functional-characterization-series/ENCSR000FCS/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": [
                    {
                        "term_name": "K562",
                        "classification": "cell line"
                    }
                ],
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "description": "MPRA experiments series.",
                "lab": {
                    "title": "Thomas Gingeras, CSHL"
                },
                "organism": [
                    {
                        "scientific_name": "Homo sapiens"
                    }
                ],
                "related_datasets": [
                    {
                        "examined_loci": [
                            {
                                "gene": {
                                    "symbol": "NR2F1"
                                }
                            },
                            {
                                "gene": {
                                    "symbol": "EBF1"
                                }
                            }
                        ],
                        "@id": "/functional-characterization-experiments/ENCSR222MPR/",
                        "replicates": [
                            {
                                "library": {
                                    "biosample": {
                                        "life_stage": "unknown"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "examined_loci": [
                            {
                                "gene": {
                                    "symbol": "NR2F1"
                                }
                            }
                        ],
                        "@id": "/functional-characterization-experiments/ENCSR333MPR/"
                    }
                ],
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR928SVL/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR928SVL",
                "assay_term_name": "STARR-seq",
                "assay_title": "STARR-seq",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/biosamples/ENCBS888RUL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released biosample {ENCBS888RUL|/biosamples/ENCBS888RUL/} has in progress subobject human donor {ENCDO000HUM|/human-donors/ENCDO000HUM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/files/ENCFF105SVF/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF105SVF|/files/ENCFF105SVF/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        },
                        {
                            "path": "/files/ENCFF021EEB/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF021EEB|/files/ENCFF021EEB/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR928SVL/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment contains a replicate [1,1] {31f76c7b-b6ac-4e06-b1d3-8907a4136ab1|/replicates/31f76c7b-b6ac-4e06-b1d3-8907a4136ab1/} without raw data associated files.",
                            "category": "missing raw data in replicate"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR928SVL/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR928SVL|/functional-characterization-experiments/ENCSR928SVL/} has no attached documents",
                            "category": "missing documents"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR928SVL/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment is expected to be replicated, but contains only one listed biological replicate.",
                            "category": "unreplicated experiment"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/files/ENCFF105SVF/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF105SVF|/files/ENCFF105SVF/}.",
                            "category": "missing analysis_step_run"
                        },
                        {
                            "path": "/genetic-modifications/ENCGM555KOT/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_genetic_modification_reagents",
                            "detail": "Genetic modification {ENCGM555KOT|/genetic-modifications/ENCGM555KOT/} of method CRISPR is missing reagents.",
                            "category": "missing genetic modification reagents"
                        },
                        {
                            "path": "/files/ENCFF021EEB/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF021EEB|/files/ENCFF021EEB/}.",
                            "category": "missing analysis_step_run"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": {
                    "term_name": "WTC-11",
                    "classification": "cell line"
                },
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "description": "STARR-seq on undifferentiated WTC11",
                "files": [
                    {
                        "@id": "/files/ENCFF105SVF/"
                    },
                    {
                        "@id": "/files/ENCFF021EEB/"
                    }
                ],
                "lab": {
                    "title": "Kevin White, UChicago"
                },
                "replicates": [
                    {
                        "library": {
                            "biosample": {
                                "organism": {
                                    "scientific_name": "Homo sapiens"
                                },
                                "life_stage": "unknown",
                                "accession": "ENCBS888RUL",
                                "age": "unknown"
                            }
                        },
                        "@id": "/replicates/31f76c7b-b6ac-4e06-b1d3-8907a4136ab1/",
                        "technical_replicate_number": 1,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR333MPR/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR333MPR",
                "assay_term_name": "MPRA",
                "assay_title": "MPRA",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/labs/thomas-gingeras/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {thomas-gingeras|/labs/thomas-gingeras/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR333MPR/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR333MPR|/functional-characterization-experiments/ENCSR333MPR/} has no attached documents",
                            "category": "missing documents"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR333MPR/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment is expected to be replicated, but currently does not have any replicates associated with it.",
                            "category": "unreplicated experiment"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR333MPR/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR333MPR|/functional-characterization-experiments/ENCSR333MPR/} does not contain any raw or processed data.",
                            "category": "lacking processed data"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": {
                    "term_name": "K562",
                    "classification": "cell line"
                },
                "description": "MPRA experiment with annotation elements_references",
                "examined_loci": [
                    {
                        "gene": {
                            "dbxrefs": [
                                "MIM:132890",
                                "HGNC:7975",
                                "ENSEMBL:ENSG00000175745",
                                "Vega:OTTHUMG00000119079",
                                "UniProtKB:P10589",
                                "RefSeq:NG_034119"
                            ],
                            "symbol": "NR2F1",
                            "organism": "/organisms/human/",
                            "synonyms": [
                                "BBOAS",
                                "BBSOAS",
                                "COUP-TFI",
                                "COUPTF1",
                                "EAR-3",
                                "EAR3",
                                "ERBAL3",
                                "SVP44",
                                "TCFCOUP1",
                                "TFCOUP1"
                            ],
                            "@type": [
                                "Gene",
                                "Item"
                            ],
                            "title": "NR2F1 (Homo sapiens)",
                            "uuid": "75866336-b42b-4341-9b70-240eb469c231",
                            "targets": [
                                "/targets/NR2F1%C3%82-human/"
                            ],
                            "schema_version": "2",
                            "geneid": "7025",
                            "name": "nuclear receptor subfamily 2 group F member 1",
                            "locations": [],
                            "@id": "/genes/7025/",
                            "ncbi_entrez_status": "live",
                            "status": "released"
                        },
                        "expression_measurement_method": "PrimeFlow",
                        "expression_percentile": 20
                    }
                ],
                "lab": {
                    "title": "Thomas Gingeras, CSHL"
                },
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR722STR/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR722STR",
                "assay_term_name": "STARR-seq",
                "assay_title": "STARR-seq",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/biosamples/ENCBS888RUL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released biosample {ENCBS888RUL|/biosamples/ENCBS888RUL/} has in progress subobject human donor {ENCDO000HUM|/human-donors/ENCDO000HUM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/files/ENCFF100ELE/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF100ELE|/files/ENCFF100ELE/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        },
                        {
                            "path": "/replicates/df1f6993-10ef-12e9-a913-1684be663d3e/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released replicate {df1f6993-10ef-12e9-a913-1684be663d3e|/replicates/df1f6993-10ef-12e9-a913-1684be663d3e/} has revoked subobject functional characterization experiment {ENCSR722STR|/functional-characterization-experiments/ENCSR722STR/}",
                            "category": "mismatched status"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR722STR/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR722STR|/functional-characterization-experiments/ENCSR722STR/} contains a library {ENCLB001MPR|/libraries/ENCLB001MPR/} linked to biosample type '{cell_line_EFO_0009747|/biosample-types/cell_line_EFO_0009747/}', while experiment's biosample type is '{cell_line_EFO_0002067|/biosample-types/cell_line_EFO_0002067/}'.",
                            "category": "inconsistent library biosample"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR722STR/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR722STR|/functional-characterization-experiments/ENCSR722STR/} has no attached documents",
                            "category": "missing documents"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/files/ENCFF100ELE/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF100ELE|/files/ENCFF100ELE/}.",
                            "category": "missing analysis_step_run"
                        },
                        {
                            "path": "/genetic-modifications/ENCGM555KOT/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_genetic_modification_reagents",
                            "detail": "Genetic modification {ENCGM555KOT|/genetic-modifications/ENCGM555KOT/} of method CRISPR is missing reagents.",
                            "category": "missing genetic modification reagents"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": {
                    "term_name": "K562",
                    "classification": "cell line"
                },
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "description": "STARR-seq example experiment",
                "files": [
                    {
                        "@id": "/files/ENCFF100ELE/"
                    }
                ],
                "lab": {
                    "title": "Barbara Wold, Caltech"
                },
                "replicates": [
                    {
                        "library": {
                            "biosample": {
                                "organism": {
                                    "scientific_name": "Homo sapiens"
                                },
                                "life_stage": "unknown",
                                "accession": "ENCBS888RUL",
                                "age": "unknown"
                            }
                        },
                        "@id": "/replicates/df1f6993-10ef-12e9-a913-1684be663d3e/",
                        "technical_replicate_number": 3,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "revoked"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR759STU/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR759STU",
                "assay_term_name": "CRISPR screen",
                "assay_title": "CRISPR screen",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/libraries/ENCLB009ACL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released library {ENCLB009ACL|/libraries/ENCLB009ACL/} has in progress subobject platform {OBI:0000703|/platforms/OBI:0000703/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/biosamples/ENCBS888RUL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released biosample {ENCBS888RUL|/biosamples/ENCBS888RUL/} has in progress subobject human donor {ENCDO000HUM|/human-donors/ENCDO000HUM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/files/ENCFF024EQB/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF024EQB|/files/ENCFF024EQB/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        },
                        {
                            "path": "/files/ENCFF420GQB/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF420GQB|/files/ENCFF420GQB/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_fcc_experiment",
                            "detail": "CRISPR screen {ENCSR759STU|/functional-characterization-experiments/ENCSR759STU/} is not part of a series.",
                            "category": "missing related_series"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released functional characterization experiment {ENCSR759STU|/functional-characterization-experiments/ENCSR759STU/} has archived subobject functional characterization experiment {ENCSR051STU|/functional-characterization-experiments/ENCSR051STU/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released functional characterization experiment {ENCSR759STU|/functional-characterization-experiments/ENCSR759STU/} has archived subobject reference {ENCSR500ELM|/references/ENCSR500ELM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/labs/gregory-crawford/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {gregory-crawford|/labs/gregory-crawford/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment contains a replicate [1,1] {df1f66d6-70ef-11e9-a923-1681be663d3e|/replicates/df1f66d6-70ef-11e9-a923-1681be663d3e/} without raw data associated files.",
                            "category": "missing raw data in replicate"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR759STU|/functional-characterization-experiments/ENCSR759STU/} has no attached documents",
                            "category": "missing documents"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR759STU/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment is expected to be replicated, but contains only one listed biological replicate.",
                            "category": "unreplicated experiment"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/files/ENCFF024EQB/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF024EQB|/files/ENCFF024EQB/}.",
                            "category": "missing analysis_step_run"
                        },
                        {
                            "path": "/files/ENCFF420GQB/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF420GQB|/files/ENCFF420GQB/}.",
                            "category": "missing analysis_step_run"
                        },
                        {
                            "path": "/genetic-modifications/ENCGM555KOT/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_genetic_modification_reagents",
                            "detail": "Genetic modification {ENCGM555KOT|/genetic-modifications/ENCGM555KOT/} of method CRISPR is missing reagents.",
                            "category": "missing genetic modification reagents"
                        }
                    ]
                },
                "award": {
                    "project": "Roadmap"
                },
                "biosample_ontology": {
                    "term_name": "WTC-11",
                    "classification": "cell line"
                },
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "crispr_screen_readout": "proliferation",
                "description": "CRISPR screen experiment description",
                "elements_references": [
                    {
                        "crispr_screen_tiling": "peak tiling",
                        "elements_selection_method": [
                            "accessible genome regions",
                            "DNase hypersensitive sites",
                            "chromatin states"
                        ]
                    }
                ],
                "files": [
                    {
                        "@id": "/files/ENCFF420GQB/"
                    },
                    {
                        "@id": "/files/ENCFF024EQB/"
                    }
                ],
                "lab": {
                    "title": "Gregory Crawford, Duke"
                },
                "perturbation_type": "knockout",
                "replicates": [
                    {
                        "library": {
                            "construction_platform": {
                                "term_name": "Illumina Genome Analyzer II"
                            },
                            "biosample": {
                                "organism": {
                                    "scientific_name": "Homo sapiens"
                                },
                                "life_stage": "unknown",
                                "accession": "ENCBS888RUL",
                                "age": "unknown"
                            }
                        },
                        "@id": "/replicates/df1f66d6-70ef-11e9-a923-1681be663d3e/",
                        "technical_replicate_number": 1,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR222MPR/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR222MPR",
                "assay_term_name": "MPRA",
                "assay_title": "MPRA",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/biosamples/ENCBS888RUL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released biosample {ENCBS888RUL|/biosamples/ENCBS888RUL/} has in progress subobject human donor {ENCDO000HUM|/human-donors/ENCDO000HUM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/labs/thomas-gingeras/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {thomas-gingeras|/labs/thomas-gingeras/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR222MPR/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released functional characterization experiment {ENCSR222MPR|/functional-characterization-experiments/ENCSR222MPR/} has archived subobject functional characterization experiment {ENCSR051STU|/functional-characterization-experiments/ENCSR051STU/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/files/ENCFF527MEQ/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF527MEQ|/files/ENCFF527MEQ/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR222MPR/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR222MPR|/functional-characterization-experiments/ENCSR222MPR/} contains a library {ENCLB001MPR|/libraries/ENCLB001MPR/} linked to biosample type '{cell_line_EFO_0009747|/biosample-types/cell_line_EFO_0009747/}', while experiment's biosample type is '{cell_line_EFO_0002067|/biosample-types/cell_line_EFO_0002067/}'.",
                            "category": "inconsistent library biosample"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR222MPR/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment contains a replicate [1,1] {df1f6993-11ef-12e9-a913-1684be663d3e|/replicates/df1f6993-11ef-12e9-a913-1684be663d3e/} without raw data associated files.",
                            "category": "missing raw data in replicate"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR222MPR/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR222MPR|/functional-characterization-experiments/ENCSR222MPR/} has no attached documents",
                            "category": "missing documents"
                        },
                        {
                            "path": "/functional-characterization-experiments/ENCSR222MPR/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment is expected to be replicated, but contains only one listed biological replicate.",
                            "category": "unreplicated experiment"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/genetic-modifications/ENCGM555KOT/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_genetic_modification_reagents",
                            "detail": "Genetic modification {ENCGM555KOT|/genetic-modifications/ENCGM555KOT/} of method CRISPR is missing reagents.",
                            "category": "missing genetic modification reagents"
                        },
                        {
                            "path": "/files/ENCFF527MEQ/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF527MEQ|/files/ENCFF527MEQ/}.",
                            "category": "missing analysis_step_run"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": {
                    "term_name": "K562",
                    "classification": "cell line"
                },
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "description": "MPRA experiment",
                "examined_loci": [
                    {
                        "gene": {
                            "dbxrefs": [
                                "MIM:132890",
                                "HGNC:7975",
                                "ENSEMBL:ENSG00000175745",
                                "Vega:OTTHUMG00000119079",
                                "UniProtKB:P10589",
                                "RefSeq:NG_034119"
                            ],
                            "symbol": "NR2F1",
                            "organism": "/organisms/human/",
                            "synonyms": [
                                "BBOAS",
                                "BBSOAS",
                                "COUP-TFI",
                                "COUPTF1",
                                "EAR-3",
                                "EAR3",
                                "ERBAL3",
                                "SVP44",
                                "TCFCOUP1",
                                "TFCOUP1"
                            ],
                            "@type": [
                                "Gene",
                                "Item"
                            ],
                            "title": "NR2F1 (Homo sapiens)",
                            "uuid": "75866336-b42b-4341-9b70-240eb469c231",
                            "targets": [
                                "/targets/NR2F1%C3%82-human/"
                            ],
                            "schema_version": "2",
                            "geneid": "7025",
                            "name": "nuclear receptor subfamily 2 group F member 1",
                            "locations": [],
                            "@id": "/genes/7025/",
                            "ncbi_entrez_status": "live",
                            "status": "released"
                        },
                        "expression_measurement_method": "PrimeFlow",
                        "expression_percentile": 90
                    },
                    {
                        "expression_range_minimum": 0,
                        "gene": {
                            "dbxrefs": [
                                "MIM:164343",
                                "HGNC:3126",
                                "ENSEMBL:ENSG00000164330",
                                "Vega:OTTHUMG00000130304",
                                "UniProtKB:Q9UH73",
                                "UniProtKB:B4E2U8"
                            ],
                            "symbol": "EBF1",
                            "organism": "/organisms/human/",
                            "synonyms": [
                                "COE1",
                                "EBF",
                                "O/E-1",
                                "OLF1"
                            ],
                            "@type": [
                                "Gene",
                                "Item"
                            ],
                            "title": "EBF1 (Homo sapiens)",
                            "uuid": "cd05d34d-9a51-4efc-b0ec-9245a1d83b40",
                            "targets": [
                                "/targets/EBF1-human/"
                            ],
                            "schema_version": "2",
                            "geneid": "1879",
                            "name": "early B cell factor 1",
                            "locations": [],
                            "@id": "/genes/1879/",
                            "ncbi_entrez_status": "live",
                            "status": "released"
                        },
                        "expression_measurement_method": "PrimeFlow",
                        "expression_range_maximum": 20
                    }
                ],
                "files": [
                    {
                        "@id": "/files/ENCFF527MEQ/"
                    }
                ],
                "lab": {
                    "title": "Thomas Gingeras, CSHL"
                },
                "replicates": [
                    {
                        "library": {
                            "biosample": {
                                "organism": {
                                    "scientific_name": "Homo sapiens"
                                },
                                "life_stage": "unknown",
                                "accession": "ENCBS888RUL",
                                "age": "unknown"
                            }
                        },
                        "@id": "/replicates/df1f6993-11ef-12e9-a913-1684be663d3e/",
                        "technical_replicate_number": 1,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR127PCE/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR127PCE",
                "assay_term_name": "pooled clone sequencing",
                "assay_title": "pooled clone sequencing",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/files/ENCFF210SUR/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_file",
                            "detail": "derived_from is a list of files that were used to create a given file; for example, fastq file(s) will appear in the derived_from list of an alignments file. Processed file {ENCFF210SUR|/files/ENCFF210SUR/} is missing the requisite file specification in its derived_from list.",
                            "category": "missing derived_from"
                        },
                        {
                            "path": "/labs/gregory-crawford/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {gregory-crawford|/labs/gregory-crawford/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR127PCE/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment contains a replicate [1,1] {23d52556-2287-47e2-add1-777d7df6b56d|/replicates/23d52556-2287-47e2-add1-777d7df6b56d/} without raw data associated files.",
                            "category": "missing raw data in replicate"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR127PCE/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR127PCE|/functional-characterization-experiments/ENCSR127PCE/} has no attached documents",
                            "category": "missing documents"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/files/ENCFF210SUR/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_file",
                            "detail": "Missing analysis_step_run information in file {ENCFF210SUR|/files/ENCFF210SUR/}.",
                            "category": "missing analysis_step_run"
                        }
                    ]
                },
                "award": {
                    "project": "Roadmap"
                },
                "biosample_ontology": {
                    "term_name": "DNA cloning sample",
                    "classification": "cloning host"
                },
                "description": "pooled clone sequencing elements validation",
                "files": [
                    {
                        "@id": "/files/ENCFF210SUR/"
                    }
                ],
                "lab": {
                    "title": "Gregory Crawford, Duke"
                },
                "replicates": [
                    {
                        "@id": "/replicates/23d52556-2287-47e2-add1-777d7df6b56d/",
                        "technical_replicate_number": 1,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "released"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR051STU/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR051STU",
                "assay_term_name": "pooled clone sequencing",
                "assay_title": "pooled clone sequencing",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/biosamples/ENCBS888RUL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released biosample {ENCBS888RUL|/biosamples/ENCBS888RUL/} has in progress subobject human donor {ENCDO000HUM|/human-donors/ENCDO000HUM/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/libraries/ENCLB001ACL/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Released library {ENCLB001ACL|/libraries/ENCLB001ACL/} has in progress subobject platform {OBI:0000703|/platforms/OBI:0000703/}",
                            "category": "mismatched status"
                        },
                        {
                            "path": "/labs/gregory-crawford/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {gregory-crawford|/labs/gregory-crawford/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ],
                    "ERROR": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR051STU/",
                            "level_name": "ERROR",
                            "level": 60,
                            "name": "audit_fcc_experiment",
                            "detail": "This experiment contains a replicate [1,1] {df1f6992-70ef-11e9-a923-1681be663d3e|/replicates/df1f6992-70ef-11e9-a923-1681be663d3e/} without raw data associated files.",
                            "category": "missing raw data in replicate"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR051STU/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR051STU|/functional-characterization-experiments/ENCSR051STU/} has no attached documents",
                            "category": "missing documents"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR051STU/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR051STU|/functional-characterization-experiments/ENCSR051STU/} does not contain any raw or processed data.",
                            "category": "lacking processed data"
                        },
                        {
                            "path": "/genetic-modifications/ENCGM555KOT/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_genetic_modification_reagents",
                            "detail": "Genetic modification {ENCGM555KOT|/genetic-modifications/ENCGM555KOT/} of method CRISPR is missing reagents.",
                            "category": "missing genetic modification reagents"
                        }
                    ]
                },
                "award": {
                    "project": "Roadmap"
                },
                "biosample_ontology": {
                    "term_name": "WTC-11",
                    "classification": "cell line"
                },
                "biosample_summary": "Homo sapiens WTC-11 genetically modified (knockout) using CRISPR",
                "description": "pooled clone sequencing mapping description",
                "lab": {
                    "title": "Gregory Crawford, Duke"
                },
                "replicates": [
                    {
                        "library": {
                            "construction_platform": {
                                "term_name": "Illumina Genome Analyzer II"
                            },
                            "biosample": {
                                "organism": {
                                    "scientific_name": "Homo sapiens"
                                },
                                "life_stage": "unknown",
                                "accession": "ENCBS888RUL",
                                "age": "unknown"
                            }
                        },
                        "@id": "/replicates/df1f6992-70ef-11e9-a923-1681be663d3e/",
                        "technical_replicate_number": 1,
                        "biological_replicate_number": 1
                    }
                ],
                "status": "archived"
            },
            {
                "@id": "/functional-characterization-experiments/ENCSR212POL/",
                "@type": [
                    "FunctionalCharacterizationExperiment",
                    "Dataset",
                    "Item"
                ],
                "accession": "ENCSR212POL",
                "assay_term_name": "pooled clone sequencing",
                "assay_title": "pooled clone sequencing",
                "audit": {
                    "INTERNAL_ACTION": [
                        {
                            "path": "/labs/thomas-gingeras/",
                            "level_name": "INTERNAL_ACTION",
                            "level": 30,
                            "name": "audit_item_status",
                            "detail": "Current lab {thomas-gingeras|/labs/thomas-gingeras/} has deleted subobject award {ENCODE2|/awards/ENCODE2/}",
                            "category": "mismatched status"
                        }
                    ],
                    "NOT_COMPLIANT": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR212POL/",
                            "level_name": "NOT_COMPLIANT",
                            "level": 50,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR212POL|/functional-characterization-experiments/ENCSR212POL/} has no attached documents",
                            "category": "missing documents"
                        }
                    ],
                    "WARNING": [
                        {
                            "path": "/functional-characterization-experiments/ENCSR212POL/",
                            "level_name": "WARNING",
                            "level": 40,
                            "name": "audit_fcc_experiment",
                            "detail": "Experiment {ENCSR212POL|/functional-characterization-experiments/ENCSR212POL/} does not contain any raw or processed data.",
                            "category": "lacking processed data"
                        }
                    ]
                },
                "award": {
                    "project": "ENCODE"
                },
                "biosample_ontology": {
                    "term_name": "cell-free sample",
                    "classification": "cell-free sample"
                },
                "description": "pooled clone sequencing experiment",
                "lab": {
                    "title": "Thomas Gingeras, CSHL"
                },
                "status": "released"
            }
        ],
        "@id": "/search/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries",
        "@type": [
            "Search"
        ],
        "clear_filters": "/search/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries",
        "facet_groups": [],
        "facets": [
            {
                "field": "type",
                "title": "Data Type",
                "terms": [
                    {
                        "key": "Dataset",
                        "doc_count": 9
                    },
                    {
                        "key": "FunctionalCharacterizationExperiment",
                        "doc_count": 8
                    },
                    {
                        "key": "FunctionalCharacterizationSeries",
                        "doc_count": 1
                    },
                    {
                        "key": "Series",
                        "doc_count": 1
                    }
                ],
                "total": 9,
                "type": "terms",
                "appended": false,
                "open_on_load": false
            },
            {
                "field": "audit.ERROR.category",
                "title": "Audit category: ERROR",
                "terms": [
                    {
                        "key": "missing raw data in replicate",
                        "doc_count": 5
                    },
                    {
                        "key": "inconsistent library biosample",
                        "doc_count": 2
                    }
                ],
                "total": 9,
                "type": "terms",
                "appended": false,
                "open_on_load": false
            },
            {
                "field": "audit.NOT_COMPLIANT.category",
                "title": "Audit category: NOT COMPLIANT",
                "terms": [
                    {
                        "key": "missing documents",
                        "doc_count": 8
                    },
                    {
                        "key": "unreplicated experiment",
                        "doc_count": 4
                    }
                ],
                "total": 9,
                "type": "terms",
                "appended": false,
                "open_on_load": false
            },
            {
                "field": "audit.WARNING.category",
                "title": "Audit category: WARNING",
                "terms": [
                    {
                        "key": "missing analysis_step_run",
                        "doc_count": 5
                    },
                    {
                        "key": "missing genetic modification reagents",
                        "doc_count": 5
                    },
                    {
                        "key": "lacking processed data",
                        "doc_count": 3
                    }
                ],
                "total": 9,
                "type": "terms",
                "appended": false,
                "open_on_load": false
            }
        ],
        "filters": [
            {
                "field": "type",
                "term": "FunctionalCharacterizationExperiment",
                "remove": "/search/?type=FunctionalCharacterizationSeries"
            },
            {
                "field": "type",
                "term": "FunctionalCharacterizationSeries",
                "remove": "/search/?type=FunctionalCharacterizationExperiment"
            }
        ],
        "notification": "Success",
        "sort": {
            "date_created": {
                "order": "desc",
                "unmapped_type": "keyword"
            },
            "label": {
                "order": "desc",
                "unmapped_type": "keyword"
            },
            "uuid": {
                "order": "desc",
                "unmapped_type": "keyword"
            }
        },
        "title": "Search",
        "total": 9,
    }
};
