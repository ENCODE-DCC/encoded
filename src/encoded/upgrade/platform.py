from ..migrator import upgrade_step


@upgrade_step('platform', '', '2')
def dataset_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []
   
    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']
    
    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'GEO:' + geo_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['geo_dbxrefs']
