from snovault.elasticsearch.searches.configs import search_config


def includeme(config):
    config.scan(__name__)


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
