from ..migrator import upgrade_step


@upgrade_step('antibody_lot', '', '2')
def antibody_lot_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []
   
    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'ucsc_encode_db:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']
        
