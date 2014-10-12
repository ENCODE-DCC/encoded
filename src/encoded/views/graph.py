from collections import defaultdict
from pyramid.response import Response
from pyramid.view import view_config


def node(name, props):
    yield '%s [shape=plaintext label=<' % name
    yield '  <table border="1" cellborder="0" cellspacing="0" align="left">'
    yield '  <tr><td PORT="uuid" BGCOLOR="Lavender">%s</td></tr>' % name
    items = sorted(props.items())
    for name, prop in items:
        if name == 'uuid':
            continue
        label = name
        if 'items' in prop:
            label += ' []'
            prop = prop['items']
        if 'linkTo' in prop:
            label = '* ' + label
        yield '<tr><td PORT="%s">%s</td></tr>' % (name, label)
    yield '  </table>>];'


def edges(source, name, linkTo, exclude, subclasses):
    if isinstance(linkTo, basestring):
        if linkTo in subclasses:
            linkTo = subclasses[linkTo]
        else:
            linkTo = [linkTo]
    exclude = [source] + exclude
    return [
        '%s:%s -> %s:uuid;' % (source, name, target)
        for target in linkTo if target not in exclude
    ]


@view_config(route_name='graph', request_method='GET')
def schema(context, request):
    exclude = request.params.getall('exclude') or ['submitted_by', 'lab', 'award']
    out = [
        'digraph schema {',
        'rankdir=LR',
    ]

    subclasses = defaultdict(list)
    for source, collection in context.by_item_type.iteritems():
        for base in collection.Item.base_types[:-1]:
            subclasses[base].append(source)

    for source, collection in context.by_item_type.iteritems():
        if collection.schema is None:
            continue
        if source.startswith('testing_'):
            continue
        if source == 'antibody_approval':
            continue
        out.extend(node(source, collection.schema['properties']))
        for name, prop in collection.schema['properties'].iteritems():
            if name in exclude:
                continue
            prop = prop.get('items', prop)
            if 'linkTo' in prop:
                out.extend(edges(source, name, prop['linkTo'], exclude, subclasses))

    out.append('}')
    return Response('\n'.join(out), content_type='text/vnd.graphviz')
