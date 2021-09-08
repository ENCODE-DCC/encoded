from pyramid.view import view_config
from encoded.vis_defines import vis_format_url
from snovault import TYPES
from .batch_download import get_peak_metadata_links
from collections import OrderedDict
import requests
from urllib.parse import urlencode

def includeme(config):
    config.add_route('new-home-page', '/new-home-page{slash:/?}')
    config.scan(__name__)
    
@view_config(route_name='new-home-page', request_method='GET', permission='search')
def new_home_page(context, request):
    result = {
        '@id': '/region-search/' + ('?' + request.query_string.split('&referrer')[0] if request.query_string else ''),
        '@type': ['new-home-page'],
        'title': 'Search by region',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }

    return result
