from snovault import upgrade_step
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


@upgrade_step('treatment', '3', '4')
def treatment_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'protocols' in value:
        value['protocols'] = list(set(value['protocols']))


@upgrade_step('treatment', '4', '5')
def treatment_4_5(value, system):
    # http://redmine.encodedcc.org/issues/1483#note-20
    # http://redmine.encodedcc.org/issues/4448
    if 'protocols' in value:
        value['documents'] = value['protocols']
        value.pop('protocols')

    if 'antibodies' in value:
        value['antibodies_used'] = value['antibodies']
        value.pop('antibodies')

    if 'concentration' in value:
        # http://redmine.encodedcc.org/issues/4385. At the time of upgrade, there were
        # no values without units and from v5 on, will be enforced by dependencies.
        value['amount'] = value['concentration']
        value['amount_units'] = value['concentration_units']
        value.pop('concentration')
        value.pop('concentration_units')


@upgrade_step('treatment', '5', '6')
def treatment_5_6(value, system):
    # http://redmine.encodedcc.org/issues/1384
    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']


@upgrade_step('treatment', '8', '9')
def treatment_8_9(value, system):
    # The namespace for UniProt is UniProtKB everywhere but in this object, where it was UniprotKB
    if 'treatment_term_id' in value:
        parts = value['treatment_term_id'].split(':')
        namespace = parts[0]
        if namespace == 'UniprotKB':
            value['treatment_term_id'] = 'UniProtKB:' + parts[1]
