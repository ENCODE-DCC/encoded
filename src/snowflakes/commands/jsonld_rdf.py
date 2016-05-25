"""\
Available formats: xml, n3, turtle, nt, pretty-xml, trix.
Example.

    %(prog)s "$SITE_URL/search/?type=Item&frame=object"
"""
EPILOG = __doc__

import rdflib


def run(sources, output, parser='json-ld', serializer='xml', base=None):
    g = rdflib.ConjunctiveGraph()
    for url in sources:
        g.parse(url, format=parser)
    g.serialize(output, format=serializer, base=base)


def main():
    import argparse
    import sys
    stdout = sys.stdout
    if sys.version_info.major > 2:
        stdout = stdout.buffer

    rdflib_parsers = sorted(
        p.name for p in rdflib.plugin.plugins(kind=rdflib.parser.Parser)
        if '/' not in p.name)
    rdflib_serializers = sorted(
        p.name for p in rdflib.plugin.plugins(kind=rdflib.serializer.Serializer)
        if '/' not in p.name)
    parser = argparse.ArgumentParser(
        description="Convert JSON-LD from source URLs to RDF", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('sources', metavar='URL', nargs='+', help="URLs to convert")
    parser.add_argument(
        '-p', '--parser', default='json-ld', help=', '.join(rdflib_parsers))
    parser.add_argument(
        '-s', '--serializer', default='xml', help=', '.join(rdflib_serializers))
    parser.add_argument(
        '-b', '--base', default=None, help='Base URL')
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('wb'), default=stdout,
        help="Output file.")
    args = parser.parse_args()
    run(args.sources, args.output, args.parser, args.serializer, args.base)


if __name__ == '__main__':
    main()
