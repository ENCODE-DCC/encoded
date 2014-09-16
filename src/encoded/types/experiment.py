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
)
from .dataset import Dataset
from pyramid.traversal import (
    find_resource,
)
import datetime


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
            'organ_slims': [
                {'$value': '{slim}', '$repeat': 'slim organ_slims', '$templated': True}
            ],
            'system_slims': [
                {'$value': '{slim}', '$repeat': 'slim system_slims', '$templated': True}
            ],
            'developmental_slims': [
                {'$value': '{slim}', '$repeat': 'slim developmental_slims', '$templated': True}
            ],
            'synonyms': [
                {'$value': '{synonym}', '$repeat': 'synonym synonyms', '$templated': True}
            ],
            'month_released': {'$value': '{month_released}', '$templated': True, '$condition': 'date_released'},
            'run_type': {'$value': '{run_type}', '$templated': True, '$condition': 'replicates'},
        }
        embedded = Dataset.Item.embedded + [
            'replicates.antibody',
            'replicates.antibody.targets',
            'replicates.library.documents.lab',
            'replicates.library.documents.submitted_by',
            'replicates.library.documents.award',
            'replicates.library.biosample.submitted_by',
            'replicates.library.biosample.source',
            'replicates.library.biosample.organism',
            'replicates.library.biosample.treatments',
            'replicates.library.biosample.donor.organism',
            'replicates.library.biosample.treatments',
            'replicates.library.treatments',
            'replicates.platform',
            'possible_controls',
            'target.organism',
        ]
        rev = {
            'replicates': ('replicate', 'experiment'),
        }

        def template_namespace(self, properties, request=None):
            ns = super(Experiment.Item, self).template_namespace(properties, request)
            if request is None:
                return ns
            terms = request.registry['ontology']
            ns['run_type'] = ''
            if 'replicates' in ns:
                for replicate in ns['replicates']:
                    f = find_resource(request.root, replicate)
                    if 'paired_ended' in f.properties:
                        ns['run_type'] = 'Single-ended'
                        if f.properties['paired_ended'] is True:
                            ns['run_type'] = 'Paired-ended'
            if 'date_released' in ns:
                ns['month_released'] = datetime.datetime.strptime(ns['date_released'], '%Y-%m-%d').strftime('%B, %Y')
            if 'biosample_term_id' in ns:
                if ns['biosample_term_id'] in terms:
                    ns['organ_slims'] = terms[ns['biosample_term_id']]['organs']
                    ns['system_slims'] = terms[ns['biosample_term_id']]['systems']
                    ns['developmental_slims'] = terms[ns['biosample_term_id']]['developmental']
                    ns['synonyms'] = terms[ns['biosample_term_id']]['synonyms']
                else:
                    ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = ns['synonyms'] = []
            else:
                ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = ns['synonyms'] = []
            return ns


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
        parent_property = 'experiment'
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
        embedded = set(['library', 'platform'])
