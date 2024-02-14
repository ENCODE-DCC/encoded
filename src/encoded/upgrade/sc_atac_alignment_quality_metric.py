from snovault import upgrade_step


@upgrade_step('sc_atac_alignment_quality_metric', '1', '2')
def sc_atac_alignment_quality_metric_1_2(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-6183
    if 'pct_properly_paired_reads' in value:
        value['frac_properly_paired_reads'] = value.pop('pct_properly_paired_reads')
    if 'pct_mapped_reads' in value:
        value['frac_mapped_reads'] = value.pop('pct_mapped_reads')
    if 'pct_singletons' in value:
        value['frac_singletons'] = value.pop('pct_singletons')

@upgrade_step('sc_atac_alignment_quality_metric', '2', '3')
def sc_atac_alignment_quality_metric_2_3(value, system):
    # https://igvf.atlassian.net/browse/ENCM-58
    if 'usable_fragments' in value:
        del value['usable_fragments']
