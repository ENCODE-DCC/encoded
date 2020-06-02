from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

from collections import OrderedDict

from snovault import COLLECTIONS


CART_USER_MAX = 30  # Maximum number of non-deleted carts allowed per user


def includeme(config):
    # config.scan()
    config.add_route('cart-view', '/cohort-view{slash:/?}')
    config.add_route('cart-manager', '/cohort-manager{slash:/?}')
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
        '@id': '/cohort-view/',
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
    blocked_statuses = ['deleted'] if 'group.admin' not in request.effective_principals else []
    user_carts = get_cart_objects_by_user(request, userid, blocked_statuses)
    # Calculate the element count in each cart, but remove the elements
    # themselves as this list can be huge.
    for c in user_carts:
        c['element_count'] = len(c['elements'])
        del c['elements']
    result = {
        '@id': '/cohort-manager/',
        '@type': ['cart-manager'],
        'title': 'Cohort',
        'facets': [],
        '@graph': user_carts,
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'cart_user_max': CART_USER_MAX
    }
    return result
