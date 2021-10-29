from snovault.elasticsearch.searches.interfaces import SEARCH_CONFIG
from snovault.elasticsearch.searches.configs import search_config


def includeme(config):
    config.scan(__name__)
    config.registry[SEARCH_CONFIG].add_aliases(ALIASES)
    config.registry[SEARCH_CONFIG].add_defaults(DEFAULTS)


@search_config(
    name='custom'
)
def custom_search_config():
    return {
        'facets': {
            'assay_title': {
                'title': 'Assay title',
                'type': 'typeahead',
                'open_on_load': True
            },
            'status': {
                'title': 'Status',
                "open_on_load": True
            },
            'target.label': {
                'title': 'Target of assay',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
            'biosample_ontology.term_name' : {
                'title': 'Biosample term name',
                'type': 'typeahead',
                'length': 'long',
                "open_on_load": True
            },
        },
        'columns': {},
        'matrix': {},
        'boost_values': {},
        'fields': {},
    }


@search_config(
    name='custom-matrix'
)
def custom_matrix_config():
    return {
        'matrix': {
            'y': {
                'group_by': [
                    'award.rfa',
                    'lab.title',
                ],
                'label': 'Lab',
            },
            'x': {
                'group_by': 'assay_title',
                'label': 'Assay',
            }
        }
    }


@search_config(
    name='custom-columns'
)
def custom_columns_config():
    return {
        'columns': {
            'award.rfa': {
                'title': 'Project',
            },
            'assay_title': {
                'title': 'Assay',
            },
            'lab.title': {
                'title': 'Lab',
            },
            'assembly': {
                'title': 'Assembly',
            },
            'status': {
                'title': 'Status',
            },
        }
    }


ALIASES = {
    'DonorSubtypes': [
        'HumanDonor',
        'FlyDonor',
        'WormDonor',
        'MouseDonor',
    ]
}


DEFAULTS = {
    'Donor': ['DonorSubtypes'],
    ('Experiment', 'FunctionalCharacterizationExperiment'): ['Experiment'],
}
