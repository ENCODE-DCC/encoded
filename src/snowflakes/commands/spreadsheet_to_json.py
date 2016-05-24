"""
Example:

    %(prog)s *.tsv

"""

from .. import loadxl
import json
import os.path

EPILOG = __doc__


def rename_test_with_underscore(rows):
    for row in rows:
        if 'test' in row:
            if row['test'] != 'test':
                row['_test'] = row['test']
            del row['test']
        yield row


def remove_empty(rows):
    for row in rows:
        if row:
            yield row


def convert(filename, sheetname=None, outputdir=None, skip_blanks=False):
    if outputdir is None:
        outputdir = os.path.dirname(filename)
    source = loadxl.read_single_sheet(filename, sheetname)
    pipeline = [
        loadxl.remove_keys_with_empty_value if skip_blanks else loadxl.noop,
        rename_test_with_underscore,
        remove_empty,
    ]
    data = list(loadxl.combine(source, pipeline))
    if sheetname is None:
        sheetname, ext = os.path.splitext(os.path.basename(filename))
    out = open(os.path.join(outputdir, sheetname + '.json'), 'w')
    json.dump(data, out, sort_keys=True, indent=4, separators=(',', ': '))



def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert spreadsheet to json list", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('filenames', metavar='FILE', nargs='+', help="Files to convert")
    parser.add_argument('--outputdir', help="Directory to write converted output")
    parser.add_argument('--sheetname', help="xlsx sheet name")
    parser.add_argument('--skip-blanks', help="Skip blank columns")
    args = parser.parse_args()

    for filename in args.filenames:
        convert(filename, args.sheetname, args.outputdir, args.skip_blanks)


if __name__ == '__main__':
    main()
