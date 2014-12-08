from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    ALIAS_KEYS,
    Collection,
    paths_filtered_by_status,
)
from .dataset import Dataset
from pyramid.traversal import (
    find_resource,
)
import datetime


def run_type(root, registry, replicates):
    for replicate in replicates:
        properties = find_resource(root, replicate).upgrade_properties()
        if properties.get('status') in ('deleted', 'replaced'):
            continue
        if 'paired_ended' in properties:
            return 'Paired-ended' if properties['paired_ended'] else 'Single-ended'


@location('experiments')
class Experiment(Dataset):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }

    class Item(Dataset.Item):
        base_types = [Dataset.item_type] + Dataset.Item.base_types
        template = {
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
                lambda root, replicates: paths_filtered_by_status(root, replicates)
            ),
        }
        embedded = Dataset.Item.embedded + [
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
        audit_inherit = list(embedded)
        audit_inherit.remove('possible_controls')
        audit_inherit.remove('replicates.library.documents.submitted_by')
        audit_inherit.remove('replicates.library.documents.award')
        audit_inherit.remove('replicates.library.biosample.submitted_by')
        audit_inherit.remove('replicates.library.biosample.source')
        audit_inherit.append('replicates.library.biosample.donor')
        audit_inherit.append('replicates.antibody.characterizations')
        rev = {
            'replicates': ('replicate', 'experiment'),
        }


@location('replicates')
class Replicates(Collection):
    item_type = 'replicate'
    schema = load_schema('replicate.json')
    __acl__ = ALLOW_SUBMITTER_ADD
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }

    class Item(Collection.Item):
        namespace_from_path = {
            'lab': 'experiment.lab',
            'award': 'experiment.award',
        }
        keys = ALIAS_KEYS + [
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
