from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
)
from .dataset import Dataset
import datetime


def run_type(request, replicates):
    for replicate in replicates:
        properties = request.embed(replicate, '@@object')
        if properties.get('status') in ('deleted', 'replaced'):
            continue
        if 'paired_ended' in properties:
            return 'Paired-ended' if properties['paired_ended'] else 'Single-ended'


@location(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    base_types = [Dataset.item_type] + Dataset.base_types
    template = Dataset.template.copy()
    template.update({
        'organ_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['organs']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'system_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['systems']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'developmental_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['developmental']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'biosample_synonyms': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['synonyms']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'assay_synonyms': {
            '$value': (
                lambda registry, assay_term_id:
                    # Add synonym and names since using differnt names for facet display
                    registry['ontology'][assay_term_id]['synonyms'] +
                    [registry['ontology'][assay_term_id]['name']]
                    if assay_term_id in registry['ontology'] else []
            ),
            '$condition': 'assay_term_id',
        },
        'month_released': {
            '$value': lambda date_released: datetime.datetime.strptime(
                date_released, '%Y-%m-%d').strftime('%B, %Y'),
            '$condition': 'date_released',
        },
        'run_type': {
            '$value': run_type,
            '$condition': run_type,
        },
        'replicates': (
            lambda request, replicates: paths_filtered_by_status(request, replicates)
        ),
    })
    embedded = Dataset.embedded + [
        'files.platform',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents.lab',
        'replicates.library.documents.submitted_by',
        'replicates.library.documents.award',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'replicates.platform',
        'possible_controls',
        'target.organism',
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
        'replicates.platform',
        'target.organism',
    ]

    rev = Dataset.rev.copy()
    rev.update({
        'replicates': ('replicate', 'experiment'),
    })


@location(
    name='replicates',
    acl=ALLOW_SUBMITTER_ADD,
    properties={
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    })
class Replicates(Item):
    item_type = 'replicate'
    schema = load_schema('replicate.json')
    namespace_from_path = {
        'lab': 'experiment.lab',
        'award': 'experiment.award',
    }
    template_keys = [
        {
            'name': '{item_type}:experiment_biological_technical',
            'value': '{experiment}/{biological_replicate_number}/{technical_replicate_number}',
            '$templated': True,
        },
    ]
    embedded = [
        'library',
        'platform',
    ]
