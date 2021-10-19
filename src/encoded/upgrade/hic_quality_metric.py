from snovault import upgrade_step


@upgrade_step('hic_quality_metric', '1', '2')
def hic_quality_metric_1_2(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-6183
    if 'alignable_normal_and_chimeric_paired' in value:
        value['2_alignments'] = value['alignable_normal_and_chimeric_paired']
        value.pop('alignable_normal_and_chimeric_paired')
    if 'chimeric_ambiguous' in value:
        value['3_or_more_alignments'] = value['chimeric_ambiguous']
        value.pop('chimeric_ambiguous')
    if 'chimeric_paired' in value:
        value['2_alignments_a1_a2b_a1b2_b1a2'] = value['chimeric_paired']
        value.pop('chimeric_paired')
    elif 'chimeric_paired' not in value:
        value['2_alignments_a1_a2b_a1b2_b1a2'] = 22
    if 'duplicates' in value:
        value['total_duplicates'] = value['duplicates']
        value.pop('duplicates')
    if 'normal_paired' in value:
        value['2_alignments_a_b'] = value['normal_paired']
        value.pop('normal_paired')
    elif 'normal_paired' not in value:
        value['2_alignments_a_b'] = 22
    if 'pct_alignable_duplicates' in value:
        value['pct_2_alignment_duplicates'] = value['pct_alignable_duplicates']
        value.pop('pct_alignable_duplicates')
    if 'pct_alignable_normal_and_chimeric_paired' in value:
        value['pct_2_alignments'] = value['pct_alignable_normal_and_chimeric_paired']
        value.pop('pct_alignable_normal_and_chimeric_paired')
    if 'pct_alignable_unique_reads' in value:
        value['pct_2_alignment_unique'] = value['pct_alignable_unique_reads']
        value.pop('pct_alignable_unique_reads')
    if 'pct_chimeric_ambiguous' in value:
        value['pct_3_or_more_alignments'] = value['pct_chimeric_ambiguous']
        value.pop('pct_chimeric_ambiguous')
    if 'pct_chimeric_paired' in value:
        value['pct_2_alignments_a1_a2b_a1b2_b1a2'] = value['pct_chimeric_paired']
        value.pop('pct_chimeric_paired')
    elif 'pct_chimeric_paired' not in value:
        value['pct_2_alignments_a1_a2b_a1b2_b1a2'] = 22
    if 'pct_normal_paired' in value:
        value['pct_2_alignments_a_b'] = value['pct_normal_paired']
        value.pop('pct_normal_paired')
    elif 'pct_normal_paired' not in value:
        value['pct_2_alignments_a_b'] = 22
    if 'pct_sequenced_duplicates' in value:
        value['pct_sequenced_total_duplicates'] = value['pct_sequenced_duplicates']
        value.pop('pct_sequenced_duplicates')
    if 'pct_sequenced_unique_reads' in value:
        value['pct_sequenced_total_unique'] = value['pct_sequenced_unique_reads']
        value.pop('pct_sequenced_unique_reads')
    if 'pct_single_alignment' in value:
        value['pct_1_alignment'] = value['pct_single_alignment']
        value.pop('pct_single_alignment')
    if 'pct_unmapped_reads' in value:
        value['pct_one_or_both_reads_unmapped'] = value['pct_unmapped_reads']
        value.pop('pct_unmapped_reads')
    elif 'pct_unmapped_reads' not in value:
        value['pct_one_or_both_reads_unmapped'] = 22
    if 'single_alignment' in value:
        value['1_alignment'] = value['single_alignment']
        value.pop('single_alignment')
    if 'unique_reads' in value:
        value['total_unique'] = value['unique_reads']
        value.pop('unique_reads')
    if 'unmapped_reads' in value:
        value['one_or_both_reads_unmapped'] = value['unmapped_reads']
        value.pop('unmapped_reads')
    elif 'unmapped_reads' not in value:
        value['one_or_both_reads_unmapped'] = 22
    if 'read_type' not in value:
        value['read_type'] = 'paired-ended'
    if 'avg_insert_size' not in value:
        value['avg_insert_size'] = 22
    if 'below_mapq_threshold' not in value:
        value['below_mapq_threshold'] = 22
    if 'library_complexity_estimate' not in value:
        value['library_complexity_estimate'] = 22
    if 'sequenced_reads' not in value:
        value['sequenced_reads'] = 22
