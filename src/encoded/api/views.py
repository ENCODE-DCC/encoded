from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )


MODELS = [
    {
        'uuid': 'a0000000000000000000000000000001',
        'title': 'First model',
        },
    {
        'uuid': 'b0000000000000000000000000000002',
        'title': 'Second model',
        },
    {
        'uuid': 'c0000000000000000000000000000003',
        'title': 'Third model',
        },
    ]


@view_config(route_name='home', request_method='GET')
def home(request):
    return {}


@view_config(route_name='antibodies', request_method='GET')
def antibodies(request):
    session = DBSession()
    query = session.query(CurrentStatement).filter(CurrentStatement.predicate == 'antibody')
    return {'items': [model.statement for model in query.all()]}


@view_config(route_name='antibodies', request_method='POST')
def create_antibody(request):
    session = DBSession()
    resource = Resource({'antibody': request.json_body})
    session.add(resource)
    request.response.status = 201
    request.response.location = request.route_url('antibody', antibody=resource.rid)
    return resource.data['antibody'].statement


@view_config(route_name='antibody', request_method='GET')
def antibody(request):
    key = (request.matchdict['antibody'], 'antibody')
    session = DBSession()
    model = session.query(CurrentStatement).get(key)
    return model.statement
