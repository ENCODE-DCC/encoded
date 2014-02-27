from ..migrator import upgrade_step


@upgrade_step('platfrom', '', '2')
def dataset_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxref'] = []
   
    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'ucsc_encode_db:' + encode2_dbxref
            value['dbxref'].append(new_dbxref)
        del value['encode2_dbxrefs']
    
    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'geo_db:' + geo_dbxref
            value['dbxref'].append(new_dbxref)
        del value['geo_dbxrefs']