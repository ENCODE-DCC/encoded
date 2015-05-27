from contentbase.upgrader import upgrade_step
import re


@upgrade_step('treatment', '', '2')
def treatment_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1182
    if 'award' in value:
        del value['award']

    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            if re.match('^encode:.*', encode2_dbxref):
                new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref.replace('encode:', '')
            else:
                new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']


@upgrade_step('treatment', '2', '3')
def treatment_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()
