from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )


@view_config(route_name='home', request_method='GET')
def home(request):
    result = {
        'class': ['portal'],
        'properties': {
            'title': 'Home',
            'portal_title': 'ENCODE 3',
            },
        'links': [
            {'rel': ['self'], 'href': request.route_url('home')},
            # {'rel': ['login'], 'href': request.route_url('login')},
            ],
        }
    return result


@view_config(route_name='antibodies', request_method='GET')
def antibodies(request):
    session = DBSession()
    query = session.query(CurrentStatement).filter(CurrentStatement.predicate == 'antibody')
    collection_uri = request.route_url('antibodies')
    items = [{
        'rel': ['item'],
        'class': ['antibody'],
        'properties': model.statement,
        'links': [
            {'rel': ['self'], 'href': request.route_url('antibody', antibody=model.rid)},
            {'rel': ['collection'], 'href': collection_uri},
            ],
        } for model in query.all()]
    result = {
        'class': ['collection:antibodies', 'collection'],
        'properties': {
            'title': 'Antibodies registry',
            'description': 'Listing of antibodies returned from server',
            },
        'entities': items,
        'actions': {
            'name': 'add-antibody',
            'title': 'Add antibody',
            'method': 'POST',
            'type': 'application/json',
            'href': collection_uri,
        },
        'links': [
            {'rel': ['self'], 'href': collection_uri},
            ],
        }
    return result


@view_config(route_name='antibodies', request_method='POST')
def create_antibody(request):
    session = DBSession()
    resource = Resource({'antibody': request.json_body})
    session.add(resource)
    item_uri = request.route_url('antibody', antibody=resource.rid)
    request.response.status = 201
    request.response.location = item_uri
    result = {
        'class': ['result:success', 'result'],
        'entities': [
            {'rel': ['item'], 'href': item_uri},
            ],
        }
    return result


@view_config(route_name='antibody', request_method='GET')
def antibody(request):
    key = (request.matchdict['antibody'], 'antibody')
    session = DBSession()
    model = session.query(CurrentStatement).get(key)
    item_uri = request.route_url('antibody', antibody=model.rid)
    collection_uri = request.route_url('antibodies')
    result = {
        'class': ['antibody'],
        'properties': model.statement,
        'actions': {
            'name': 'save',
            'title': 'Save',
            'method': 'POST',
            'type': 'application/json',
            'href': collection_uri,
        },
        'links': [
            {'rel': ['self'], 'href': item_uri},
            {'rel': ['collection'], 'href': collection_uri},
            ],
        }
    return result
