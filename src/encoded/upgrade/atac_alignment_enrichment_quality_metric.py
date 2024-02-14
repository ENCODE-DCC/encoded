import json

from snovault import upgrade_step


@upgrade_step('atac_alignment_enrichment_quality_metric', '1', '2')
def atac_alignment_enrichment_quality_metric_1_2(value, system):
    if 'fri_blacklist' in value:
        value['fri_exclusion_list'] = value['fri_blacklist']
        value.pop('fri_blacklist')
