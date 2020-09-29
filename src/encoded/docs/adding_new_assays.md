Adding a new assay
=========================

This document describes how and where to update the encoded application to support a new assay term name.

Guide to where to edit Source Code
----------------

* **src** directory - contains all the python and javascript code for front and backends
    * **schemas** - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
    * **audit** - python instructions for checking metadata stored in the schema
    * **tests** - Unit and integration tests
    * **types** -  business logic for dispatching URLs and producing the correct JSON
    * **docs** -  SOPs and additional information on schemas, audits, ontologies, and annotations

Steps to add a new assay
---------------- 

1. Schemas and changelogs:

    Assays are identified by precise ontological terms that we list in a property *assay_term_name*. This is used in many different objects on the portal, and in most cases a mixin property ```assay``` provides this enum list. You will need to add your new assay type to the enum in mixins.json and update the changelogs of the objects that import this property.
    The objects **Award**, **Pipeline**, and **Software** list ```assay_term_name``` in unique objects without importing the ```assay``` property, so both the schema profile and changelog will need to be updated in these cases.
    
    * [mixins.json] & [mixins changelog]
    * [award.json] & [award changelog]
    * [software.json] & [software changelog]
    * [pipeline.json] & [pipeline changelog]

    To find objects that import the ```assay``` property, search for: ```"$ref": "mixins.json#/assay"```; update the changelog for these objects. A list of links for these object changelogs is at the end of this document.
    
    For additional information on schema changes, please refer to [schema-changes.md].

2. Audits: 

    In [audit/experiment.py], determine what audit checks are appropriate for your type of assay. Assays that need controls should be added to ```controlRequiredAssayList```, assays that have targets should be added to ```targetRequiredAssayList```, and sequencing assays should be added to ```seq_assays```.

    For additional information or how to add entirely new audits, please refer to [making_audits.md].

3. Tests:

    * Add an experiment insert. This is an example experiment of this assay type, which you will place in [src/encoded/inserts/experiment.json]. This will be a simple ```JSON``` object that can load in the local application. If we were adding the assay type **CUT&Tag**, the insert might appear as:

    ```
    {
        "_test": "CUT&Tag test",
        "uuid": "6600481e-b667-46ff-acd8-7de7026c2fdf",
        "accession": "ENCSR830QHT",
        "lab": "/labs/john-stamatoyannopoulos/",
        "award": "U54HG007010",
        "status": "released",
        "date_released": "2015-08-31",
        "biosample_ontology": "tissue_UBERON_0001891",
        "assay_term_name": "CUT&Tag"
    }
    ```
    * Update existing test features. Now that another experiment is added to our inserts, some tests will break without a couple of corrections. We will need to add our experiment to the number of expected fixtures.

        * Add 1 to the numbered results in [tests/features/views.feature]:
        ```
        When I click the link to "/matrix/?type=Experiment"
        Then I should see "Showing 72 results"
        ```
        * Add 1 to the ```len(lines)``` in [tests/test_batch_download.py]:
        ```
        def test_batch_download_report_download(testapp, index_workbook):
        ...
        assert len(lines) == 72
        ```
        * Assess if your new insert will break any other tests- the easiest way to do this is simply to run the tests and interpret any errors that come up. The tests are listed in sets in the [encoded README.md].

    * Add a new audit test. To ensure assays with the new assay term name will be audited correctly, you need to create or edit a fixture (a sample experiment object, similar to your insert) and test that it is audited the same way as experiments of other assay types. For example, if you were to test that your new **CUT&Tag** term was added correctly to ```targetRequiredAssayList```, you can add new lines to the existing test for this audit.

        * In [tests/test_audit_experiment.py], you'll find this test for checking targets are included in experiments that require them:

        ```
        def test_audit_experiment_target(testapp, base_experiment):
            testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
            res = testapp.get(base_experiment['@id'] + '@@index-data')
            assert any(error['category'] == 'missing target'
                for error in collect_audit_errors(res))
        ```

        * Then, you can patch a fixture (```base_experiment``` is imported in the test above) already used in the audit test to check your new assay term, for example:

        ```
        testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'CUT&Tag'})
            res = testapp.get(base_experiment['@id'] + '@@index-data')
            assert any(error['category'] == 'missing target'
                for error in collect_audit_errors(res))
        ```
        * If you prefer, you can also write a new experiment fixture which you would add to [tests/fixtures/schemas/experiment.py]. For more detailed instructions, please refer to [making_audits.md].

4. Ontology: 

    Check to see if the new assay type has an entry in [OBI].
    * If there is an entry, you will use the OBI identifier (e.g., OBI:0002039).
    * If there is no entry, write a New Term Request ticket on the [NTR board], and provide a publication describing the assay type. The ticket number will be used as your assay term identifier (e.g., NTR-564 becomes NTR:0000564).

    Add the assay term name and identifier to [types/assay_data.py].

    If you using an NTR identifier, add an entry to [src/encoded/commands/ntr_terms.py]. You will need to provide:
    * The name for your assay type in the ```name``` property
    * A shortened form of the name in ```preferred_name```
    * The parent term for assay type that it will slim to in ```assay```

    For **CUT&Tag**, the entry would appear as follows:
    ```
     "NTR:0000564": {
        "assay": ['DNA binding'],
        "category": [],
        "developmental": [],
        "name": "Cleavage Under Targets and Tagmentation",
        "objectives": [],
        "organs": [],
        "preferred_name": "CUT&Tag",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    ```
    Lastly, follow the instructions in [Updating ontologies] to include your new assay in the encoded application ```ontology.json```.


Changelogs for objects with the ```assay``` mixin property
-------------------
42 code results in ENCODE-DCC/encoded for ```"$ref": "mixins.json#/assay"```
If your search does not match this, the list needs to be updated.

