from pyramid.response import Response
from pyramid.view import view_config


def edges(source, linkTo, name, exclude):
    if isinstance(linkTo, basestring):
        linkTo = [linkTo]
    return [
        '%s -> %s [label="%s"];' % (source, target, name)
        for target in linkTo if target not in exclude
    ]


@view_config(route_name='graph', request_method='GET')
def schema(context, request):
    exclude = request.params.getall('exclude')
    out = ['digraph schema {']
    for source, collection in context.by_item_type.iteritems():
        if collection.schema is None:
            continue
        if source.startswith('testing_'):
            continue
        if source in exclude:
            continue
        for name, prop in collection.schema['properties'].iteritems():
            if 'linkTo' in prop:
                out.extend(edges(source, prop['linkTo'], name, exclude))
            elif 'linkTo' in prop.get('items', ()):
                out.extend(edges(source, prop['items']['linkTo'], name + ':array', exclude))
    out.append('}')
    return Response('\n'.join(out), content_type='text/vnd.graphviz')
