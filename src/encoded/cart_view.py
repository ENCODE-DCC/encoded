from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from urllib.parse import (
    parse_qs,
    urlencode,
)

from collections import OrderedDict

from snovault import COLLECTIONS


CART_USER_MAX = 30  # Maximum number of non-deleted carts allowed per non-admin user
CART_ADMIN_MAX = 200  # Maximum per admin user


def includeme(config):
    # config.scan()
    config.add_route('cart-view', '/cart-view{slash:/?}')
    config.add_route('cart-manager', '/cart-manager{slash:/?}')
    config.add_route('search_elements', '/search_elements/{search_params}')
    config.scan(__name__)


def get_userid(request):
    userid = [
        p.replace('userid.', '')
        for p in request.effective_principals
        if p.startswith('userid.')
    ]
    if not userid:
        raise HTTPBadRequest()
    return userid[0]


def get_cart_objects_by_user(request, userid, blocked_statuses=[]):
    request.datastore = 'database'
    return [
        dict(v.properties, **{'@id': request.resource_path(v)})
        for k, v in request.registry[COLLECTIONS]['cart'].items()
        if v.properties['submitted_by'] == userid and v.properties['status'] not in blocked_statuses
    ]


@view_config(route_name='cart-view', request_method='GET', permission='search')
def cart_view(context, request):
    result = {
        '@id': '/cart-view/',
        '@type': ['cart-view'],
        'title': 'Cohort',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }
    return result


@view_config(route_name='cart-manager', request_method='GET', permission='search')
def cart_manager(context, request):
    '''Cohort manager page context object generation'''
    userid = get_userid(request)
    is_admin = 'group.admin' in request.effective_principals
    blocked_statuses = ['deleted'] if not is_admin else []
    user_carts = get_cart_objects_by_user(request, userid, blocked_statuses)
    # Calculate the element count in each cart, but remove the elements
    # themselves as this list can be huge.
    for c in user_carts:
        c['element_count'] = len(c['elements'])
        del c['elements']
    result = {
        '@id': '/cart-manager/',
        '@type': ['cart-manager'],
        'title': 'Cohort',
        'facets': [],
        '@graph': user_carts,
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'cart_user_max': CART_ADMIN_MAX if is_admin else CART_USER_MAX
    }
    return result


@view_config(route_name='search_elements', request_method='POST')
def search_elements(context, request):
    '''Same as search but takes JSON payload of search filters'''
    param_list = parse_qs(request.matchdict['search_params'])
    param_list.update(request.json_body)
    path = '/search/?%s' % urlencode(param_list, True)
    results = request.embed(path, as_user=True)
    return results
