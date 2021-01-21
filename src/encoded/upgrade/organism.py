from snovault import upgrade_step


@upgrade_step('organism', '1', '2')
def organism_1_2(value, system):
    value['taxon_id'] = 'NCBI:' + value['ncbi_taxon_id']
    del value['ncbi_taxon_id']
