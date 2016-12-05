#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import os.path
import argparse
import encodedcc

EPILOG = '''
Input file should be a TSV (tab separated value) file with headers
if the field value is a non-string value, list its type separated by a colon

accession   header1  header2:list  header3:int ...
ENCSR000AAA value1   list1,list2   value3  ...

Whatever data is used to identify the object (accession, uuid, alias)
goes in the accession column to be used for identification of object

Examples:

To PATCH data run with update comamnd:

        %(prog)s --update

To PATCH a single object, field with field type, and data:

        %(prog)s --accession ENCSR000AAA --field assay_term_name --data ChIP-seq
        %(prog)s --accession ENCSR000AAA --field read_length:int --data 31
        %(prog)s --accession ENCSR000AAA --field documents:list --data document1,document2

    for integers use ':int' or ':integer'
    for lists use    ':list' or ':array'
    lists are appended to unless the --overwite command is used
    string are the default and do not require an identifier

To PATCH flowcells:

        %(prog)s --flowcell

    the "flowcell" option is a flag used to have the script search for\
    flowcell data in the infile

    accession   flowcell   lane    barcode   machine
    ENCSR000AAA value1     value2  value3    value4

    not all the columns are needed for the flowcell to be built


Removing Data:
Data can be removed with the '--remove' option, but must be run with '--update'

To remove individual items from a list you must also tag the column header as such,\
otherwise it will remove the entire list

    accession   listobject:list
    ENCSR000AAA item1,item2

This will remove "item1" and "item2" from the list\
but you need to use the FULL NAME of the object
Ex: "/files/ENCFF000ABD/"
NOT: "file/ENCFF000ABD"

To remove an entire list object, don't include the ":list"/":array" tag

    accession   listobject
    ENCSR000AAA

This will completely remove listobject regardless of whatever else is in the column below it
'''


def getArgs():
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('--infile',
                        help="A minimum two column list with identifier and value to \
                        patch")
    parser.add_argument('--key',
                        default='default',
                        help="The keypair identifier from the keyfile.  \
                        Default is --key=default")
    parser.add_argument('--keyfile',
                        default=os.path.expanduser("~/keypairs.json"),
                        help="The keypair file.  Default is --keyfile=%s" % (os.path.expanduser("~/keypairs.json")))
    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help="Print debug messages.  Default is False.")
    parser.add_argument('--remove',
                        default=False,
                        action='store_true',
                        help="Patch to remove the value specified in the input \
                        file from the given field.  Requires --update to work. Default is False.")
    parser.add_argument('--update',
                        default=False,
                        action='store_true',
                        help="Let the script PATCH the data.  Default is False")
    parser.add_argument('--accession',
                        help="Single accession/identifier to patch")
    parser.add_argument('--field',
                        help="Field for single accession, input needs to have the field type listed\
                                Ex: --field read_length:int    --field documents:list\
                                strings don't need to have their type listed")
    parser.add_argument('--data',
                        help='Data for single accession')
    parser.add_argument('--overwrite',
                        help="If field is an list then overwrite it with new data. Default is False, and data is appended",
                        action='store_true',
                        default=False)
    parser.add_argument('--flowcell',
                        default=False,
                        action='store_true',
                        help="used when file contains flowcell information\
                        script will seek out the flowcell data and build flowcells\
                        unless --overwrite is used flowcells will append data")
    args = parser.parse_args()
    return args


def main():

    args = getArgs()
    key = encodedcc.ENC_Key(args.keyfile, args.key)
    connection = encodedcc.ENC_Connection(key)

    encodedcc.patch_set(args, connection)

if __name__ == '__main__':
        main()
