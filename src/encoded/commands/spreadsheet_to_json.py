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


def convert(filename, sheetname=None, outputdir=None):
    if outputdir is None:
        outputdir = os.path.dirname(filename)
    source = loadxl.read_single_sheet(filename, sheetname)
    pipeline = [
        loadxl.remove_keys_with_empty_value,
        rename_test_with_underscore,
    ]
    data = list(loadxl.combine(source, pipeline))
    if sheetname is None:
        sheetname, ext = os.path.splitext(os.path.basename(filename))
    out = open(os.path.join(outputdir, sheetname + '.json'), 'w')
    json.dump(data, out, sort_keys=True, indent=4)



def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert spreadsheet to json list", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('filenames', metavar='FILE', nargs='+', help="Files to convert")
    parser.add_argument('--outputdir', help="Directory to write converted output")
    parser.add_argument('--sheetname', help="xlsx sheet name")
    args = parser.parse_args()

    for filename in args.filenames:
        convert(filename, args.sheetname, args.outputdir)


if __name__ == '__main__':
    main()
