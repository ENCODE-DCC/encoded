from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS

@upgrade_step('antibody_lot', '', '2')
def antibody_lot_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']


@upgrade_step('antibody_lot', '2', '3')
def antibody_lot_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
    	if value['status'] == 'DELETED':
    		value['status'] = 'deleted'
    	elif value['status'] == 'CURRENT' and value['award'] in ENCODE2_AWARDS:
    		value['status'] = 'released'
    	elif value['status'] == 'CURRENT' and value['award'] not in ENCODE2_AWARDS:
    		value['status'] = 'in progress'
