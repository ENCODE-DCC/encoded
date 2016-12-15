from snovault import calculated_property
from snovault.util import ensurelist


class CalculatedBiosampleSlims:
    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['organs'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['systems'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['developmental'])
        return list(slims)


class CalculatedBiosampleSynonyms:
    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        syns = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'])
        return list(syns)


class CalculatedAssaySynonyms:
    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        assay_term_id = ensurelist(assay_term_id)
        syns = set()
        for term_id in assay_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'] + [
                    registry['ontology'][term_id]['name'],
                ])
        return list(syns)


class CalculatedFileSetBiosample:
    @calculated_property(condition='files', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, files):
        return request.select_distinct_values(
            'replicate.experiment.biosample_term_name', *files)

    @calculated_property(define=True, condition='files', schema={
        "title": "Biosample term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_id(self, request, files):
        return request.select_distinct_values(
            'replicate.experiment.biosample_term_id', *files)

    @calculated_property(condition='files', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, files):
        return request.select_distinct_values(
            'replicate.experiment.biosample_type', *files)

    @calculated_property(condition='files', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, files):
        return request.select_distinct_values(
            'replicate.library.biosample.organism', *files)


class CalculatedFileSetAssay:
    @calculated_property(condition='files', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, files):
        return request.select_distinct_values(
            'replicate.experiment.assay_term_name', *files)

    @calculated_property(define=True, condition='files', schema={
        "title": "Assay term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, files):
        return request.select_distinct_values(
            'replicate.experiment.assay_term_id', *files)


class CalculatedSeriesAssay:
    @calculated_property(condition='related_datasets', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_name', *related_datasets)

    @calculated_property(define=True, condition='related_datasets', schema={
        "title": "Assay term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_id', *related_datasets)


class CalculatedSeriesBiosample:
    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_term_name', *related_datasets)

    @calculated_property(define=True, condition='related_datasets', schema={
        "title": "Biosample term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_id(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_term_id', *related_datasets)

    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_type', *related_datasets)

    @calculated_property(condition='related_datasets', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.library.biosample.organism', *related_datasets)


class CalculatedSeriesTreatment:
    @calculated_property(condition='related_datasets', schema={
        "title": "Treatment term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def treatment_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.library.biosample.treatments.treatment_term_name',
            *related_datasets)


class CalculatedSeriesTarget:
    @calculated_property(condition='related_datasets', schema={
        "title": "Target",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Target",
        },
    })
    def target(self, request, related_datasets):
        return request.select_distinct_values('target', *related_datasets)


class CalculatedAssayTermID:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay ID",
        "description": "OBI (Ontology for Biomedical Investigations) ontology identifier for the assay.",
        "type": "string",
        "comment": "Calculated based on the choice of assay_term_name"
    })
    def assay_term_id(self, request, assay_term_name):
        term_lookup = {
            'ChIP-seq': 'OBI:0000716',
            'RNA-seq': 'OBI:0001271',
            'DNase-seq': 'OBI:0001853',
            'eCLIP': 'NTR:0003027',
            'shRNA knockdown followed by RNA-seq': 'NTR:0000762',
            'RNA Bind-n-Seq': 'OBI:0002044',
            'transcription profiling by array assay': 'OBI:0001463',
            'DNA methylation profiling by array assay': 'OBI:0001332',
            'whole-genome shotgun bisulfite sequencing': 'OBI:0001863',
            'RRBS': 'OBI:0001862',
            'siRNA knockdown followed by RNA-seq': 'NTR:0000763',
            'RAMPAGE': 'OBI:0001864',
            'comparative genomic hybridization by array': 'OBI:0001393',
            'CAGE': 'OBI:0001674',
            'single cell isolation followed by RNA-seq': 'NTR:0003082',
            'Repli-seq': 'OBI:0001920',
            'microRNA-seq': 'OBI:0001922',
            'microRNA counts': 'NTR:0003660',
            'MRE-seq': 'OBI:0001861',
            'RIP-seq': 'OBI:0001857',
            'Repli-chip': 'OBI:0001915',
            'MeDIP-seq': 'OBI:0000693',
            'ChIA-PET': 'OBI:0001848',
            'FAIRE-seq': 'OBI:0001859',
            'ATAC-seq': 'OBI:0002039',
            'PAS-seq': 'OBI:0002045',
            'RIP-chip': 'OBI:0001918',
            'RNA-PET': 'OBI:0001850',
            'genotyping by high throughput sequencing assay': 'OBI:0001247',
            'CRISPR genome editing followed by RNA-seq': 'NTR:0003814',
            'protein sequencing by tandem mass spectrometry assay': 'OBI:0001923',
            '5C': 'OBI:0001919',
            'HiC': 'OBI:0002042',
            'TAB-seq': 'NTR:0002490',
            'iCLIP': 'OBI:0002043',
            'DNA-PET': 'OBI:0001849',
            'Switchgear': 'NTR:0000612',
            '5\' RLM RACE': 'NTR:0001684',
            'MNase-seq': 'OBI:0001924'
        }
        term_id = list()
        for term_name in assay_term_name:
            if term_name in term_lookup:
                term_id.append(term_lookup.get(term_name))
            else:
                term_id.append('Term ID unknown')
        return term_id
