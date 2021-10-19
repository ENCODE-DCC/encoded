from snovault import upgrade_step


@upgrade_step('sc_atac_library_complexity_quality_metric', '1', '2')
def sc_atac_library_complexity_quality_metric_1_2(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-6183
    if 'pct_duplicate_reads' in value:
        value['frac_duplicate_reads'] = value['pct_duplicate_reads']
        value.pop('pct_duplicate_reads')
