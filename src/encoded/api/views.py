from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )


@view_config(route_name='home', request_method='GET')
def home(request):
    result = {
        'title': 'Home',
        'portal_title': 'ENCODE 3',
        '_links': {
            'self': {'href': request.route_path('home')},
            'profile': {'href': '/profiles/portal'},
            # 'login': {'href': request.route_path('login')},
            },
        }
    return result


@view_config(route_name='antibodies', request_method='GET')
def antibodies(request):
    session = DBSession()
    query = session.query(CurrentStatement).filter(CurrentStatement.predicate == 'antibody')
    collection_uri = request.route_path('antibodies')
    items = []
    for model in query.all():
        item = model.statement.__json__()
        item['_links'] = {
            'self': {'href': request.route_path('antibody', antibody=model.rid)},
            'collection': {'href': collection_uri},
            }
        items.append(item)
    result = {
        'title': 'Antibodies registry',
        'description': 'Listing of antibodies returned from server',
        '_embedded': {
            'item': items,
            },
        '_links': {
            'self': {'href': collection_uri},
            '/rels/actions': [
                {
                    'name': 'add-antibody',
                    'title': 'Add antibody',
                    'method': 'POST',
                    'type': 'application/json',
                    'href': collection_uri,
                    }
                ],
            },
        }
    return result


@view_config(route_name='antibodies', request_method='POST')
def create_antibody(request):
    session = DBSession()
    resource = Resource({'antibody': request.json_body})
    session.add(resource)
    item_uri = request.route_path('antibody', antibody=resource.rid)
    request.response.status = 201
    request.response.location = item_uri
    result = {
        'result': 'success',
        '_links': {
            'profile': {'href': '/profiles/result'},
            'item': [
                {'href': item_uri},
                ],
            },
        }
    return result


@view_config(route_name='antibody', request_method='GET')
def antibody(request):
    key = (request.matchdict['antibody'], 'antibody')
    session = DBSession()
    model = session.query(CurrentStatement).get(key)
    item_uri = request.route_path('antibody', antibody=model.rid)
    collection_uri = request.route_path('antibodies')
    result = model.statement.__json__()
    result['_links'] = {
        '/rels/actions': [
            {
                'name': 'save',
                'title': 'Save',
                'method': 'POST',
                'type': 'application/json',
                'href': item_uri,
                },
            ],
        'self': {'href': item_uri},
        'collection': {'href': collection_uri},
        'profile': {'href': '/profiles/antibody'},
        }
    return result
