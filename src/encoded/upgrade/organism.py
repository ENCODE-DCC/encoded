from snovault import upgrade_step


@upgrade_step('organism', '1', '2')
def organism_1_2(value, system):
    value['taxon_id'] = 'NCBI:' + value['ncbi_taxon_id']
    del value['ncbi_taxon_id']



@upgrade_step('organism', '2', '3')
def organism_2_3(value, system):
    if 'taxon_id' in value:
    	path = value['taxon_id'].split(':')
    	value['taxon_id'] = 'NCBITaxon:' + path[1]
