"""\
Example.

    %(prog)s "https://www.encodeproject.org/search/?type=organism&frame=object"
"""
EPILOG = __doc__

import rdflib


def run(sources, output):
    g = rdflib.ConjunctiveGraph()
    for url in sources:
        g.parse(url, format='json-ld')
    g.serialize(output)


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description="Convert JSON-LD from source URLs to RDF", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('sources', metavar='URL', nargs='+', help="URLs to convert")
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
        help="Output file.")
    args = parser.parse_args()
    run(args.sources, args.output)


if __name__ == '__main__':
    main()
