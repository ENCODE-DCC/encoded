from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    paths_filtered_by_status
)
from .dataset import Dataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
)

from .assay_data import assay_terms
from .biosample import construct_biosample_summary
from .shared_biosample import biosample_summary_information


@collection(
    name='transgenic-enhancer-experiments',
    unique_key='accession',
    properties={
        'title': 'Transgenic enhancer experiments',
        'description': 'Listing of Transgenic Enhancer Experiments',
    })
class TransgenicEnhancerExperiment(
    Dataset,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedAssayTitle,
    CalculatedAssaySlims,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims):
    item_type = 'transgenic_enhancer_experiment'
    schema = load_schema('encoded:schemas/transgenic_enhancer_experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'biosamples',
        'biosamples.donor.organism',
        'biosamples.biosample_ontology',
        'biosamples.organism',
        'biosamples.characterizations',
        'related_series',
        'possible_controls',
    ]
    audit_inherit = [
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    set_status_up = [
        'documents',
        'biosamples',
    ]
    set_status_down = []
    rev = Dataset.rev.copy()
    rev.update({
        'related_series': ('Series', 'related_datasets'),
        'superseded_by': ('TransgenicEnhancerExperiment', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Related series",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Series.related_datasets",
        },
        "notSubmittable": True,
    })
    def related_series(self, request, related_series):
        return paths_filtered_by_status(request, related_series)

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "TransgenicEnhancerExperiment.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "string",
    })
    def biosample_summary(self, request, biosamples=None):
        drop_age_sex_flag = False
        add_classification_flag = False
        dictionaries_of_phrases = []
        biosample_accessions = set()
        if biosamples is not None:
            for bs in biosamples:
                biosampleObject = request.embed(bs, '@@object')
                if biosampleObject['status'] == 'deleted':
                    continue
                if biosampleObject['accession'] not in biosample_accessions:
                    biosample_accessions.add(biosampleObject['accession'])
                    biosample_info = biosample_summary_information(request, biosampleObject)
                    biosample_summary_dictionary = biosample_info[0]
                    biosample_drop_age_sex_flag = biosample_info[1]
                    biosample_add_classification_flag = biosample_info[2]
                    biosample_drop_originated_from_flag = biosample_info[3]
                    dictionaries_of_phrases.append(biosample_summary_dictionary)
                    if biosample_drop_age_sex_flag is True:
                        drop_age_sex_flag = True
                    if biosample_add_classification_flag is True:
                        add_classification_flag = True

        sentence_parts = [
            'genotype_strain',
            'experiment_term_phrase',
            'phase',
            'fractionated',
            'sex_stage_age',
            'post_nucleic_acid_delivery_time',
            'post_differentiation_time',
            'synchronization',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'depleted_in',
            'disease_term_name',
            'pulse_chase_time'
        ]
        if drop_age_sex_flag:
            sentence_parts.remove('sex_stage_age')
        if add_classification_flag:
            sentence_parts.insert(2, 'sample_type')
        if biosample_drop_originated_from_flag:
            sentence_parts.remove('originated_from')

        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)

    @calculated_property(schema={
        "title": "Datapoint",
        "description": "A flag to indicate whether the Transgenic Enhancer Experiment is a datapoint that should not be displayed on it's own.",
        "type": "boolean",
        "notSubmittable": True,
    })
    def datapoint(self, request):
        return False