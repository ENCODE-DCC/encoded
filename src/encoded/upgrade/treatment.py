from ..migrator import upgrade_step
import re


@upgrade_step('treatment', '', '2')
def treatment_0_2(value, system):
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
