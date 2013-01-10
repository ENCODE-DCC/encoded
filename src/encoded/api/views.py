from pyramid.view import view_config


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

uuid_model = {model['uuid']: model for model in MODELS}


@view_config(route_name='home')
def home(request):
    return {}


@view_config(route_name='antibodies')
def antibodies(request):
    return MODELS


@view_config(route_name='antibody')
def antibody(request):
    antibody_id = request.matchdict['antibody']
    model = uuid_model[antibody_id]
    return model