[experiment.md]

[annotation.md]

[atac_alignment_quality_metric.md]

[atac_alignment_enrichment_quality_metric.md]

[atac_library_complexity_quality_metric.md]

[atac_peak_enrichment_quality_metric.md]

[atac_replication_quality_metric.md]

[bismark_quality_metric.md]

[chip_alignment_enrichment_quality_metric.md]

[chip_alignment_samstat_quality_metric.md]

[chip_library_quality_metric.md]

[chip_peak_enrichment_quality_metric.md]

[chip_replication_quality_metric.md]

[chipseq_filter_quality_metric.md]

[complexity_xcorr_quality_metric.md]

[correlation_quality_metric.md]

[cpg_correlation_quality_metric.md]

[dnase_alignment_quality_metric.md]

[dnase_footprinting_quality_metric.md]

[duplicates_quality_metric.md]

[edwbamstats_quality_metric.md]

[filtering_quality_metric.md]

[gembs_alignment_quality_metric.md]

[gencode_category_quality_metric.md]

[gene_quantification_quality_metric.md]

[generic_quality_metric.md]

[gene_type_quantification_quality_metric.md]

[histone_chipseq_quality_metric.md]

[hotspot_quality_metric.md]

[idr_quality_metric.md]

[idr_summary_quality_metric.md]

[long_read_rna_mapping_quality_metric.md]

[long_read_rna_quantification_quality_metric.md]

[mad_quality_metric.md]

[micro_rna_mapping_quality_metric.md]

[micro_rna_quantification_quality_metric.md]

[quality_metric.md]

[samtools_flagstats_quality_metric.md]

[samtools_stats_quality_metric.md]

[star_quality_metric.md]

[transgenic_enhancer_experiment.md]

[trimming_quality_metric.md]

[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[mixins.json]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/mixins.json
[mixins changelog]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/mixins.md
[award.json]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/award.json
[award changelog]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/award.md
[software.json]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/software.json
[software changelog]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/software.md
[pipeline.json]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/pipeline.json
[pipeline changelog]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/pipeline.md
[schema-changes.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/docs/schema-changes.md

[audit/experiment.py]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/audit/experiment.py
[making_audits.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/docs/making_audits.md

[src/encoded/inserts/experiment.json]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/tests/data/inserts/experiment.json
[tests/features/views.feature]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/tests/features/views.feature
[tests/test_batch_download.py]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/tests/test_batch_download.py
[encoded README.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/README.md
[tests/test_audit_experiment.py]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/tests/test_audit_experiment.py
[tests/fixtures/schemas/experiment.py]: https://github.com/ENCODE-DCC/encoded/tree/dev/src/encoded/tests/fixtures/schemas/experiment.py

[OBI]: http://www.ontobee.org/ontology/OBI
[NTR board]: https://encodedcc.atlassian.net/browse/NTR
[types/assay_data.py]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/types/assay_data.py
[src/encoded/commands/ntr_terms.py]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/commands/ntr_terms.py
[Updating ontologies]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/docs/updating_ontologies.md

[experiment.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/experiment.md
[annotation.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/annotation.md
[atac_alignment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/atac_alignment_quality_metric.md
[atac_alignment_enrichment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/atac_alignment_enrichment_quality_metric.md
[atac_library_complexity_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/atac_library_complexity_quality_metric.md
[atac_peak_enrichment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/atac_peak_enrichment_quality_metric.md
[atac_replication_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/atac_replication_quality_metric.md
[bismark_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/bismark_quality_metric.md
[chip_alignment_enrichment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chip_alignment_enrichment_quality_metric.md
[chip_alignment_samstat_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chip_alignment_samstat_quality_metric.md
[chip_library_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chip_library_quality_metric.md
[chip_peak_enrichment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chip_peak_enrichment_quality_metric.md
[chip_replication_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chip_replication_quality_metric.md
[chipseq_filter_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/chipseq_filter_quality_metric.md
[complexity_xcorr_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/complexity_xcorr_quality_metric.md
[correlation_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/correlation_quality_metric.md
[cpg_correlation_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/cpg_correlation_quality_metric.md
[dnase_alignment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/dnase_alignment_quality_metric.md
[dnase_footprinting_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/dnase_footprinting_quality_metric.md
[duplicates_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/duplicates_quality_metric.md
[edwbamstats_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/edwbamstats_quality_metric.md
[filtering_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/filtering_quality_metric.md
[gembs_alignment_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/gembs_alignment_quality_metric.md
[gencode_category_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/gencode_category_quality_metric.md
[gene_quantification_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/gene_quantification_quality_metric.md
[generic_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/generic_quality_metric.md
[gene_type_quantification_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/gene_type_quantification_quality_metric.md
[histone_chipseq_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/histone_chipseq_quality_metric.md
[hotspot_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/hotspot_quality_metric.md
[idr_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/idr_quality_metric.md
[idr_summary_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/idr_summary_quality_metric.md
[long_read_rna_mapping_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/long_read_rna_mapping_quality_metric.md
[long_read_rna_quantification_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/long_read_rna_quantification_quality_metric.md
[mad_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/mad_quality_metric.md
[micro_rna_mapping_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/micro_rna_mapping_quality_metric.md
[micro_rna_quantification_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/micro_rna_quantification_quality_metric.md
[quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/quality_metric.md
[samtools_flagstats_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/samtools_flagstats_quality_metric.md
[samtools_stats_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/samtools_stats_quality_metric.md
[star_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/star_quality_metric.md
[transgenic_enhancer_experiment.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/transgenic_enhancer_experiment.md
[trimming_quality_metric.md]: https://github.com/ENCODE-DCC/encoded/blob/dev/src/encoded/schemas/changelogs/trimming_quality_metric.md
