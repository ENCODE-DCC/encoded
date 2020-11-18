import json

from snovault import upgrade_step


@upgrade_step('atac_peak_enrichment_quality_metric', '1', '2')
def atac_peak_enrichment_quality_metric_1_2(value, system):
    fri_to_move = {}
    if 'fri_blacklist' in value:
        fri_to_move['fri_blacklist'] = value['fri_blacklist']
        value.pop('fri_blacklist')
    if 'fri_dhs' in value:
        fri_to_move['fri_dhs'] = value['fri_dhs']
        value.pop('fri_dhs')
    if 'fri_enh' in value:
        fri_to_move['fri_enh'] = value['fri_enh']
        value.pop('fri_enh')
    if 'fri_prom' in value:
        fri_to_move['fri_prom'] = value['fri_prom']
        value.pop('fri_prom')
    new_notes = value.get('notes', '') + json.dumps(fri_to_move, sort_keys=True)
    value['notes'] = new_notes
