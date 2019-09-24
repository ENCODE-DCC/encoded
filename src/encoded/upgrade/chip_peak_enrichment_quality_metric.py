from snovault import (
    CONNECTION,
    upgrade_step
)

@upgrade_step('chip_peak_enrichment_quality_metric', '1', '2')
def chip_peak_enrichment_quality_metric_1_2(value, system):
    if 'FRiP' in value:
        value['frip'] = value['FRiP']
        value.pop('FRiP')
