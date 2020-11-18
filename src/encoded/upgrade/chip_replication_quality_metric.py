from snovault import (
    CONNECTION,
    upgrade_step
)
@upgrade_step('chip_replication_quality_metric', '1', '2')
def chip_peak_enrichment_quality_metric_1_2(value, system):
    if 'IDR_dispersion_plot' in value:
        value['idr_dispersion_plot'] = value['IDR_dispersion_plot']
        value.pop('IDR_dispersion_plot')
