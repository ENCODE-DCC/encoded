from pyramid.traversal import find_root
from contentbase import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
)
from .dataset import Dataset
import datetime


@collection(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    base_types = [Dataset.__name__] + Dataset.base_types
    embedded = Dataset.embedded + [
        'files.lab',
        'files.platform',
        'files.lab',
        'files.derived_from',
        'files.derived_from.replicate',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.versions',
        'files.analysis_step_version.analysis_step.versions.software_versions',
        'files.analysis_step_version.analysis_step.versions.software_versions.software',
        'files.analysis_step_version.software_versions',
        'files.analysis_step_version.software_versions.software',
        'files.replicate.library.biosample',
        'files.quality_metrics',
        'files.quality_metrics.step_run',
        'files.quality_metrics.step_run.analysis_step_version.analysis_step',
        'contributing_files.platform',
        'contributing_files.lab',
        'contributing_files.derived_from',
        'contributing_files.analysis_step_version.analysis_step',
        'contributing_files.analysis_step_version.analysis_step.pipelines',
        'contributing_files.analysis_step_version.software_versions',
        'contributing_files.analysis_step_version.software_versions.software',
        'award.pi.lab',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents.lab',
        'replicates.library.documents.submitted_by',
        'replicates.library.documents.award',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.rnais',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor.mutated_gene',
        'replicates.library.biosample.treatments',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'possible_controls',
        'possible_controls.target',
        'possible_controls.lab',
        'target.organism',
        'references',
    ]
    audit_inherit = [
        'original_files',
        'original_files.replicate',
        'original_files.platform',
        'target',
        'revoked_files',
        'revoked_files.replicate',
        'submitted_by',
        'lab',
        'award',
        'documents',
        'replicates.antibody',
        'replicates.antibody.characterizations',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.derived_from',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.pooled_from',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'target.organism',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'replicates': ('Replicate', 'experiment')
    })

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['organs']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['systems']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['developmental']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['synonyms']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['synonyms'] + [
                registry['ontology'][assay_term_id]['name'],
            ]
        return []

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay category",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def category_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['category']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def type_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['types']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay objective",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def objective_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['objectives']
        return []

    @calculated_property(schema={
        "title": "Replicates",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Replicate.experiment",
        },
    })
    def replicates(self, request, replicates):
        return paths_filtered_by_status(request, replicates)


@collection(
    name='replicates',
    acl=ALLOW_SUBMITTER_ADD,
    properties={
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    })
class Replicate(Item):
    item_type = 'replicate'
    schema = load_schema('encoded:schemas/replicate.json')
    embedded = [
        'antibody',
        'experiment',
        'library',
        'library.biosample',
        'library.biosample.donor',
        'library.biosample.donor.organism',
    ]

    def unique_keys(self, properties):
        keys = super(Replicate, self).unique_keys(properties)
        value = u'{experiment}/{biological_replicate_number}/{technical_replicate_number}'.format(
            **properties)
        keys.setdefault('replicate:experiment_biological_technical', []).append(value)
        return keys

    def __ac_local_roles__(self):
        properties = self.upgrade_properties()
        root = find_root(self)
        experiment = root.get_by_uuid(properties['experiment'])
        return experiment.__ac_local_roles__()
