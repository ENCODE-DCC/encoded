from ..migrator import upgrade_step


@upgrade_step('treatment', '', '2')
def treatment_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxref'] = []
   
    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'ucsc_encode_db:' + encode2_dbxref
            value['dbxref'].append(new_dbxref)
        del value['encode2_dbxrefs']