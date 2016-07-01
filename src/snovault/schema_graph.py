from collections import defaultdict
from past.builtins import basestring
from pyramid.response import Response
from pyramid.view import view_config
from subprocess import Popen, PIPE
from xml.sax.saxutils import quoteattr, escape
from snovault import TYPES


def includeme(config):
    config.add_route('graph_dot', '/profiles/graph.dot')
    config.add_route('graph_svg', '/profiles/graph.svg')
    config.scan(__name__)


def node(type_name, props):
    yield (
        '{type_name} [shape=plaintext label=<\n'
        '  <table border="1" cellborder="0" cellspacing="0" align="left">\n'
        '  <tr><td PORT="uuid" border="1" sides="B" bgcolor="lavender" href="/profiles/{type_name}.json">{type_name}</td></tr>'
    ).format(type_name=type_name)
    items = sorted(props.items())
    for name, prop in items:
        if name == 'uuid' or prop.get('calculatedProperty'):
            continue
        label = escape(name)
        if 'items' in prop:
            label += ' []'
            prop = prop['items']
        if 'linkTo' in prop:
            label = '<b>' + label + '</b>'
        yield '  <tr><td PORT={name}>{label}</td></tr>'.format(name=quoteattr(name), label=label)
    yield '  </table>>];'


def edges(source, name, linkTo, exclude, subclasses):
    if isinstance(linkTo, basestring):
        if linkTo in subclasses:
            linkTo = subclasses[linkTo]
        else:
            linkTo = [linkTo]
    exclude = [source] + exclude
    return [
        '{source}:{name} -> {target}:uuid;'.format(source=source, name=quoteattr(name), target=target)
        for target in linkTo if target not in exclude
    ]


def digraph(types, exclude=None):
    if not exclude:
        exclude = ['submitted_by', 'lab', 'award']
    out = [
        'digraph schema {',
        'rankdir=LR',
    ]

    subclasses = defaultdict(list)
    for type_info in sorted(types.values(), key=lambda ti: ti.name):
        for base in type_info.base_types[:-1]:
            subclasses[base].append(type_info.name)

    for type_info in sorted(types.values(), key=lambda ti: ti.name):
        if type_info.schema is None:
            continue
        if type_info.item_type.startswith('testing_'):
            continue
        out.extend(node(type_info.name, type_info.schema['properties']))
        for name, prop in type_info.schema['properties'].items():
            if name in exclude or prop.get('calculatedProperty'):
                continue
            prop = prop.get('items', prop)
            if 'linkTo' in prop:
                out.extend(edges(type_info.name, name, prop['linkTo'], exclude, subclasses))

    out.append('}')
    return '\n'.join(out)


@view_config(route_name='graph_dot', request_method='GET')
def schema_dot(request):
    dot = digraph(request.registry[TYPES].by_item_type, request.params.getall('exclude'))
    return Response(dot, content_type='text/vnd.graphviz', charset='utf-8')


@view_config(route_name='graph_svg', request_method='GET')
def schema_svg(request):
    dot = digraph(request.registry[TYPES].by_item_type, request.params.getall('exclude'))
    p = Popen(['dot', '-Tsvg'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    svg, err = p.communicate(dot.encode('utf-8'))
    assert p.returncode == 0, err.decode('utf-8')
    return Response(svg, content_type='image/svg+xml', charset='utf-8')
