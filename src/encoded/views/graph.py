from collections import defaultdict
from past.builtins import basestring
from pyramid.response import Response
from pyramid.view import view_config
from subprocess import Popen, PIPE


def node(item_type, props):
    yield (
        '{item_type} [shape=plaintext label=<\n'
        '  <table border="1" cellborder="0" cellspacing="0" align="left">\n'
        '  <tr><td PORT="uuid" border="1" sides="B" bgcolor="lavender" href="/profiles/{item_type}.json">{item_type}</td></tr>'
    ).format(item_type=item_type)
    items = sorted(props.items())
    for name, prop in items:
        if name == 'uuid':
            continue
        label = name
        if 'items' in prop:
            label += ' []'
            prop = prop['items']
        if 'linkTo' in prop:
            label = '<b>' + label + '</b>'
        yield '  <tr><td PORT="{name}">{label}</td></tr>'.format(name=name, label=label)
    yield '  </table>>];'


def edges(source, name, linkTo, exclude, subclasses):
    if isinstance(linkTo, basestring):
        if linkTo in subclasses:
            linkTo = subclasses[linkTo]
        else:
            linkTo = [linkTo]
    exclude = [source] + exclude
    return [
        '{source}:{name} -> {target}:uuid;'.format(source=source, name=name, target=target)
        for target in linkTo if target not in exclude
    ]


def digraph(root, exclude=None):
    if not exclude:
        exclude = ['submitted_by', 'lab', 'award']
    out = [
        'digraph schema {',
        'rankdir=LR',
    ]

    subclasses = defaultdict(list)
    for source, collection in root.by_item_type.items():
        for base in collection.type_info.base_types[:-1]:
            subclasses[base].append(source)

    for source, collection in root.by_item_type.items():
        if collection.type_info.schema is None:
            continue
        if source.startswith('testing_'):
            continue
        if source == 'antibody_approval':
            continue
        out.extend(node(source, collection.type_info.schema['properties']))
        for name, prop in collection.type_info.schema['properties'].items():
            if name in exclude:
                continue
            prop = prop.get('items', prop)
            if 'linkTo' in prop:
                out.extend(edges(source, name, prop['linkTo'], exclude, subclasses))

    out.append('}')
    return '\n'.join(out)


@view_config(route_name='graph_dot', request_method='GET')
def schema_dot(request):
    dot = digraph(request.root, request.params.getall('exclude'))
    return Response(dot, content_type='text/vnd.graphviz')


@view_config(route_name='graph_svg', request_method='GET')
def schema_svg(request):
    dot = digraph(request.root, request.params.getall('exclude'))
    p = Popen(['dot', '-Tsvg'], stdin=PIPE, stdout=PIPE)
    svg, err = p.communicate(dot)
    return Response(svg, content_type='image/svg+xml')
